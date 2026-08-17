"""
Directly insert all 22 products into the remote PostgreSQL database using psycopg.
This bypasses Django's ORM connection switching to avoid commit issues.
"""
import psycopg
from decimal import Decimal

REMOTE_DSN = "postgresql://kulfi_user:Sv3kaNqPJg4Oqco59sW7hilF5WclUm5c@dpg-d81nc48g4nts73883ang-a.oregon-postgres.render.com/kulfi_db_7yxh"

products = [
    (1,  "Slice Kesar Badam", "IK0021", "New Bowring", Decimal("35.00"), Decimal("40.00"), 0,  6, "", True),
    (2,  "Slice Kesar Pista",  "IK0022", "New Bowring", Decimal("35.00"), Decimal("40.00"), 0,  6, "", True),
    (3,  "Slice Malai",        "IK0020", "New Bowring", Decimal("35.00"), Decimal("40.00"), 0,  6, "", True),
    (4,  "Pot",                "IK0019", "New Bowring", Decimal("30.00"), Decimal("40.00"), 0,  6, "", True),
    (5,  "Paan",               "IK0018", "New Bowring", Decimal("26.67"), Decimal("40.00"), 1,  6, "", True),
    (6,  "Guava",              "IK0017", "New Bowring", Decimal("26.67"), Decimal("40.00"), 31, 6, "", True),
    (7,  "Kesar Kajoor",       "IK0016", "New Bowring", Decimal("24.17"), Decimal("40.00"), 10, 6, "", True),
    (8,  "Litchi",             "IK0015", "New Bowring", Decimal("24.17"), Decimal("40.00"), 27, 6, "", True),
    (9,  "Elachi",             "IK0014", "New Bowring", Decimal("24.17"), Decimal("40.00"), 38, 6, "", True),
    (10, "Coconut",            "IK0013", "New Bowring", Decimal("24.17"), Decimal("40.00"), 28, 6, "", True),
    (11, "Caramel Coffee",     "IK0012", "New Bowring", Decimal("26.67"), Decimal("40.00"), 25, 6, "", True),
    (12, "Black Currant",      "IK0011", "New Bowring", Decimal("26.67"), Decimal("40.00"), 22, 6, "", True),
    (13, "Rose",               "IK0010", "New Bowring", Decimal("26.67"), Decimal("40.00"), 39, 6, "", True),
    (14, "Butterscotch",       "IK0009", "New Bowring", Decimal("26.67"), Decimal("40.00"), 19, 6, "", True),
    (15, "Dry Fruit",          "IK0008", "New Bowring", Decimal("26.67"), Decimal("40.00"), 17, 6, "", True),
    (16, "Mango Malai",        "IK0007", "New Bowring", Decimal("24.17"), Decimal("40.00"), 24, 6, "", True),
    (17, "Strawberry",         "IK0006", "New Bowring", Decimal("24.17"), Decimal("40.00"), 28, 6, "", True),
    (18, "Chocolate",          "IK0005", "New Bowring", Decimal("26.67"), Decimal("40.00"), 25, 6, "", True),
    (19, "Pista Badam",        "IK0004", "New Bowring", Decimal("26.67"), Decimal("40.00"), 32, 6, "", True),
    (20, "Kesar Pista",        "IK0003", "New Bowring", Decimal("24.17"), Decimal("40.00"), 26, 6, "", True),
    (21, "Kesar Badam",        "IK0002", "New Bowring", Decimal("24.17"), Decimal("40.00"), 11, 6, "", True),
    (22, "Malai",              "IK0001", "New Bowring", Decimal("24.17"), Decimal("40.00"), 32, 6, "", True),
]

print("Connecting to remote database...")
with psycopg.connect(REMOTE_DSN) as conn:
    with conn.cursor() as cur:
        # Delete existing products
        cur.execute("DELETE FROM inventory_product")
        deleted = cur.rowcount
        print(f"Cleared {deleted} old products")

        # Reset sequence
        cur.execute("SELECT setval(pg_get_serial_sequence('inventory_product', 'id'), 1, false)")

        # Insert all products
        insert_sql = """
            INSERT INTO inventory_product
                (id, name, sku, category, cost_price, selling_price,
                 current_stock, reorder_level, description, is_active,
                 created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                 NOW(), NOW())
        """
        for p in products:
            cur.execute(insert_sql, p)
            print(f"  Inserted: {p[1]} (SKU: {p[2]})")

        # Update sequence to next available id
        cur.execute("SELECT setval(pg_get_serial_sequence('inventory_product', 'id'), (SELECT MAX(id) FROM inventory_product))")

        conn.commit()
        print(f"\nSUCCESS! All 22 products committed to the live database!")

        # Verify
        cur.execute("SELECT COUNT(*) FROM inventory_product WHERE is_active = TRUE")
        count = cur.fetchone()[0]
        print(f"Verification: {count} active products in live database.")
