# Product Requirements Document (PRD)
## Kulfi Inventory & Sales Management System

### 1. Executive Summary
The **Kulfi Inventory & Sales Management System** is a robust, web-based and mobile-ready platform designed specifically for an Indian Kulfi business. It enables real-time tracking of product inventory, streamlined sales processing, expense/income tracking, and detailed business intelligence reporting. The system is built with a Django backend and provides both a web administration dashboard and a secure REST API for mobile clients with offline sync capabilities.

---

### 2. Objectives and Goals
* **Inventory Control:** Prevent stockouts and track inventory movements down to the exact unit cost and date.
* **Sales Tracking:** Provide quick and accurate recording of sales data by salespeople, including daily stock allocation (stock taken).
* **Financial Oversight:** Track daily business expenses and ad-hoc income to automatically calculate net profits.
* **Business Intelligence:** Offer extensive daily, weekly, and profit-margin reporting to give business owners immediate insight into performance.
* **Mobile & Offline Support:** Ensure field workers/salespeople can operate seamlessly via mobile devices, syncing data reliably using idempotency keys.

---

### 3. User Roles & Permissions
1. **Administrator (Owner):**
   * Full access to all dashboards, reporting, and management modules.
   * Can add/edit/delete products, users, and hard-delete or restore trashed records.
   * Access to all financial metrics and historical data.
2. **Staff / Salesperson:**
   * Restricted access. 
   * Can record daily sales and their assigned "Stock Taken".
   * Cannot view high-level profit reports, administrative settings, or alter core product definitions.

---

### 4. Core Features & Requirements

#### 4.1 Product Management
* **CRUD Operations:** Create, read, update, and soft-delete/restore products. Hard deletion is reserved for admins.
* **Attributes:** Track Name, SKU, Category, Cost Price, Selling Price, Current Stock, and Low Stock Reorder Levels.
* **Low Stock Alerts:** System automatically flags items that fall below the designated reorder threshold.
* **Profit Tracking:** Real-time calculation of unit profit margins (Selling Price - Cost Price).

#### 4.2 Inventory Management
* **Movements:** Track all stock movements (`IN`, `OUT`, `ADJUSTMENT`) with precise timestamps, unit costs, and reference document numbers (e.g., Purchase Orders).
* **Stock Ordering:** Facility to draft and save "Stock Orders" tracking manufacturers, lots, and requested quantities.
* **Clear Stock:** Admins can quickly zero out stock for specific products during audits.
* **Quick Entry:** Streamlined interface for rapid inventory intake operations.

#### 4.3 Sales Management
* **Stock Allocation (Sales Stock Taken):** Salespeople can log the amount of stock they take out at the start of the day.
* **Sales Processing:** Record items sold, calculating total prices based on unit prices automatically.
* **Draft Sales (Sales Count Draft):** Persist unfinalized sales counts before final recording to prevent data loss mid-entry.
* **History & Corrections:** View all historical sales. Grouped or date-based deletions are allowed to correct mass entry errors.

#### 4.4 Operations & Finance
* **Expense Tracking:** Record daily operational expenses to accurately reflect net profit.
* **Income Tracking:** Record non-sales related income.
* **History:** Dedicated views to analyze expense and income streams.

#### 4.5 Reporting & Analytics
* **Dashboard:** High-level summary of today's sales, stock alerts, and recent movements.
* **Pre-aggregated Reports:** System automatically calculates and stores `DailySalesReport`, `WeeklyReport`, and `ProfitReport` for fast querying.
* **Export Capabilities:** Every major view and report can be exported/printed in multiple formats: **HTML, PDF, Excel, and CSV**.

#### 4.6 Mobile API & Synchronization
* **REST API:** Fully documented API using Swagger/DRF-Spectacular.
* **JWT Authentication:** Secure token-based access (access/refresh tokens) for mobile clients.
* **Offline Syncing Engine:** 
  * `SyncEvent` ledger mechanism ensures reliable client-server syncing.
  * Uses client-side idempotency keys (`client_txn_id`) and `server_version` counters to resolve conflicts and prevent duplicate transactions if the network drops.

---

### 5. Technical Architecture

* **Backend Framework:** Django 6.0.3, Django REST Framework 3.16
* **Database:** SQLite (default/development) / PostgreSQL (via `psycopg` & `dj-database-url` for production)
* **Authentication:** Django Session Auth (Web) + Simple JWT (Mobile API)
* **Frontend:** Django Templates with HTML, CSS, JavaScript (Vanilla/Bootstrap)
* **Static/Media Files:** WhiteNoise for efficient static file serving in production.
* **Export Libraries:** OpenPyXL (Excel), ReportLab (PDF)

---

### 6. Deployment Strategy
* **Hosting Platforms:** Native support built-in for Railway and Render (includes `Procfile`, `railway.json`, `render.yaml`).
* **Environment Configuration:** Uses `python-dotenv` for local `.env` and host environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`).
* **Security:** Configured for production-level HTTPS redirection, secure cookies, and HSTS when `DEBUG=False`.

---

### 7. Future Enhancements (Roadmap)
* Integration with barcode scanners for faster product lookup.
* SMS or Email notifications for low stock alerts.
* Direct integration with accounting software (e.g., QuickBooks, Tally).
* Supplier management and automated purchase order generation.
