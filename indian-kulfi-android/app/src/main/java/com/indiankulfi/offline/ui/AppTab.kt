package com.indiankulfi.offline.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Assessment
import androidx.compose.material.icons.outlined.Dashboard
import androidx.compose.material.icons.outlined.Inventory2
import androidx.compose.material.icons.outlined.ReceiptLong
import androidx.compose.material.icons.outlined.ShoppingCart
import androidx.compose.ui.graphics.vector.ImageVector

enum class AppTab(
    val label: String,
    val icon: ImageVector,
) {
    Dashboard("Dashboard", Icons.Outlined.Dashboard),
    Products("Products", Icons.Outlined.Inventory2),
    Sales("Sales", Icons.Outlined.ShoppingCart),
    Expenses("Expenses", Icons.Outlined.ReceiptLong),
    Reports("Reports", Icons.Outlined.Assessment),
}
