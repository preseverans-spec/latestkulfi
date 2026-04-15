package com.indiankulfi.offline.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.indiankulfi.offline.data.AppDatabase
import com.indiankulfi.offline.data.model.DailyReportSnapshot
import com.indiankulfi.offline.data.model.DashboardSnapshot
import com.indiankulfi.offline.data.model.ExpenseEntity
import com.indiankulfi.offline.data.model.InventoryMovementSummary
import com.indiankulfi.offline.data.model.ProductEntity
import com.indiankulfi.offline.data.model.SaleSummary
import com.indiankulfi.offline.data.repository.AppRepository
import com.indiankulfi.offline.ui.AppTab
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = AppRepository(AppDatabase.getInstance(application))

    private val _selectedTab = MutableStateFlow(AppTab.Dashboard)
    val selectedTab: StateFlow<AppTab> = _selectedTab.asStateFlow()

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    val dashboard = repository.dashboard.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = DashboardSnapshot(),
    )

    val products = repository.products.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<ProductEntity>(),
    )

    val lowStockProducts = repository.lowStockProducts.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<ProductEntity>(),
    )

    val recentMovements = repository.recentMovements.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<InventoryMovementSummary>(),
    )

    val recentSales = repository.recentSales.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<SaleSummary>(),
    )

    val recentExpenses = repository.recentExpenses.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<ExpenseEntity>(),
    )

    val weeklyReport = repository.weeklyReport.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList<DailyReportSnapshot>(),
    )

    init {
        viewModelScope.launch {
            repository.seedDefaultsIfEmpty()
        }
    }

    fun selectTab(tab: AppTab) {
        _selectedTab.value = tab
    }

    fun consumeMessage() {
        _message.value = null
    }

    fun addProduct(
        name: String,
        sku: String,
        category: String,
        costPrice: String,
        sellingPrice: String,
        reorderLevel: String,
        description: String,
    ) {
        launchAction(successMessage = "Product saved.") {
            repository.addProduct(
                name = name,
                sku = sku,
                category = category,
                costPrice = parseDouble(costPrice, "Cost price"),
                sellingPrice = parseDouble(sellingPrice, "Selling price"),
                reorderLevel = parseInt(reorderLevel, "Reorder level"),
                description = description,
            )
        }
    }

    fun addInventoryMovement(
        productId: Int,
        movementType: String,
        quantity: String,
        unitCost: String,
        referenceDocument: String,
        notes: String,
        movementDate: String = AppRepository.today(),
    ) {
        launchAction(successMessage = "Stock movement saved.") {
            repository.addInventoryMovement(
                productId = productId,
                movementType = movementType,
                quantity = parseInt(quantity, "Quantity"),
                unitCost = parseDouble(unitCost, "Unit cost"),
                referenceDocument = referenceDocument,
                notes = notes,
                movementDate = movementDate,
            )
        }
    }

    fun recordSale(
        productId: Int,
        quantity: String,
        unitPrice: String,
        notes: String,
        saleDate: String = AppRepository.today(),
    ) {
        launchAction(successMessage = "Sale recorded.") {
            repository.addSale(
                productId = productId,
                quantity = parseInt(quantity, "Quantity"),
                unitPrice = parseDouble(unitPrice, "Unit price"),
                notes = notes,
                saleDate = saleDate,
            )
        }
    }

    fun addExpense(
        details: String,
        amount: String,
        operationDate: String = AppRepository.today(),
    ) {
        launchAction(successMessage = "Expense added.") {
            repository.addExpense(
                details = details,
                amount = parseDouble(amount, "Amount"),
                operationDate = operationDate,
            )
        }
    }

    private fun launchAction(successMessage: String, block: suspend () -> Unit) {
        viewModelScope.launch {
            runCatching { block() }
                .onSuccess { _message.value = successMessage }
                .onFailure { throwable ->
                    _message.value = throwable.message ?: "Something went wrong."
                }
        }
    }

    private fun parseInt(value: String, fieldName: String): Int {
        return value.trim().toIntOrNull() ?: throw IllegalArgumentException("$fieldName must be a whole number.")
    }

    private fun parseDouble(value: String, fieldName: String): Double {
        return value.trim().toDoubleOrNull() ?: throw IllegalArgumentException("$fieldName must be a valid number.")
    }
}
