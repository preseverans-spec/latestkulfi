package com.indiankulfi.offline.data.model

data class InventoryMovementSummary(
    val id: Int,
    val productName: String,
    val movementType: String,
    val quantity: Int,
    val unitCost: Double,
    val movementDate: String,
    val notes: String,
)

data class SaleSummary(
    val id: Int,
    val productName: String,
    val quantity: Int,
    val unitPrice: Double,
    val totalPrice: Double,
    val saleDate: String,
    val saleTime: String,
    val notes: String,
)

data class SaleReportItem(
    val id: Int,
    val productId: Int,
    val productName: String,
    val quantity: Int,
    val unitPrice: Double,
    val totalPrice: Double,
    val saleDate: String,
    val saleTime: String,
    val costPrice: Double,
    val notes: String,
)

data class DashboardSnapshot(
    val totalStock: Int = 0,
    val lowStockCount: Int = 0,
    val salesCount: Int = 0,
    val revenue: Double = 0.0,
    val grossProfit: Double = 0.0,
    val expenses: Double = 0.0,
) {
    val netProfit: Double
        get() = grossProfit - expenses
}

data class DailyReportSnapshot(
    val date: String,
    val salesCount: Int,
    val revenue: Double,
    val cost: Double,
    val expenses: Double,
) {
    val grossProfit: Double
        get() = revenue - cost

    val netProfit: Double
        get() = grossProfit - expenses
}
