from datetime import timedelta
from decimal import Decimal
import re

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from inventory.models import Inventory, OperationsExpense, OperationsIncome, Product, Sales, SalesStockTaken


class SyncApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.sales_user = User.objects.create_user(
			username='sales1',
			password='pass12345',
			is_staff=False,
		)
		self.other_user = User.objects.create_user(
			username='sales2',
			password='pass12345',
			is_staff=False,
		)
		self.admin_user = User.objects.create_user(
			username='admin1',
			password='pass12345',
			is_staff=True,
		)
		self.product = Product.objects.create(
			name='Kesar Kulfi',
			sku='IK-001',
			category='Kulfi',
			cost_price='12.00',
			selling_price='20.00',
			current_stock=50,
			reorder_level=5,
			is_active=True,
		)

	def authenticate(self, user):
		self.client.force_authenticate(user=user)

	def test_sync_push_create_sales_idempotent(self):
		self.authenticate(self.sales_user)
		payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'sale-create-1',
					'payload': {
						'product': self.product.id,
						'quantity': 2,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
						'notes': 'mobile sale',
					},
				}
			]
		}

		first = self.client.post('/api/v1/sync/push/', payload, format='json')
		second = self.client.post('/api/v1/sync/push/', payload, format='json')

		self.assertEqual(first.status_code, 200)
		self.assertEqual(second.status_code, 200)
		self.assertEqual(Sales.objects.count(), 1)

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 48)

		accepted_1 = first.data['data']['accepted'][0]
		accepted_2 = second.data['data']['accepted'][0]
		self.assertEqual(accepted_1['status'], 'created')
		self.assertEqual(accepted_2['status'], 'duplicate')

	def test_sync_push_rejects_inventory_create_for_non_staff(self):
		self.authenticate(self.sales_user)
		payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'inv-create-1',
					'payload': {
						'product': self.product.id,
						'movement_type': 'IN',
						'quantity': 5,
						'unit_cost': '10.00',
						'movement_date': '2026-04-15',
					},
				}
			]
		}

		response = self.client.post('/api/v1/sync/push/', payload, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Inventory.objects.count(), 0)
		rejected = response.data['data']['rejected'][0]
		self.assertEqual(rejected['reason'], 'permission_denied')

	def test_sync_push_update_conflict_on_stale_version(self):
		self.authenticate(self.sales_user)
		create_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'sale-create-2',
					'payload': {
						'product': self.product.id,
						'quantity': 3,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				}
			]
		}
		self.client.post('/api/v1/sync/push/', create_payload, format='json')
		sale = Sales.objects.get(client_txn_id='sale-create-2')

		sale.notes = 'edited elsewhere'
		sale.save()

		stale_update_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'update',
					'client_txn_id': 'sale-update-stale-1',
					'payload': {
						'id': sale.id,
						'server_version': 1,
						'quantity': 2,
					},
				}
			]
		}

		response = self.client.post('/api/v1/sync/push/', stale_update_payload, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['data']['conflicts']), 1)
		self.assertEqual(response.data['data']['conflicts'][0]['reason'], 'stale_server_version')

	def test_sync_push_delete_returns_tombstone_in_pull(self):
		self.authenticate(self.sales_user)
		create_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'sale-create-3',
					'payload': {
						'product': self.product.id,
						'quantity': 4,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				}
			]
		}
		self.client.post('/api/v1/sync/push/', create_payload, format='json')
		sale = Sales.objects.get(client_txn_id='sale-create-3')

		delete_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'delete',
					'client_txn_id': 'sale-delete-1',
					'payload': {
						'id': sale.id,
						'server_version': sale.server_version,
					},
				}
			]
		}

		delete_response = self.client.post('/api/v1/sync/push/', delete_payload, format='json')
		self.assertEqual(delete_response.status_code, 200)
		self.assertFalse(Sales.objects.filter(id=sale.id).exists())

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 50)

		last_sync_at = (timezone.now() - timedelta(minutes=5)).isoformat()
		pull_response = self.client.get(f'/api/v1/sync/pull/?last_sync_at={last_sync_at}')
		self.assertEqual(pull_response.status_code, 200)

		deleted_events = pull_response.data['data']['deleted_events']
		self.assertTrue(any(item['entity'] == 'sales' and item['object_id'] == sale.id for item in deleted_events))

	def test_sync_pull_scopes_non_staff_expenses(self):
		OperationsExpense.objects.create(
			operation_date='2026-04-15',
			details='Fuel A',
			amount='100.00',
			created_by=self.sales_user,
		)
		OperationsExpense.objects.create(
			operation_date='2026-04-15',
			details='Fuel B',
			amount='120.00',
			created_by=self.other_user,
		)

		self.authenticate(self.sales_user)
		response = self.client.get('/api/v1/sync/pull/')
		self.assertEqual(response.status_code, 200)

		expenses = response.data['data']['changes']['expenses']
		self.assertEqual(len(expenses), 1)
		self.assertEqual(expenses[0]['details'], 'Fuel A')
		self.assertEqual(response.data['data']['changes']['inventory_movements'], [])

	def test_sync_ack_validates_payload_shape(self):
		self.authenticate(self.sales_user)
		bad_response = self.client.post('/api/v1/sync/ack/', {'acknowledged': 'bad'}, format='json')
		ok_response = self.client.post('/api/v1/sync/ack/', {'acknowledged': [{'entity': 'sales', 'object_id': 1}]}, format='json')

		self.assertEqual(bad_response.status_code, 400)
		self.assertEqual(ok_response.status_code, 200)
		self.assertEqual(ok_response.data['data']['received'], 1)

	def test_sales_stock_taken_admin_summary_uses_fixed_product_order(self):
		client = Client()
		client.force_login(self.admin_user)
		sales_date = timezone.datetime(2026, 4, 15).date()

		SalesStockTaken.objects.create(
			salesperson=self.sales_user,
			sales_date=sales_date,
			product_key='guava',
			product_name='Guava',
			avg_unit_price=Decimal('28.00'),
			combined_stock=10,
			stock_taken_count=1,
		)
		SalesStockTaken.objects.create(
			salesperson=self.sales_user,
			sales_date=sales_date,
			product_key='coconut',
			product_name='Coconut',
			avg_unit_price=Decimal('26.00'),
			combined_stock=10,
			stock_taken_count=1,
		)
		SalesStockTaken.objects.create(
			salesperson=self.sales_user,
			sales_date=sales_date,
			product_key='elaichi',
			product_name='Elaichi',
			avg_unit_price=Decimal('26.00'),
			combined_stock=10,
			stock_taken_count=1,
		)

		response = client.get(reverse('sales_stock_taken_entry'), {'sales_date': sales_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			[entry.display_product_name for entry in response.context['admin_day_entries']],
			['COCONUT', 'ELAICHI', 'GUAVA'],
		)

	def test_sales_stock_taken_product_list_uses_requested_labels_and_order(self):
		client = Client()
		client.force_login(self.admin_user)
		sales_date = timezone.datetime(2026, 4, 16).date()
		self.product.is_active = False
		self.product.save(update_fields=['is_active'])
		expected_names = [
			'MALAI',
			'PISTA BADAM',
			'CHOCOLATE',
			'KESAR BADAM',
			'KESAR PISTA',
			'STRAWBERRY',
			'DRY FRUIT',
			'BLACK CURRANT',
			'LITCHI',
			'CARAMEL COFFEE',
			'ROSE',
			'MANGO MALAI',
			'BUTTERSCOTCH',
			'COCONUT',
			'ELAICHI',
			'GUAVA',
			'PAAN',
			'KESAR KAJOOR',
		]
		products = [
			('Malai', 'IK-101'),
			('Pista Badam', 'IK-102'),
			('Chocolate', 'IK-103'),
			('Kesar Badam', 'IK-104'),
			('Kesar Pista', 'IK-105'),
			('Strawberry', 'IK-106'),
			('Dry Fruit', 'IK-107'),
			('Blackcurrant', 'IK-108'),
			('Litchi', 'IK-109'),
			('Caramel Coffee', 'IK-110'),
			('Rose', 'IK-111'),
			('Mango Malai', 'IK-112'),
			('Butterscotch', 'IK-113'),
			('Coconut', 'IK-114'),
			('Elaichi', 'IK-115'),
			('Guava', 'IK-116'),
			('Paan', 'IK-117'),
			('Kesar Kajoor', 'IK-118'),
		]

		for name, sku in products:
			Product.objects.create(
				name=name,
				sku=sku,
				category='Kulfi',
				cost_price='12.00',
				selling_price='20.00',
				current_stock=10,
				reorder_level=2,
				is_active=True,
			)

		response = client.get(reverse('sales_stock_taken_entry'), {'sales_date': sales_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertEqual([product['name'] for product in response.context['products']], expected_names)

	def test_sales_stock_taken_treats_elachi_as_elaichi(self):
		client = Client()
		client.force_login(self.admin_user)
		sales_date = timezone.datetime(2026, 4, 17).date()
		self.product.is_active = False
		self.product.save(update_fields=['is_active'])

		for name, sku in [
			('Coconut', 'IK-201'),
			('Elachi', 'IK-202'),
			('Guava', 'IK-203'),
			('Kesar Kajoor', 'IK-204'),
		]:
			Product.objects.create(
				name=name,
				sku=sku,
				category='Kulfi',
				cost_price='12.00',
				selling_price='20.00',
				current_stock=10,
				reorder_level=2,
				is_active=True,
			)

		response = client.get(reverse('sales_stock_taken_entry'), {'sales_date': sales_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			[product['name'] for product in response.context['products']],
			['COCONUT', 'ELAICHI', 'GUAVA', 'KESAR KAJOOR'],
		)

	def test_quick_sales_entry_treats_elachi_as_elaichi_for_combined_stock(self):
		client = Client()
		client.force_login(self.admin_user)
		sales_date = timezone.datetime(2026, 4, 18).date()
		self.product.is_active = False
		self.product.save(update_fields=['is_active'])

		products = {}
		for name, sku, quantity in [
			('Coconut', 'IK-301', 20),
			('Elachi', 'IK-302', 29),
			('Guava', 'IK-303', 13),
		]:
			product = Product.objects.create(
				name=name,
				sku=sku,
				category='Kulfi',
				cost_price=Decimal('12.00'),
				selling_price=Decimal('20.00'),
				current_stock=quantity,
				reorder_level=2,
				is_active=True,
			)
			products[name] = product
			Inventory.objects.create(
				product=product,
				movement_type='IN',
				quantity=quantity,
				unit_cost=Decimal('12.00'),
				movement_date=sales_date,
				reference_document='test',
				created_by=self.admin_user,
			)

		response = client.get(reverse('quick_sales_entry'), {'sales_date': sales_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		product_rows = response.context['products']
		self.assertEqual(response.context['total_combined_stock'], 62)
		self.assertEqual(
			[(product['name'], product['stock']) for product in product_rows],
			[('COCONUT', 20), ('ELAICHI', 29), ('GUAVA', 13)],
		)

	def test_inventory_list_keeps_historical_zero_stock_in_rows(self):
		client = Client()
		client.force_login(self.admin_user)
		self.product.is_active = False
		self.product.save(update_fields=['is_active'])
		selected_date = timezone.datetime(2026, 4, 25).date()
		history_product = Product.objects.create(
			name='Historic Zero Test',
			sku='IK-401',
			category='Kulfi',
			cost_price=Decimal('12.00'),
			selling_price=Decimal('20.00'),
			current_stock=10,
			reorder_level=2,
			is_active=True,
		)
		Inventory.objects.create(
			product=history_product,
			movement_type='IN',
			quantity=10,
			unit_cost=Decimal('12.00'),
			movement_date=timezone.datetime(2026, 5, 2).date(),
			reference_document='test',
			created_by=self.admin_user,
		)

		response = client.get(reverse('inventory_list'), {'as_of_date': selected_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['total_stock'], 0)
		content = response.content.decode()
		self.assertRegex(
			content,
			re.compile(r'Historic Zero Test</strong></td>\s*<td>IK-401</td>\s*<td>Indian Kulfi</td>\s*<td>0</td>', re.S),
		)

	def test_view_sales_sort_treats_elachi_as_elaichi(self):
		from inventory.views import get_report_product_sort_key

		names = ['Guava', 'Elachi', 'Coconut']
		sorted_names = sorted(names, key=lambda name: get_report_product_sort_key(name))

		self.assertEqual(sorted_names, ['Coconut', 'Elachi', 'Guava'])

	def test_view_sales_previous_next_day_links_use_adjacent_dates(self):
		client = Client()
		client.force_login(self.admin_user)
		selected_date = timezone.datetime(2026, 4, 25).date()

		response = client.get(reverse('view_sales'), {'date': selected_date.isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '?date=2026-04-24')
		self.assertContains(response, '?date=2026-04-26')

	def test_admin_inventory_update_adjusts_stock_correctly(self):
		self.authenticate(self.admin_user)
		create_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'inv-create-admin-1',
					'payload': {
						'product': self.product.id,
						'movement_type': 'IN',
						'quantity': 5,
						'unit_cost': '11.00',
						'movement_date': '2026-04-15',
					},
				}
			]
		}

		create_response = self.client.post('/api/v1/sync/push/', create_payload, format='json')
		self.assertEqual(create_response.status_code, 200)

		inv = Inventory.objects.get(client_txn_id='inv-create-admin-1')
		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 55)

		update_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'update',
					'client_txn_id': 'inv-update-admin-1',
					'payload': {
						'id': inv.id,
						'server_version': inv.server_version,
						'movement_type': 'OUT',
						'quantity': 2,
					},
				}
			]
		}

		update_response = self.client.post('/api/v1/sync/push/', update_payload, format='json')
		self.assertEqual(update_response.status_code, 200)
		self.assertEqual(update_response.data['data']['accepted'][0]['status'], 'updated')

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 48)

	def test_admin_inventory_delete_reverts_stock(self):
		self.authenticate(self.admin_user)
		create_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'inv-create-admin-2',
					'payload': {
						'product': self.product.id,
						'movement_type': 'IN',
						'quantity': 7,
						'unit_cost': '11.00',
						'movement_date': '2026-04-15',
					},
				}
			]
		}

		self.client.post('/api/v1/sync/push/', create_payload, format='json')
		inv = Inventory.objects.get(client_txn_id='inv-create-admin-2')

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 57)

		delete_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'delete',
					'client_txn_id': 'inv-delete-admin-1',
					'payload': {
						'id': inv.id,
						'server_version': inv.server_version,
					},
				}
			]
		}

		delete_response = self.client.post('/api/v1/sync/push/', delete_payload, format='json')
		self.assertEqual(delete_response.status_code, 200)
		self.assertEqual(delete_response.data['data']['accepted'][0]['status'], 'deleted')
		self.assertFalse(Inventory.objects.filter(id=inv.id).exists())

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 50)

	def test_inventory_adjustment_update_conflict(self):
		self.authenticate(self.admin_user)
		create_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'inv-adjust-create-1',
					'payload': {
						'product': self.product.id,
						'movement_type': 'ADJUSTMENT',
						'quantity': 42,
						'unit_cost': '11.00',
						'movement_date': '2026-04-15',
					},
				}
			]
		}

		self.client.post('/api/v1/sync/push/', create_payload, format='json')
		inv = Inventory.objects.get(client_txn_id='inv-adjust-create-1')

		update_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'update',
					'client_txn_id': 'inv-adjust-update-1',
					'payload': {
						'id': inv.id,
						'server_version': inv.server_version,
						'quantity': 40,
					},
				}
			]
		}

		response = self.client.post('/api/v1/sync/push/', update_payload, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['data']['conflicts'][0]['reason'], 'business_rule_conflict')

	def test_inventory_adjustment_delete_conflict(self):
		self.authenticate(self.admin_user)
		create_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'inv-adjust-create-2',
					'payload': {
						'product': self.product.id,
						'movement_type': 'ADJUSTMENT',
						'quantity': 38,
						'unit_cost': '11.00',
						'movement_date': '2026-04-15',
					},
				}
			]
		}

		self.client.post('/api/v1/sync/push/', create_payload, format='json')
		inv = Inventory.objects.get(client_txn_id='inv-adjust-create-2')

		delete_payload = {
			'records': [
				{
					'entity': 'inventory_movements',
					'operation': 'delete',
					'client_txn_id': 'inv-adjust-delete-1',
					'payload': {
						'id': inv.id,
						'server_version': inv.server_version,
					},
				}
			]
		}

		response = self.client.post('/api/v1/sync/push/', delete_payload, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['data']['conflicts'][0]['reason'], 'business_rule_conflict')

	def test_sync_push_batch_mixed_outcomes(self):
		self.authenticate(self.sales_user)

		# Seed one sale and bump version so the batch update below is stale.
		seed_create_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'batch-seed-sale-1',
					'payload': {
						'product': self.product.id,
						'quantity': 1,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				}
			]
		}
		self.client.post('/api/v1/sync/push/', seed_create_payload, format='json')
		seed_sale = Sales.objects.get(client_txn_id='batch-seed-sale-1')
		seed_sale.notes = 'version bump'
		seed_sale.save()

		batch_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'batch-create-sale-1',
					'payload': {
						'product': self.product.id,
						'quantity': 2,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				},
				{
					'entity': 'inventory_movements',
					'operation': 'create',
					'client_txn_id': 'batch-reject-inv-1',
					'payload': {
						'product': self.product.id,
						'movement_type': 'IN',
						'quantity': 3,
						'unit_cost': '10.00',
						'movement_date': '2026-04-15',
					},
				},
				{
					'entity': 'sales',
					'operation': 'update',
					'client_txn_id': 'batch-conflict-sale-1',
					'payload': {
						'id': seed_sale.id,
						'server_version': 1,
						'quantity': 5,
					},
				},
			]
		}

		response = self.client.post('/api/v1/sync/push/', batch_payload, format='json')
		self.assertEqual(response.status_code, 200)

		self.assertEqual(len(response.data['data']['accepted']), 1)
		self.assertEqual(len(response.data['data']['rejected']), 1)
		self.assertEqual(len(response.data['data']['conflicts']), 1)
		self.assertEqual(response.data['data']['accepted'][0]['status'], 'created')
		self.assertEqual(response.data['data']['rejected'][0]['reason'], 'permission_denied')
		self.assertEqual(response.data['data']['conflicts'][0]['reason'], 'stale_server_version')

	def test_sync_push_batch_duplicate_in_same_request(self):
		self.authenticate(self.sales_user)
		batch_payload = {
			'records': [
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'batch-dup-sale-1',
					'payload': {
						'product': self.product.id,
						'quantity': 2,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				},
				{
					'entity': 'sales',
					'operation': 'create',
					'client_txn_id': 'batch-dup-sale-1',
					'payload': {
						'product': self.product.id,
						'quantity': 2,
						'unit_price': '20.00',
						'sale_date': '2026-04-15',
					},
				},
			]
		}

		response = self.client.post('/api/v1/sync/push/', batch_payload, format='json')
		self.assertEqual(response.status_code, 200)

		accepted = response.data['data']['accepted']
		self.assertEqual(len(accepted), 2)
		self.assertEqual(accepted[0]['status'], 'created')
		self.assertEqual(accepted[1]['status'], 'duplicate')
		self.assertEqual(Sales.objects.filter(client_txn_id='batch-dup-sale-1').count(), 1)


class ViewSalesDeleteTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.admin_user = User.objects.create_user(
			username='admin-delete',
			password='pass12345',
			is_staff=True,
		)
		self.product = Product.objects.create(
			name='Malai Kulfi',
			sku='IK-900',
			category='Kulfi',
			cost_price='10.00',
			selling_price='20.00',
			current_stock=5,
			reorder_level=5,
			is_active=True,
		)

	def test_view_sales_shows_delete_all_button_for_admin(self):
		Sales.objects.create(
			product=self.product,
			quantity=2,
			unit_price=Decimal('20.00'),
			sale_date='2026-04-15',
			recorded_by=self.admin_user,
		)

		self.client.force_login(self.admin_user)
		response = self.client.get(reverse('view_sales'), {'date': '2026-04-15'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('delete_sales_for_date'))

	def test_delete_sales_for_date_recalculates_stock_after_later_adjustment(self):
		Sales.objects.create(
			product=self.product,
			quantity=2,
			unit_price=Decimal('20.00'),
			sale_date='2026-04-15',
			recorded_by=self.admin_user,
		)
		Sales.objects.create(
			product=self.product,
			quantity=1,
			unit_price=Decimal('20.00'),
			sale_date='2026-04-15',
			recorded_by=self.admin_user,
		)
		Inventory.objects.create(
			product=self.product,
			movement_type='ADJUSTMENT',
			quantity=5,
			unit_cost='10.00',
			movement_date='2026-04-16',
			created_by=self.admin_user,
		)

		self.client.force_login(self.admin_user)
		response = self.client.post(
			reverse('delete_sales_for_date'),
			{
				'selected_date': '2026-04-15',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, f"{reverse('view_sales')}?date=2026-04-15")
		self.assertFalse(Sales.objects.filter(sale_date='2026-04-15').exists())

		self.product.refresh_from_db()
		self.assertEqual(self.product.current_stock, 5)


class QuickIncomeEntryTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.admin_user = User.objects.create_user(
			username='admin-income',
			password='pass12345',
			is_staff=True,
		)

	def test_quick_income_entry_creates_income_record(self):
		self.client.force_login(self.admin_user)
		response = self.client.post(
			reverse('quick_income_entry'),
			{
				'income_date': '2026-04-19',
				'details': 'Bank transfer from catering',
				'amount': '1500.00',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, f"{reverse('quick_income_entry')}?date=2026-04-19")
		self.assertTrue(OperationsIncome.objects.filter(details='Bank transfer from catering').exists())
