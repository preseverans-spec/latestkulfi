from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from inventory.models import Inventory, OperationsExpense, OperationsIncome, Product, Sales


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
