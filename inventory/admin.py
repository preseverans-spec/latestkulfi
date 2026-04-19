from django.contrib import admin
from .models import Product, Inventory, Sales, SalesStockTaken, OperationsExpense, OperationsIncome, DailySalesReport, WeeklyReport, ProfitReport

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'current_stock', 'selling_price', 'is_active')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'sku')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'sku', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Stock', {
            'fields': ('current_stock', 'reorder_level')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at', 'product')
    search_fields = ('product__name', 'reference_document')
    readonly_fields = ('created_at', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit_price', 'total_price', 'sale_date', 'recorded_by')
    list_filter = ('sale_date', 'product', 'recorded_by')
    search_fields = ('product__name',)
    readonly_fields = ('total_price', 'created_at')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SalesStockTaken)
class SalesStockTakenAdmin(admin.ModelAdmin):
    list_display = ('salesperson', 'sales_date', 'product_name', 'stock_taken_count', 'estimated_total')
    list_filter = ('sales_date', 'salesperson')
    search_fields = ('product_name', 'product_key', 'salesperson__username')
    readonly_fields = ('estimated_total', 'created_at', 'updated_at')


@admin.register(OperationsExpense)
class OperationsExpenseAdmin(admin.ModelAdmin):
    list_display = ('operation_date', 'details', 'amount', 'created_by', 'created_at')
    list_filter = ('operation_date', 'created_at', 'created_by')
    search_fields = ('details',)
    readonly_fields = ('created_at',)


@admin.register(OperationsIncome)
class OperationsIncomeAdmin(admin.ModelAdmin):
    list_display = ('income_date', 'details', 'amount', 'created_by', 'created_at')
    list_filter = ('income_date', 'created_at', 'created_by')
    search_fields = ('details',)
    readonly_fields = ('created_at',)

@admin.register(DailySalesReport)
class DailySalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'total_sales', 'total_revenue', 'total_profit')
    list_filter = ('report_date',)
    readonly_fields = ('total_revenue', 'total_cost', 'total_profit', 'created_at', 'updated_at')

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'total_sales', 'total_revenue', 'total_profit')
    list_filter = ('start_date',)
    readonly_fields = ('total_revenue', 'total_cost', 'total_profit', 'created_at', 'updated_at')

@admin.register(ProfitReport)
class ProfitReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'product', 'total_profit', 'profit_margin')
    list_filter = ('report_date', 'product')
    readonly_fields = ('profit_margin', 'created_at', 'updated_at')
