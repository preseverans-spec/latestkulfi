from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from inventory.models import Inventory, OperationsExpense, Product, Sales


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'role')

    def get_role(self, obj):
        return 'admin' if obj.is_staff else 'sales'


class ProductSerializer(serializers.ModelSerializer):
    profit_per_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'sku',
            'category',
            'cost_price',
            'selling_price',
            'current_stock',
            'reorder_level',
            'description',
            'is_active',
            'created_at',
            'updated_at',
            'profit_per_unit',
        )
        read_only_fields = ('created_at', 'updated_at', 'profit_per_unit')

    def get_profit_per_unit(self, obj):
        return obj.get_profit_per_unit()


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Inventory
        fields = (
            'id',
            'product',
            'product_name',
            'movement_type',
            'quantity',
            'unit_cost',
            'reference_document',
            'notes',
            'movement_date',
            'client_txn_id',
            'client_updated_at',
            'server_version',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'server_version', 'product_name', 'created_by_name')

    def create(self, validated_data):
        request = self.context['request']
        client_txn_id = validated_data.get('client_txn_id')
        if client_txn_id:
            existing = Inventory.objects.filter(created_by=request.user, client_txn_id=client_txn_id).first()
            if existing:
                return existing

        validated_data['created_by'] = request.user
        inventory = super().create(validated_data)

        product = inventory.product
        if inventory.movement_type == 'IN':
            product.current_stock += inventory.quantity
        elif inventory.movement_type == 'OUT':
            product.current_stock -= inventory.quantity
        elif inventory.movement_type == 'ADJUSTMENT':
            product.current_stock = inventory.quantity

        product.save(update_fields=['current_stock', 'updated_at'])
        return inventory


class SalesSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)

    class Meta:
        model = Sales
        fields = (
            'id',
            'product',
            'product_name',
            'quantity',
            'unit_price',
            'total_price',
            'sale_date',
            'sale_time',
            'client_txn_id',
            'client_updated_at',
            'server_version',
            'recorded_by',
            'recorded_by_name',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'total_price',
            'sale_time',
            'recorded_by',
            'created_at',
            'updated_at',
            'server_version',
            'product_name',
            'recorded_by_name',
        )

    def validate(self, attrs):
        product = attrs.get('product') or getattr(self.instance, 'product', None)
        quantity = attrs.get('quantity', getattr(self.instance, 'quantity', 0))

        if product and quantity and quantity <= 0:
            raise serializers.ValidationError({'quantity': 'Quantity must be greater than zero.'})

        if product and quantity:
            available = product.current_stock
            if self.instance and self.instance.product_id == product.id:
                available += self.instance.quantity
            if available < quantity:
                raise serializers.ValidationError({'quantity': 'Insufficient stock for this sale.'})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        client_txn_id = validated_data.get('client_txn_id')
        if client_txn_id:
            existing = Sales.objects.filter(recorded_by=request.user, client_txn_id=client_txn_id).first()
            if existing:
                return existing

        validated_data['recorded_by'] = request.user

        if 'unit_price' not in validated_data or validated_data['unit_price'] is None:
            validated_data['unit_price'] = Decimal(validated_data['product'].selling_price)

        sale = super().create(validated_data)

        product = sale.product
        product.current_stock -= sale.quantity
        product.save(update_fields=['current_stock', 'updated_at'])

        return sale


class OperationsExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = OperationsExpense
        fields = (
            'id',
            'operation_date',
            'details',
            'amount',
            'client_txn_id',
            'client_updated_at',
            'server_version',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_by', 'created_by_name', 'created_at', 'updated_at', 'server_version')

    def create(self, validated_data):
        request = self.context['request']
        client_txn_id = validated_data.get('client_txn_id')
        if client_txn_id:
            existing = OperationsExpense.objects.filter(created_by=request.user, client_txn_id=client_txn_id).first()
            if existing:
                return existing

        validated_data['created_by'] = request.user
        return super().create(validated_data)
