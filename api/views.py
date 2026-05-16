from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import serializers
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from inventory.models import Inventory, OperationsExpense, Product, Sales, SyncEvent

from .permissions import IsStaffOrOwner, IsStaffUser
from .response_mixins import ResponseEnvelopeMixin
from .serializers import (
    InventorySerializer,
    OperationsExpenseSerializer,
    ProductSerializer,
    SalesSerializer,
    UserProfileSerializer,
)


class MobileTokenObtainPairView(TokenObtainPairView):
    """JWT login endpoint that returns token pair and user profile."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.filter(username=request.data.get('username')).first()
            if user:
                response.data = {
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        **response.data,
                        'user': UserProfileSerializer(user).data,
                    },
                }
                return response
        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            response.data = {
                'success': False,
                'message': 'Login failed',
                'data': None,
                'errors': response.data,
            }
        return response


class MobileTokenRefreshView(TokenRefreshView):
    """JWT refresh endpoint with response envelope."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data = {
                'success': True,
                'message': 'Token refreshed successfully',
                'data': response.data,
            }
            return response

        response.data = {
            'success': False,
            'message': 'Token refresh failed',
            'data': None,
            'errors': response.data,
        }
        return response


class AuthViewSet(ResponseEnvelopeMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({'success': True, 'message': 'Profile fetched successfully', 'data': serializer.data})


class ProductViewSet(ResponseEnvelopeMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Product.objects.all().order_by('name')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(sku__icontains=search))

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_value = str(is_active).strip().lower() in ('1', 'true', 'yes', 'on')
            queryset = queryset.filter(is_active=is_active_value)

        updated_after = self.request.query_params.get('updated_after')
        if updated_after:
            parsed = parse_datetime(updated_after)
            if parsed:
                queryset = queryset.filter(updated_at__gte=parsed)

        return queryset

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsStaffUser()]
        return [IsAuthenticated()]


class InventoryViewSet(ResponseEnvelopeMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = InventorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Inventory.objects.select_related('product', 'created_by').order_by('-created_at')

        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                queryset = queryset.filter(movement_date__gte=parsed)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                queryset = queryset.filter(movement_date__lte=parsed)

        updated_after = self.request.query_params.get('updated_after')
        if updated_after:
            parsed = parse_datetime(updated_after)
            if parsed:
                queryset = queryset.filter(created_at__gte=parsed)

        return queryset

    def get_permissions(self):
        if self.action == 'create':
            return [IsStaffUser()]
        return [IsAuthenticated()]


class SalesViewSet(ResponseEnvelopeMixin, viewsets.ModelViewSet):
    serializer_class = SalesSerializer
    permission_classes = (IsAuthenticated, IsStaffOrOwner)

    def get_queryset(self):
        queryset = Sales.objects.select_related('product', 'recorded_by').order_by('-sale_date', '-sale_time')

        if not self.request.user.is_staff:
            queryset = queryset.filter(recorded_by=self.request.user)

        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                queryset = queryset.filter(sale_date__gte=parsed)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                queryset = queryset.filter(sale_date__lte=parsed)

        updated_after = self.request.query_params.get('updated_after')
        if updated_after:
            parsed = parse_datetime(updated_after)
            if parsed:
                queryset = queryset.filter(created_at__gte=parsed)

        recorded_by = self.request.query_params.get('recorded_by')
        if recorded_by and self.request.user.is_staff:
            queryset = queryset.filter(recorded_by_id=recorded_by)

        return queryset

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsStaffUser()]
        return [IsAuthenticated()]


class OperationsExpenseViewSet(ResponseEnvelopeMixin, viewsets.ModelViewSet):
    serializer_class = OperationsExpenseSerializer
    permission_classes = (IsAuthenticated, IsStaffOrOwner)

    def get_queryset(self):
        queryset = OperationsExpense.objects.select_related('created_by').order_by('-operation_date', '-created_at')

        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                queryset = queryset.filter(operation_date__gte=parsed)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                queryset = queryset.filter(operation_date__lte=parsed)

        details_search = self.request.query_params.get('details')
        if details_search:
            queryset = queryset.filter(details__icontains=details_search)

        updated_after = self.request.query_params.get('updated_after')
        if updated_after:
            parsed = parse_datetime(updated_after)
            if parsed:
                queryset = queryset.filter(created_at__gte=parsed)

        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsStaffOrOwner()]


class SyncViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def _effect(self, movement_type, quantity):
        if movement_type == 'IN':
            return quantity
        if movement_type == 'OUT':
            return -quantity
        return None

    def _create_event(self, user, device_id, client_txn_id, entity, operation, object_id, payload, event_status, message=''):
        return SyncEvent.objects.create(
            user=user,
            device_id=device_id or '',
            client_txn_id=client_txn_id or '',
            entity=entity,
            operation=operation,
            object_id=object_id,
            payload=payload or {},
            status=event_status,
            message=message,
        )

    def _entity_config(self):
        return {
            'products': {
                'queryset': Product.objects.all().order_by('id'),
                'serializer': ProductSerializer,
                'timestamp_field': 'updated_at',
            },
            'inventory_movements': {
                'queryset': Inventory.objects.select_related('product', 'created_by').all().order_by('id'),
                'serializer': InventorySerializer,
                'timestamp_field': 'updated_at',
            },
            'sales': {
                'queryset': Sales.objects.select_related('product', 'recorded_by').all().order_by('id'),
                'serializer': SalesSerializer,
                'timestamp_field': 'updated_at',
            },
            'expenses': {
                'queryset': OperationsExpense.objects.select_related('created_by').all().order_by('id'),
                'serializer': OperationsExpenseSerializer,
                'timestamp_field': 'updated_at',
            },
        }

    def _find_instance(self, entity, user, payload):
        object_id = payload.get('id') or payload.get('server_id') or payload.get('object_id')
        if not object_id:
            return None

        if entity == 'inventory_movements':
            queryset = Inventory.objects.select_related('product', 'created_by').filter(id=object_id)
            if not user.is_staff:
                queryset = queryset.none()
            return queryset.first()

        if entity == 'sales':
            queryset = Sales.objects.select_related('product', 'recorded_by').filter(id=object_id)
            if not user.is_staff:
                queryset = queryset.filter(recorded_by=user)
            return queryset.first()

        if entity == 'expenses':
            queryset = OperationsExpense.objects.select_related('created_by').filter(id=object_id)
            if not user.is_staff:
                queryset = queryset.filter(created_by=user)
            return queryset.first()

        return None

    @action(detail=False, methods=['post'])
    def push(self, request):
        records = request.data.get('records', [])
        device_id = request.data.get('device_id', '')
        if not isinstance(records, list):
            return Response(
                {
                    'success': False,
                    'message': 'Invalid payload',
                    'data': None,
                    'errors': {'records': 'records must be an array'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        accepted = []
        conflicts = []
        rejected = []

        for index, record in enumerate(records):
            entity = record.get('entity')
            operation = str(record.get('operation', '')).lower()
            payload = record.get('payload') or {}
            client_txn_id = record.get('client_txn_id') or payload.get('client_txn_id')

            if entity not in ('inventory_movements', 'sales', 'expenses'):
                rejected.append({'index': index, 'reason': 'unsupported_entity', 'entity': entity})
                continue

            if operation != 'create':
                if operation not in ('update', 'delete'):
                    rejected_item = {'index': index, 'reason': 'unsupported_operation', 'operation': operation}
                    rejected.append(rejected_item)
                    self._create_event(request.user, device_id, client_txn_id, entity, operation or 'create', None, payload, 'rejected', 'Unsupported operation')
                    continue

            if entity == 'inventory_movements' and not request.user.is_staff:
                rejected_item = {'index': index, 'reason': 'permission_denied', 'entity': entity}
                rejected.append(rejected_item)
                self._create_event(request.user, device_id, client_txn_id, entity, operation, None, payload, 'rejected', 'Permission denied')
                continue

            existing_event = None
            if client_txn_id:
                existing_event = SyncEvent.objects.filter(user=request.user, client_txn_id=client_txn_id).order_by('-created_at').first()
            if existing_event:
                accepted.append(
                    {
                        'index': index,
                        'entity': entity,
                        'server_id': existing_event.object_id,
                        'client_txn_id': client_txn_id,
                        'status': 'duplicate',
                    }
                )
                continue

            serializer_map = {
                'inventory_movements': InventorySerializer,
                'sales': SalesSerializer,
                'expenses': OperationsExpenseSerializer,
            }

            try:
                if operation == 'create':
                    serializer = serializer_map[entity](data={**payload, 'client_txn_id': client_txn_id}, context={'request': request})
                    if not serializer.is_valid():
                        conflicts.append(
                            {
                                'index': index,
                                'entity': entity,
                                'reason': 'validation_failed',
                                'errors': serializer.errors,
                            }
                        )
                        self._create_event(request.user, device_id, client_txn_id, entity, operation, None, payload, 'conflict', 'Validation failed')
                        continue

                    saved = serializer.save()
                    self._create_event(request.user, device_id, client_txn_id, entity, operation, saved.id, payload, 'processed')
                    accepted.append(
                        {
                            'index': index,
                            'entity': entity,
                            'server_id': saved.id,
                            'client_txn_id': client_txn_id,
                            'status': 'created',
                        }
                    )
                    continue

                instance = self._find_instance(entity, request.user, payload)
                if not instance:
                    conflicts.append(
                        {
                            'index': index,
                            'entity': entity,
                            'reason': 'not_found_or_forbidden',
                        }
                    )
                    self._create_event(request.user, device_id, client_txn_id, entity, operation, None, payload, 'conflict', 'Record not found')
                    continue

                client_server_version = payload.get('server_version')
                if client_server_version is None:
                    conflicts.append(
                        {
                            'index': index,
                            'entity': entity,
                            'reason': 'missing_server_version',
                        }
                    )
                    self._create_event(request.user, device_id, client_txn_id, entity, operation, instance.id, payload, 'conflict', 'Missing server_version')
                    continue

                if int(client_server_version) != int(instance.server_version):
                    conflicts.append(
                        {
                            'index': index,
                            'entity': entity,
                            'reason': 'stale_server_version',
                            'server_version': instance.server_version,
                        }
                    )
                    self._create_event(request.user, device_id, client_txn_id, entity, operation, instance.id, payload, 'conflict', 'Stale server_version')
                    continue

                if operation == 'update':
                    with transaction.atomic():
                        if entity == 'inventory_movements':
                            serializer = InventorySerializer(instance, data=payload, partial=True, context={'request': request})
                            serializer.is_valid(raise_exception=True)

                            new_product = serializer.validated_data.get('product', instance.product)
                            new_type = serializer.validated_data.get('movement_type', instance.movement_type)
                            new_qty = serializer.validated_data.get('quantity', instance.quantity)

                            old_effect = self._effect(instance.movement_type, instance.quantity)
                            new_effect = self._effect(new_type, new_qty)
                            if old_effect is None or new_effect is None:
                                raise serializers.ValidationError({'movement_type': 'ADJUSTMENT updates are not supported via sync.'})

                            old_product = instance.product
                            old_product.current_stock -= old_effect
                            old_product.save(update_fields=['current_stock', 'updated_at'])

                            if new_product.current_stock + new_effect < 0:
                                raise serializers.ValidationError({'quantity': 'Insufficient stock for this inventory update.'})

                            new_product.current_stock += new_effect
                            new_product.save(update_fields=['current_stock', 'updated_at'])

                            updated = serializer.save(client_txn_id=client_txn_id or instance.client_txn_id)

                        elif entity == 'sales':
                            serializer = SalesSerializer(instance, data=payload, partial=True, context={'request': request})
                            serializer.is_valid(raise_exception=True)

                            new_product = serializer.validated_data.get('product', instance.product)
                            new_qty = serializer.validated_data.get('quantity', instance.quantity)

                            instance.product.current_stock += instance.quantity
                            instance.product.save(update_fields=['current_stock', 'updated_at'])

                            if new_product.current_stock < new_qty:
                                raise serializers.ValidationError({'quantity': 'Insufficient stock for this sales update.'})

                            new_product.current_stock -= new_qty
                            new_product.save(update_fields=['current_stock', 'updated_at'])

                            updated = serializer.save(client_txn_id=client_txn_id or instance.client_txn_id)

                        else:
                            serializer = OperationsExpenseSerializer(instance, data=payload, partial=True, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            updated = serializer.save(client_txn_id=client_txn_id or instance.client_txn_id)

                    self._create_event(request.user, device_id, client_txn_id, entity, operation, updated.id, payload, 'processed')
                    accepted.append(
                        {
                            'index': index,
                            'entity': entity,
                            'server_id': updated.id,
                            'client_txn_id': client_txn_id,
                            'status': 'updated',
                            'server_version': updated.server_version,
                        }
                    )
                    continue

                with transaction.atomic():
                    if entity == 'inventory_movements':
                        old_effect = self._effect(instance.movement_type, instance.quantity)
                        if old_effect is None:
                            raise serializers.ValidationError({'movement_type': 'ADJUSTMENT deletes are not supported via sync.'})
                        product = instance.product
                        product.current_stock -= old_effect
                        product.save(update_fields=['current_stock', 'updated_at'])
                    elif entity == 'sales':
                        product = instance.product
                        product.current_stock += instance.quantity
                        product.save(update_fields=['current_stock', 'updated_at'])

                    deleted_id = instance.id
                    instance.delete()

                self._create_event(request.user, device_id, client_txn_id, entity, operation, deleted_id, payload, 'processed')
                accepted.append(
                    {
                        'index': index,
                        'entity': entity,
                        'server_id': deleted_id,
                        'client_txn_id': client_txn_id,
                        'status': 'deleted',
                    }
                )

            except serializers.ValidationError as exc:
                conflicts.append(
                    {
                        'index': index,
                        'entity': entity,
                        'reason': 'business_rule_conflict',
                        'errors': getattr(exc, 'detail', str(exc)),
                    }
                )
                self._create_event(request.user, device_id, client_txn_id, entity, operation, None, payload, 'conflict', 'Business rule conflict')
                continue

        return Response(
            {
                'success': True,
                'message': 'Sync push processed',
                'data': {
                    'accepted': accepted,
                    'conflicts': conflicts,
                    'rejected': rejected,
                },
            }
        )

    @action(detail=False, methods=['get'])
    def pull(self, request):
        last_sync_at = request.query_params.get('last_sync_at')
        parsed_last_sync = parse_datetime(last_sync_at) if last_sync_at else None

        entity_config = self._entity_config()
        changes = {}
        cursors = {}

        for entity_name, config in entity_config.items():
            queryset = config['queryset']

            # Keep sales and expenses scoped to non-staff owners.
            if not request.user.is_staff and entity_name == 'sales':
                queryset = queryset.filter(recorded_by=request.user)
            if not request.user.is_staff and entity_name == 'expenses':
                queryset = queryset.filter(created_by=request.user)
            if not request.user.is_staff and entity_name == 'inventory_movements':
                queryset = queryset.none()

            timestamp_field = config['timestamp_field']
            if parsed_last_sync:
                queryset = queryset.filter(**{f'{timestamp_field}__gte': parsed_last_sync})

            serializer = config['serializer'](queryset, many=True, context={'request': request})
            changes[entity_name] = serializer.data

            latest_record = queryset.order_by(f'-{timestamp_field}').first()
            cursors[entity_name] = getattr(latest_record, timestamp_field).isoformat() if latest_record else None

        delete_events_queryset = SyncEvent.objects.filter(operation='delete', status='processed')
        if parsed_last_sync:
            delete_events_queryset = delete_events_queryset.filter(created_at__gte=parsed_last_sync)

        if request.user.is_staff:
            delete_events_queryset = delete_events_queryset.filter(entity__in=('inventory_movements', 'sales', 'expenses'))
        else:
            delete_events_queryset = delete_events_queryset.filter(user=request.user, entity__in=('sales', 'expenses'))

        deleted_events = [
            {
                'entity': event.entity,
                'object_id': event.object_id,
                'client_txn_id': event.client_txn_id,
                'deleted_at': event.created_at.isoformat(),
            }
            for event in delete_events_queryset.order_by('created_at')
        ]

        return Response(
            {
                'success': True,
                'message': 'Sync pull completed',
                'data': {
                    'server_sync_time': timezone.now().isoformat(),
                    'last_sync_at': parsed_last_sync.isoformat() if parsed_last_sync else None,
                    'changes': changes,
                    'cursors': cursors,
                    'deleted_events': deleted_events,
                },
            }
        )

    @action(detail=False, methods=['post'])
    def ack(self, request):
        acknowledgements = request.data.get('acknowledged')
        if acknowledgements is None:
            acknowledgements = []

        if not isinstance(acknowledgements, list):
            return Response(
                {
                    'success': False,
                    'message': 'Invalid payload',
                    'data': None,
                    'errors': {'acknowledged': 'acknowledged must be an array'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'success': True,
                'message': 'Acknowledgement recorded',
                'data': {
                    'received': len(acknowledgements),
                    'server_time': timezone.now().isoformat(),
                },
            }
        )
