package com.indiankulfi.offline.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.Modifier
import com.indiankulfi.offline.ui.screens.DashboardScreen
import com.indiankulfi.offline.ui.screens.ExpensesScreen
import com.indiankulfi.offline.ui.screens.ProductsScreen
import com.indiankulfi.offline.ui.screens.ReportsScreen
import com.indiankulfi.offline.ui.screens.SalesScreen
import com.indiankulfi.offline.viewmodel.MainViewModel

@Composable
fun IndianKulfiApp(viewModel: MainViewModel) {
    val selectedTab by viewModel.selectedTab.collectAsState()
    val dashboard by viewModel.dashboard.collectAsState()
    val products by viewModel.products.collectAsState()
    val lowStockProducts by viewModel.lowStockProducts.collectAsState()
    val recentMovements by viewModel.recentMovements.collectAsState()
    val recentSales by viewModel.recentSales.collectAsState()
    val recentExpenses by viewModel.recentExpenses.collectAsState()
    val weeklyReport by viewModel.weeklyReport.collectAsState()
    val message by viewModel.message.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(message) {
        message?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.consumeMessage()
        }
    }

    Scaffold(
        modifier = Modifier.windowInsetsPadding(WindowInsets.safeDrawing),
        containerColor = Color.Transparent,
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        bottomBar = {
            NavigationBar {
                AppTab.entries.forEach { tab ->
                    NavigationBarItem(
                        selected = selectedTab == tab,
                        onClick = { viewModel.selectTab(tab) },
                        icon = { Icon(imageVector = tab.icon, contentDescription = tab.label) },
                        label = { Text(tab.label) },
                    )
                }
            }
        },
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(Color(0xFFF5F3F1), Color(0xFFFFFAF4), Color(0xFFE8D8B1)),
                    )
                )
                .padding(innerPadding),
        ) {
            when (selectedTab) {
                AppTab.Dashboard -> DashboardScreen(
                    dashboard = dashboard,
                    lowStockProducts = lowStockProducts,
                    weeklyReport = weeklyReport,
                )

                AppTab.Products -> ProductsScreen(
                    products = products,
                    recentMovements = recentMovements,
                    onAddProduct = viewModel::addProduct,
                    onAddMovement = viewModel::addInventoryMovement,
                )

                AppTab.Sales -> SalesScreen(
                    products = products,
                    recentSales = recentSales,
                    onAddSale = viewModel::recordSale,
                )

                AppTab.Expenses -> ExpensesScreen(
                    recentExpenses = recentExpenses,
                    onAddExpense = viewModel::addExpense,
                )

                AppTab.Reports -> ReportsScreen(
                    weeklyReport = weeklyReport,
                    recentSales = recentSales,
                    recentExpenses = recentExpenses,
                )
            }
        }
    }
}
