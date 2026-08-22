"""
Deletes transactional records created/dated strictly AFTER a given cutoff date,
effectively rolling the database back to the state it was in at the end of that date.

Usage (ALWAYS dry-run first):
    python manage.py wipe_after_date --after 2026-08-17
    python manage.py wipe_after_date --after 2026-08-17 --confirm

Safety:
- Without --confirm, this only PRINTS counts of what would be deleted (dry run).
- Everything runs inside a single DB transaction; if anything fails, nothing is deleted.
- Make sure you have a verified backup of the target database before using --confirm.
"""
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inventory.models import (
    Inventory,
    Sales,
    SalesStockTaken,
    SalesCountDraft,
    OperationsExpense,
    OperationsIncome,
    StockOrder,
    DailySalesReport,
    WeeklyReport,
    ProfitReport,
)


class Command(BaseCommand):
    help = (
        "Delete Sales, Inventory movements, StockOrders, Operations Expense/Income, "
        "sales draft/stock-taken records, and aggregated reports dated after --after. "
        "Runs as a dry run unless --confirm is passed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--after",
            required=True,
            help="Cutoff date (YYYY-MM-DD). Records dated/created strictly AFTER this date are deleted; this date itself is kept.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Actually perform the deletion. Without this flag, only a dry-run report is printed.",
        )

    def handle(self, *args, **options):
        try:
            cutoff = datetime.strptime(options["after"], "%Y-%m-%d").date()
        except ValueError:
            raise CommandError("--after must be in YYYY-MM-DD format")

        confirm = options["confirm"]

        querysets = [
            ("Sales", Sales.objects.filter(sale_date__gt=cutoff)),
            ("Inventory (stock in/out/adjustment)", Inventory.objects.filter(movement_date__gt=cutoff)),
            ("StockOrder", StockOrder.objects.filter(order_date__gt=cutoff)),
            ("OperationsExpense", OperationsExpense.objects.filter(operation_date__gt=cutoff)),
            ("OperationsIncome", OperationsIncome.objects.filter(income_date__gt=cutoff)),
            ("SalesStockTaken", SalesStockTaken.objects.filter(sales_date__gt=cutoff)),
            ("SalesCountDraft", SalesCountDraft.objects.filter(sales_date__gt=cutoff)),
            ("DailySalesReport", DailySalesReport.objects.filter(report_date__gt=cutoff)),
            ("WeeklyReport", WeeklyReport.objects.filter(start_date__gt=cutoff)),
            ("ProfitReport", ProfitReport.objects.filter(report_date__gt=cutoff)),
        ]

        self.stdout.write(self.style.WARNING(f"Cutoff date: {cutoff} (kept). Deleting everything strictly after this date."))
        self.stdout.write("")

        total = 0
        for label, qs in querysets:
            count = qs.count()
            total += count
            self.stdout.write(f"{label:<40} {count:>8} row(s)")

        self.stdout.write("")

        if not confirm:
            self.stdout.write(self.style.NOTICE(
                f"DRY RUN: {total} total row(s) would be deleted. Re-run with --confirm to actually delete."
            ))
            return

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nothing to delete."))
            return

        with transaction.atomic():
            for label, qs in querysets:
                deleted_count, _ = qs.delete()
                self.stdout.write(f"Deleted {deleted_count} row(s) from {label}")

        self.stdout.write(self.style.SUCCESS(f"Done. Deleted {total} row(s) total. Database rolled back to end of {cutoff}."))
