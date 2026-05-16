
from django.db import models
from django.contrib.auth import get_user_model

class StockOrder(models.Model):
    manufacturer = models.CharField(max_length=100)
    order_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

class StockOrderItem(models.Model):
    order = models.ForeignKey(StockOrder, related_name='items', on_delete=models.CASCADE)
    kulfi_name = models.CharField(max_length=100)
    lot = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class Product(models.Model):
    """Product model for inventory management"""
    name = models.CharField(max_length=200, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100)
    
    # Pricing
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stock info
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10, help_text="Low stock alert threshold")
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.name
    
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    def get_profit_per_unit(self):
        return self.selling_price - self.cost_price

    def get_stock_trend(self, days=7):
        """Simple trend of last inventory movements for sparkline."""
        movements = self.inventory_movements.order_by('-created_at')[:days]
        values = []
        for m in movements[::-1]:
            if m.movement_type == 'IN':
                delta = m.quantity
            elif m.movement_type == 'OUT':
                delta = -m.quantity
            else:
                delta = 0
            values.append({
                'delta': delta,
                'abs': abs(delta),
            })
        return values


class Inventory(models.Model):
    """Track inventory movements (additions/updates)"""
    MOVEMENT_TYPE = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Stock Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost price per unit at the time of this movement")
    reference_document = models.CharField(max_length=100, blank=True, help_text="PO/DO/Invoice number")
    notes = models.TextField(blank=True)
    movement_date = models.DateField(default=timezone.now, help_text="The actual date of inventory movement")
    client_txn_id = models.CharField(max_length=64, blank=True, null=True, db_index=True, help_text="Client-generated idempotency key")
    client_updated_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="Client-side update timestamp")
    server_version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Inventory Movements"
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values_list('server_version', flat=True).first()
            if previous is not None:
                self.server_version = previous + 1
        super().save(*args, **kwargs)


class Sales(models.Model):
    """Individual sales transactions"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Timestamp
    sale_date = models.DateField()
    sale_time = models.TimeField(auto_now_add=True)
    
    # User info
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client_txn_id = models.CharField(max_length=64, blank=True, null=True, db_index=True, help_text="Client-generated idempotency key")
    client_updated_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="Client-side update timestamp")
    server_version = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date', '-sale_time']
        verbose_name_plural = "Sales"
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} units on {self.sale_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        self.total_price = self.quantity * self.unit_price
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values_list('server_version', flat=True).first()
            if previous is not None:
                self.server_version = previous + 1
        super().save(*args, **kwargs)
    
    def get_profit(self):
        return (self.unit_price - self.product.cost_price) * self.quantity


class SalesStockTaken(models.Model):
    """Daily stock allocation captured by sales users before recording sales."""
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_stock_taken_entries')
    sales_date = models.DateField(default=timezone.now)
    product_key = models.CharField(max_length=120)
    product_name = models.CharField(max_length=200)
    avg_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    combined_stock = models.IntegerField(default=0)
    stock_taken_count = models.IntegerField(default=0)
    estimated_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sales_date', 'product_name']
        verbose_name_plural = "Sales Stock Taken"
        unique_together = ('salesperson', 'sales_date', 'product_key')

    def __str__(self):
        return f"{self.salesperson.username} - {self.product_name} ({self.sales_date})"

    def save(self, *args, **kwargs):
        self.estimated_total = self.avg_unit_price * self.stock_taken_count
        super().save(*args, **kwargs)


# --- NEW MODEL: SalesCountDraft ---
class SalesCountDraft(models.Model):
    """Draft sales count per user/date/product, persists until sales are recorded."""
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_count_drafts')
    sales_date = models.DateField(default=timezone.now)
    product_key = models.CharField(max_length=120)
    sales_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('salesperson', 'sales_date', 'product_key')
        ordering = ['-sales_date', 'product_key']

    def __str__(self):
        return f"{self.salesperson.username} - {self.product_key} ({self.sales_date}): {self.sales_count}"


class OperationsExpense(models.Model):
    """Operational expense entries used for net profit calculations."""
    operation_date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    client_txn_id = models.CharField(max_length=64, blank=True, null=True, db_index=True, help_text="Client-generated idempotency key")
    client_updated_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="Client-side update timestamp")
    server_version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-operation_date', '-created_at']
        verbose_name_plural = "Operations Expenses"

    def __str__(self):
        return f"{self.operation_date} - {self.details} ({self.amount})"

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values_list('server_version', flat=True).first()
            if previous is not None:
                self.server_version = previous + 1
        super().save(*args, **kwargs)


class OperationsIncome(models.Model):
    """Operational income entries used when additional money comes into business."""
    income_date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-income_date', '-created_at']
        verbose_name_plural = "Operations Incomes"

    def __str__(self):
        return f"{self.income_date} - {self.details} ({self.amount})"


class SyncEvent(models.Model):
    """Server-side sync audit log and idempotency ledger for mobile clients."""

    ENTITY_CHOICES = [
        ('products', 'Products'),
        ('inventory_movements', 'Inventory Movements'),
        ('sales', 'Sales'),
        ('expenses', 'Expenses'),
    ]
    OPERATION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    STATUS_CHOICES = [
        ('processed', 'Processed'),
        ('duplicate', 'Duplicate'),
        ('conflict', 'Conflict'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=128, blank=True)
    client_txn_id = models.CharField(max_length=64, blank=True, db_index=True)
    entity = models.CharField(max_length=40, choices=ENTITY_CHOICES)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    object_id = models.BigIntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processed')
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity', 'object_id']),
            models.Index(fields=['user', 'client_txn_id']),
        ]
        verbose_name_plural = "Sync Events"

    def __str__(self):
        return f"{self.entity}:{self.operation} ({self.status})"


class DailySalesReport(models.Model):
    """Daily aggregated sales report"""
    report_date = models.DateField(unique=True)
    total_sales = models.IntegerField()  # Number of transactions
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        verbose_name_plural = "Daily Sales Reports"
    
    def __str__(self):
        return f"Daily Report - {self.report_date}"


class WeeklyReport(models.Model):
    """Weekly aggregated sales report"""
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Weekly Reports"
    
    def __str__(self):
        return f"Weekly Report - {self.start_date} to {self.end_date}"


class ProfitReport(models.Model):
    """Profit analysis report"""
    report_date = models.DateField(unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2)
    profit_margin = models.FloatField(default=0, help_text="Profit as percentage of revenue")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        verbose_name_plural = "Profit Reports"
    
    def __str__(self):
        return f"Profit Report - {self.report_date}"


class ExpenseDetailOption(models.Model):
    """Stores predefined and user-created expense detail labels for the dropdown."""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Expense Detail Option"
        verbose_name_plural = "Expense Detail Options"

    def __str__(self):
        return self.name


def stock_invoice_upload_path(instance, filename):
    """Legacy helper kept only so old migration 0019 can still import it."""
    from django.utils import timezone
    now = timezone.now()
    return f'stock_invoices/{now.year}/{now.month:02d}/{filename}'
