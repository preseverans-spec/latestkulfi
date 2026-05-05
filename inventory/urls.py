
from django.urls import path
from . import views
from .views import save_stock_order

urlpatterns = [
        path('save_stock_order/', save_stock_order, name='save_stock_order'),
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.admin_only_view(views.dashboard), name='dashboard'),
    
    # Indian Kulfi Products Management
    path('products/', views.admin_only_view(views.product_list), name='product_list'),
    path('products/add/', views.admin_only_view(views.add_product), name='add_product'),
    path('products/edit/<int:product_id>/', views.admin_only_view(views.edit_product), name='edit_product'),
    path('products/delete/<int:product_id>/', views.admin_only_view(views.delete_product), name='delete_product'),
    path('products/trash/', views.admin_only_view(views.trash_list), name='inventory_trash'),
    path('products/restore/<int:product_id>/', views.admin_only_view(views.restore_product), name='restore_product'),
    path('products/hard-delete/<int:product_id>/', views.admin_only_view(views.hard_delete_product), name='hard_delete_product'),
    
    # Inventory
    path('inventory/', views.admin_only_view(views.inventory_list), name='inventory_list'),
    path('inventory/print/html/', views.admin_only_view(views.print_inventory_html), name='print_inventory_html'),
    path('inventory/print/pdf/', views.admin_only_view(views.print_inventory_pdf), name='print_inventory_pdf'),
    path('inventory/print/excel/', views.admin_only_view(views.print_inventory_excel), name='print_inventory_excel'),
    path('inventory/print/csv/', views.admin_only_view(views.print_inventory_csv), name='print_inventory_csv'),
    path('inventory/quick-entry/', views.admin_only_view(views.quick_inventory_entry), name='quick_inventory_entry'),
    path('inventory/clear-stock/<int:product_id>/', views.admin_only_view(views.clear_stock), name='clear_stock'),
    path('inventory/history/<int:product_id>/', views.admin_only_view(views.inventory_history), name='inventory_history'),
    path('inventory/date-history/', views.admin_only_view(views.inventory_date_history), name='inventory_date_history'),
    path('inventory/stock-order/', views.admin_only_view(views.stock_order), name='stock_order'),
    
    # Sales
    path('sales/stock-taken/', views.sales_stock_taken_entry, name='sales_stock_taken_entry'),
    path('sales/quick-entry/', views.quick_sales_entry, name='quick_sales_entry'),
    path('sales/view/', views.view_sales, name='view_sales'),
    path('sales/edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('sales/delete/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sales/delete-grouped/', views.delete_grouped_sale, name='delete_grouped_sale'),
    path('sales/delete-date/', views.delete_sales_for_date, name='delete_sales_for_date'),
    path('sales/history/', views.sales_history, name='sales_history'),
    path('sales/quick-entry/print/html/', views.print_daily_data_sheet_html, name='print_daily_data_sheet_html'),
    path('sales/print/html/', views.print_sales_html, name='print_sales_html'),
    path('sales/print/pdf/', views.print_sales_pdf, name='print_sales_pdf'),
    path('sales/print/jpeg/', views.print_sales_jpeg, name='print_sales_jpeg'),
    path('sales/print/excel/', views.print_sales_excel, name='print_sales_excel'),
    path('api/product-price/', views.get_product_price, name='get_product_price'),
    path('api/next-sku/', views.admin_only_view(views.get_next_sku), name='get_next_sku'),

    # Operations
    path('operations/quick-entry/', views.admin_only_view(views.quick_operations_entry), name='quick_operations_entry'),
    path('operations/quick-income-entry/', views.admin_only_view(views.quick_income_entry), name='quick_income_entry'),
    path('operations/delete/<int:expense_id>/', views.admin_only_view(views.delete_operations_expense), name='delete_operations_expense'),
    path('operations/income/delete/<int:income_id>/', views.admin_only_view(views.delete_operation_income), name='delete_operation_income'),
    path('operations/expenses-history/', views.admin_only_view(views.expenses_history), name='expenses_history'),
    path('operations/expenses-history/print/html/', views.admin_only_view(views.print_expenses_html), name='print_expenses_html'),
    path('operations/expenses-history/print/pdf/', views.admin_only_view(views.print_expenses_pdf), name='print_expenses_pdf'),
    path('operations/expenses-history/print/excel/', views.admin_only_view(views.print_expenses_excel), name='print_expenses_excel'),
    path('operations/expenses-history/print/csv/', views.admin_only_view(views.print_expenses_csv), name='print_expenses_csv'),
    
    # Reports
    path('reports/', views.admin_only_view(views.reports_dashboard), name='reports_dashboard'),
    path('reports/daily/', views.admin_only_view(views.daily_report), name='daily_report'),
    path('reports/weekly/', views.admin_only_view(views.weekly_report), name='weekly_report'),
    path('reports/profit/', views.admin_only_view(views.profit_report), name='profit_report'),
    path('reports/income-statement/', views.admin_only_view(views.income_statement), name='income_statement'),
    path('reports/stock/', views.admin_only_view(views.stock_report), name='stock_report'),
    path('reports/stock/print/html/', views.admin_only_view(views.print_stock_report_html), name='print_stock_report_html'),
    path('reports/stock/print/pdf/', views.admin_only_view(views.print_stock_report_pdf), name='print_stock_report_pdf'),
    path('reports/stock/print/excel/', views.admin_only_view(views.print_stock_report_excel), name='print_stock_report_excel'),
    path('reports/daily/print/html/', views.admin_only_view(views.print_daily_report_html), name='print_daily_report_html'),
    path('reports/daily/print/pdf/', views.admin_only_view(views.print_daily_report_pdf), name='print_daily_report_pdf'),
    path('reports/daily/print/excel/', views.admin_only_view(views.print_daily_report_excel), name='print_daily_report_excel'),
    path('reports/weekly/print/html/', views.admin_only_view(views.print_weekly_report_html), name='print_weekly_report_html'),
    path('reports/weekly/print/pdf/', views.admin_only_view(views.print_weekly_report_pdf), name='print_weekly_report_pdf'),
    path('reports/weekly/print/excel/', views.admin_only_view(views.print_weekly_report_excel), name='print_weekly_report_excel'),
    path('reports/profit/print/html/', views.admin_only_view(views.print_profit_report_html), name='print_profit_report_html'),
    path('reports/profit/print/pdf/', views.admin_only_view(views.print_profit_report_pdf), name='print_profit_report_pdf'),
    path('reports/profit/print/excel/', views.admin_only_view(views.print_profit_report_excel), name='print_profit_report_excel'),
    path('reports/income-statement/print/html/', views.admin_only_view(views.print_income_statement_html), name='print_income_statement_html'),
    path('reports/income-statement/print/pdf/', views.admin_only_view(views.print_income_statement_pdf), name='print_income_statement_pdf'),
    path('reports/income-statement/print/excel/', views.admin_only_view(views.print_income_statement_excel), name='print_income_statement_excel'),
    
    # User Management
    path('users/', views.admin_only_view(views.user_list), name='user_list'),
    path('users/add/', views.admin_only_view(views.add_user), name='add_user'),
    path('users/<int:user_id>/edit/', views.admin_only_view(views.edit_user), name='edit_user'),
    path('users/<int:user_id>/delete/', views.admin_only_view(views.delete_user), name='delete_user'),
    # Forgot Password AJAX endpoint
    path('forgot-password/', views.send_forgot_password_email, name='send_forgot_password_email'),
]
