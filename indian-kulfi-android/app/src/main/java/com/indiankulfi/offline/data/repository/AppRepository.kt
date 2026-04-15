package com.indiankulfi.offline.data.repository

import androidx.room.withTransaction
import com.indiankulfi.offline.data.AppDatabase
import com.indiankulfi.offline.data.model.DailyReportSnapshot
import com.indiankulfi.offline.data.model.DashboardSnapshot
import com.indiankulfi.offline.data.model.ExpenseEntity
import com.indiankulfi.offline.data.model.InventoryMovementEntity
import com.indiankulfi.offline.data.model.ProductEntity
import com.indiankulfi.offline.data.model.SaleEntity
import com.indiankulfi.offline.data.seed.SeedData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.Locale

class AppRepository(
    private val database: AppDatabase,
) {
    private val productDao = database.productDao()
    private val movementDao = database.inventoryMovementDao()
    private val saleDao = database.saleDao()
    private val expenseDao = database.expenseDao()

    val products: Flow<List<ProductEntity>> = productDao.observeAllActive()
    val lowStockProducts: Flow<List<ProductEntity>> = productDao.observeLowStock()
    val recentMovements = movementDao.observeRecent(limit = 15)
    val recentSales = saleDao.observeRecent(limit = 15)
    val recentExpenses = expenseDao.observeRecent(limit = 15)

    val dashboard: Flow<DashboardSnapshot> = combine(
        productDao.observeTotalStock(),
        lowStockProducts,
        saleDao.observeSalesCountForDate(today()),
        saleDao.observeRevenueForDate(today()),
        saleDao.observeGrossProfitForDate(today()),
        expenseDao.observeTotalForDate(today()),
    ) { totalStock, lowStock, salesCount, revenue, grossProfit, expenses ->
        DashboardSnapshot(
            totalStock = totalStock ?: 0,
            lowStockCount = lowStock.size,
            salesCount = salesCount,
            revenue = revenue ?: 0.0,
            grossProfit = grossProfit ?: 0.0,
            expenses = expenses ?: 0.0,
        )
    }

    val weeklyReport: Flow<List<DailyReportSnapshot>> = combine(
        saleDao.observeAllReportItems(),
        expenseDao.observeAll(),
    ) { sales, expenses ->
        val salesByDate = sales.groupBy { it.saleDate }
        val expensesByDate = expenses.groupBy { it.operationDate }
        lastSevenDates().map { date ->
            val dailySales = salesByDate[date].orEmpty()
            val dailyExpenses = expensesByDate[date].orEmpty()
            val revenue = dailySales.sumOf { it.totalPrice }
            val cost = dailySales.sumOf { it.costPrice * it.quantity }
            DailyReportSnapshot(
                date = date,
                salesCount = dailySales.sumOf { it.quantity },
                revenue = revenue,
                cost = cost,
                expenses = dailyExpenses.sumOf(ExpenseEntity::amount),
            )
        }
    }

    suspend fun seedDefaultsIfEmpty() {
        if (productDao.countAll() > 0) {
            return
        }
        val now = nowDateTime()
        productDao.insertAll(SeedData.defaultProducts(now))
    }

    suspend fun addProduct(
        name: String,
        sku: String,
        category: String,
        costPrice: Double,
        sellingPrice: Double,
        reorderLevel: Int,
        description: String,
    ) {
        require(name.isNotBlank()) { "Product name is required." }
        require(sku.isNotBlank()) { "SKU is required." }
        require(costPrice >= 0.0) { "Cost price cannot be negative." }
        require(sellingPrice >= 0.0) { "Selling price cannot be negative." }
        require(reorderLevel >= 0) { "Reorder level cannot be negative." }

        val now = nowDateTime()
        productDao.insert(
            ProductEntity(
                name = name.trim(),
                sku = sku.trim().uppercase(Locale.ENGLISH),
                category = category.trim().ifBlank { "Kulfi" },
                costPrice = costPrice,
                sellingPrice = sellingPrice,
                currentStock = 0,
                reorderLevel = reorderLevel,
                description = description.trim(),
                createdAt = now,
                updatedAt = now,
            )
        )
    }

    suspend fun addInventoryMovement(
        productId: Int,
        movementType: String,
        quantity: Int,
        unitCost: Double,
        referenceDocument: String,
        notes: String,
        movementDate: String,
    ) {
        require(quantity > 0) { "Quantity must be greater than zero." }
        require(unitCost >= 0.0) { "Unit cost cannot be negative." }

        database.withTransaction {
            val product = productDao.getById(productId) ?: error("Product not found.")
            val newStock = when (movementType) {
                MOVEMENT_IN -> product.currentStock + quantity
                MOVEMENT_OUT -> {
                    val result = product.currentStock - quantity
                    require(result >= 0) { "Insufficient stock for stock-out movement." }
                    result
                }
                MOVEMENT_ADJUSTMENT -> quantity
                else -> error("Unsupported movement type.")
            }
            val now = nowDateTime()
            movementDao.insert(
                InventoryMovementEntity(
                    productId = productId,
                    movementType = movementType,
                    quantity = quantity,
                    unitCost = unitCost,
                    referenceDocument = referenceDocument.trim(),
                    notes = notes.trim(),
                    movementDate = movementDate,
                    createdAt = now,
                    updatedAt = now,
                )
            )
            productDao.updateStock(productId, newStock, now)
        }
    }

    suspend fun addSale(
        productId: Int,
        quantity: Int,
        unitPrice: Double,
        notes: String,
        saleDate: String,
    ) {
        require(quantity > 0) { "Sale quantity must be greater than zero." }
        require(unitPrice >= 0.0) { "Unit price cannot be negative." }

        database.withTransaction {
            val product = productDao.getById(productId) ?: error("Product not found.")
            val remainingStock = product.currentStock - quantity
            require(remainingStock >= 0) { "Not enough stock available for this sale." }

            saleDao.insert(
                SaleEntity(
                    productId = productId,
                    quantity = quantity,
                    unitPrice = unitPrice,
                    totalPrice = quantity * unitPrice,
                    saleDate = saleDate,
                    saleTime = nowTime(),
                    notes = notes.trim(),
                    createdAt = nowDateTime(),
                )
            )
            productDao.updateStock(productId, remainingStock, nowDateTime())
        }
    }

    suspend fun addExpense(
        details: String,
        amount: Double,
        operationDate: String,
    ) {
        require(details.isNotBlank()) { "Expense details are required." }
        require(amount > 0.0) { "Expense amount must be greater than zero." }

        expenseDao.insert(
            ExpenseEntity(
                operationDate = operationDate,
                details = details.trim(),
                amount = amount,
                createdAt = nowDateTime(),
            )
        )
    }

    companion object {
        const val MOVEMENT_IN = "IN"
        const val MOVEMENT_OUT = "OUT"
        const val MOVEMENT_ADJUSTMENT = "ADJUSTMENT"

        private val dateFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE
        private val dateTimeFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME
        private val timeFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm", Locale.ENGLISH)

        fun today(): String = LocalDate.now().format(dateFormatter)

        fun lastSevenDates(): List<String> {
            val today = LocalDate.now()
            return (6 downTo 0).map { today.minusDays(it.toLong()).format(dateFormatter) }
        }

        fun nowDateTime(): String = LocalDateTime.now().format(dateTimeFormatter)

        fun nowTime(): String = LocalTime.now().format(timeFormatter)
    }
}
