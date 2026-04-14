# Indian Kulfi App - Complete User Manual

## 1. Introduction

The Indian Kulfi App is a Django-based operations system for:
- Product management
- Inventory movement tracking
- Daily sales entry and review
- Operations expense tracking
- Profit and stock reporting
- User access control

The app is designed for day-to-day store operations with date-based data entry and printable/exportable reports.

---

## 2. User Roles and Access Control

### 2.1 Admin Users
Admin users (staff users) can access all modules:
- Dashboard
- Products
- Inventory Management
- Kulfi Sales
- Kulfi Operations
- Reports
- User Management

### 2.2 Sales Users (Non-Admin)
Sales users can access only the Sales module:
- Quick Sales Entry
- View Sales
- Sales History

Other modules are hidden in the sidebar and blocked at URL level.

### 2.3 Login Redirect Behavior
- Admin login redirects to Dashboard.
- Non-admin login redirects to Quick Sales Entry.

---

## 3. Navigation Overview

### 3.1 Main Sidebar (Admin)
- Dashboard
- Products
  - View All Products
  - Add New Product
  - Trash
- Inventory Management
  - Quick Entry
  - View Stock
  - Stock History
- Kulfi Sales
  - Quick Sales Entry
  - View Sales
  - Sales History
- Kulfi Operations
  - Quick Operations Entry
  - View Expenses
- Reports
  - Daily Report
  - Weekly Report
  - Profit Report
  - Stock Report

### 3.2 Main Sidebar (Sales User)
- Kulfi Sales only
  - Quick Sales Entry
  - View Sales
  - Sales History

---

## 4. Module-by-Module Usage

## 4.1 Authentication

### Login
1. Open app URL.
2. Enter username and password.
3. Click login.

### Logout
1. Click Logout from the top bar.

---

## 4.2 Dashboard (Admin)

Shows today-level snapshots such as:
- Total stock
- Total sales count for today
- Revenue for today
- Profit for today
- Operation cost for today
- Net profit for today (after operations)
- Low stock alerts

Use this page for a quick health check at start and end of day.

---

## 4.3 Products (Admin)

### Add New Product
1. Go to Products -> Add New Product.
2. Enter product details:
   - Name
   - SKU
   - Category
   - Cost price
   - Selling price
   - Reorder level
3. Save.

### View and Edit Products
1. Go to Products -> View All Products.
2. Use edit action to modify product details.

### Delete and Restore
- Soft delete moves product to Trash.
- Restore from Trash if needed.
- Permanent delete is available from Trash.

---

## 4.4 Inventory Management (Admin)

### Quick Entry
Use for fast stock updates with multiple rows.

Each row supports:
- Product
- Movement type: IN, OUT, ADJUSTMENT
- Quantity
- Quantity unit: NOS or PACK
- Cost price
- Movement date

Important behavior:
- PACK is converted to units (1 pack = 6 units).
- Manufacturer-specific pricing support exists in quick inventory flow.
- Backdated entries are supported via movement date.

### View Stock
Use filters and sorting to review live inventory state.

### Stock History
Review inventory movement history by date.

---

## 4.5 Kulfi Sales

## Quick Sales Entry (Admin + Sales)
Use this for daily and backdated sales recording.

General flow:
1. Open Kulfi Sales -> Quick Sales Entry.
2. Choose date.
3. Enter product lines and quantity.
4. Submit.

Notes:
- System validates stock and shows warnings for failed rows.
- Multiple product rows can be submitted together.
- Stock is reduced automatically when sale is saved.

## View Sales by Date (Admin + Sales)
This screen supports filtering and reporting.

Filters available:
- Date
- Sales person (user who recorded the sale)

How to use salesperson filter:
1. Select date.
2. Select Sales Person (or keep All Sales Persons).
3. Click View Sales.

What you get:
- Filtered sales table
- Totals (count, revenue, quantity)
- Print and export actions

Print/Export:
- Print HTML
- Download PDF
- Download Excel

The salesperson filter is carried into print/export output.

## Sales History (Admin + Sales)
Use date range and search-style review for past sales records.

### Edit/Delete Sales
- Admin only.
- Non-admin users cannot edit or delete sales records.

---

## 4.6 Kulfi Operations (Admin)

## Quick Operations Entry
Use this for daily operating expenses.

Fields:
- Date
- Details of Operation
- Amount

Daily summary includes:
- Sales amount for selected date
- Operation cost for selected date
- Net after operations

### Edit/Delete in Daily Operations Sheet
Actions are available in each row:
- Edit icon: loads row into form for update
- Delete icon: removes row after confirmation

## View Expenses
Use this to review expense entries with date-range filtering.

Filters:
- Start date
- End date

Output:
- Matching operations entries
- Total operation cost for selected range

---

## 4.7 Reports (Admin)

## Reports Dashboard
Central entry point for report modules.

## Daily Report
Shows selected day metrics such as:
- Transactions
- Revenue
- Cost
- Profit
- Operations cost
- Net profit

Print/export options are available.

## Weekly Report
Shows week-range performance with aggregates and export options.

## Profit Report
Shows profitability analysis by date range and product insights.

## Stock Report
Tracks stock-in entries for Indian Kulfi and Kulfi Corner.

Modes:
- General report
- Detailed report

Summary includes:
- Total entries
- Total quantity in
- Indian Kulfi quantity
- Kulfi Corner quantity
- Total purchase cost

Exports:
- Print HTML
- PDF
- Excel

---

## 4.8 User Management (Admin)

Available actions:
- View users
- Add user
- Edit user
- Delete user

Use this section to maintain admin and sales users.

Recommended policy:
- Keep minimum number of admin accounts.
- Use non-admin accounts for day-to-day sales entry.

---

## 5. Daily Operating SOP

### Morning
1. Admin checks Dashboard.
2. Admin records opening stock changes if needed in Inventory Quick Entry.

### During Day
1. Sales user records sales in Quick Sales Entry.
2. Admin records operation expenses in Quick Operations Entry.

### End of Day
1. Open View Sales and filter by date (and optionally salesperson).
2. Verify sales totals.
3. Open Daily Report and confirm net profit.
4. Export daily report (PDF/Excel) for record keeping.

---

## 6. Common Tasks

### Task: See sales by one salesperson
1. Go to View Sales.
2. Select date.
3. Select Sales Person.
4. Click View Sales.

### Task: Correct an operations expense entry
1. Go to Quick Operations Entry.
2. Pick date.
3. Click edit icon on entry row.
4. Update values and save.

### Task: Delete wrong operations entry
1. Go to Quick Operations Entry.
2. Click delete icon in row.
3. Confirm deletion.

### Task: Print stock report with totals
1. Go to Stock Report.
2. Select date range and mode.
3. Click Print and choose HTML/PDF/Excel.

---

## 7. Troubleshooting Guide

### 7.1 Error: no such table
Typical message example:
- no such table: inventory_operationsexpense

Cause:
- Pending migrations not applied.

Fix:
1. Activate virtual environment.
2. Run migrations:
   - python manage.py migrate
3. Reopen the page.

### 7.2 Sales row not saved
Possible reasons:
- Quantity invalid
- Quantity more than stock
- Product mismatch

Fix:
- Check warning messages displayed after submit.
- Correct rows and resubmit.

### 7.3 Non-admin cannot open module
This is expected behavior.
- Non-admin users are restricted to Sales module only.

### 7.4 Print output not matching on-screen filter
Ensure the filter is set before clicking print/export.
- View Sales print links now carry date and salesperson filter.

---

## 8. Data Backup and Recovery

### SQLite Backup
Create periodic backups of database file:
- db.sqlite3

Recommended:
- End-of-day copy
- Weekly archive copy with date-stamped filename

### Media/Logo Backup
Also back up the media directory to preserve uploaded branding assets.

---

## 9. Security and Best Practices

- Use unique passwords per user.
- Keep admin users limited.
- Disable or delete inactive accounts.
- Avoid sharing accounts between staff.
- Review sales and operations entries daily.

---

## 10. Quick Reference

### Core Sales Pages
- Quick Sales Entry
- View Sales
- Sales History

### Core Admin Pages
- Dashboard
- Inventory Quick Entry
- Quick Operations Entry
- View Expenses
- Daily/Weekly/Profit/Stock Reports
- User Management

---

## 11. Support Checklist for Admin

When a user reports an issue, collect:
1. Username and role (admin/non-admin)
2. Exact page and date filter used
3. Error text screenshot (if any)
4. Whether issue appears in print/export too
5. Whether migration is up-to-date

---

## 12. Version Notes (Current Behavior)

Current manual reflects these key implemented behaviors:
- Operations module with Date, Details, Amount
- Operation expenses included in daily net profit
- Quick Operations daily sheet supports edit/delete actions
- View Expenses is available with date range filter
- Role-based restrictions enforce sales-only access for non-admin users
- View Sales supports salesperson-level filtering and filtered print/export
