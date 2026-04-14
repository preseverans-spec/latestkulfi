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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Inventory Movements"
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"


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
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sale_date', '-sale_time']
        verbose_name_plural = "Sales"
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} units on {self.sale_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        self.total_price = self.quantity * self.unit_price
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


class OperationsExpense(models.Model):
    """Operational expense entries used for net profit calculations."""
    operation_date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-operation_date', '-created_at']
        verbose_name_plural = "Operations Expenses"

    def __str__(self):
        return f"{self.operation_date} - {self.details} ({self.amount})"


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
