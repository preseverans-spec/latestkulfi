package com.indiankulfi.offline.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.SwapHoriz
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.indiankulfi.offline.data.model.InventoryMovementSummary
import com.indiankulfi.offline.data.model.ProductEntity
import com.indiankulfi.offline.data.repository.AppRepository

@Composable
fun ProductsScreen(
    products: List<ProductEntity>,
    recentMovements: List<InventoryMovementSummary>,
    onAddProduct: (String, String, String, String, String, String, String) -> Unit,
    onAddMovement: (Int, String, String, String, String, String, String) -> Unit,
) {
    var showProductDialog by remember { mutableStateOf(false) }
    var selectedProductForMovement by remember { mutableStateOf<ProductEntity?>(null) }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            contentPadding = PaddingValues(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            item {
                SectionTitle(
                    title = "Products & stock",
                    subtitle = "Manage the offline catalog and post stock movements against each item.",
                )
            }

            if (products.isEmpty()) {
                item { EmptyCard("No products found. Use the add button to create your first item.") }
            } else {
                items(products, key = { it.id }) { product ->
                    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text(product.name, fontWeight = FontWeight.SemiBold)
                            LabelValueRow("SKU", product.sku)
                            LabelValueRow("Category", product.category)
                            LabelValueRow("Stock", "${product.currentStock} pcs")
                            LabelValueRow("Sell price", formatCurrency(product.sellingPrice))
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                DetailChip(label = "Reorder ${product.reorderLevel}")
                                DetailChip(label = "Cost ${formatCurrency(product.costPrice)}")
                            }
                            TextButton(onClick = { selectedProductForMovement = product }) {
                                Icon(Icons.Outlined.SwapHoriz, contentDescription = null)
                                Text(" Move stock")
                            }
                        }
                    }
                }
            }

            item {
                SectionTitle(
                    title = "Recent stock movements",
                    subtitle = "Last offline inventory actions recorded on this device.",
                )
            }

            if (recentMovements.isEmpty()) {
                item { EmptyCard("No stock movements yet.") }
            } else {
                items(recentMovements, key = { it.id }) { movement ->
                    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text(movement.productName, fontWeight = FontWeight.SemiBold)
                            LabelValueRow("Type", movement.movementType)
                            LabelValueRow("Qty", movement.quantity.toString())
                            LabelValueRow("Date", movement.movementDate)
                            if (movement.notes.isNotBlank()) {
                                Text(movement.notes, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.72f))
                            }
                        }
                    }
                }
            }
        }

        FloatingActionButton(
            onClick = { showProductDialog = true },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(20.dp),
        ) {
            Icon(Icons.Outlined.Add, contentDescription = "Add product")
        }
    }

    if (showProductDialog) {
        var name by remember { mutableStateOf("") }
        var sku by remember { mutableStateOf("") }
        var category by remember { mutableStateOf("Kulfi") }
        var costPrice by remember { mutableStateOf("24.17") }
        var sellingPrice by remember { mutableStateOf("40") }
        var reorderLevel by remember { mutableStateOf("10") }
        var description by remember { mutableStateOf("") }

        FormDialog(
            title = "Add product",
            onDismiss = { showProductDialog = false },
            onConfirm = {
                onAddProduct(name, sku, category, costPrice, sellingPrice, reorderLevel, description)
                showProductDialog = false
            },
        ) {
            OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Name") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = sku, onValueChange = { sku = it }, label = { Text("SKU") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = category, onValueChange = { category = it }, label = { Text("Category") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = costPrice, onValueChange = { costPrice = it }, label = { Text("Cost price") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = sellingPrice, onValueChange = { sellingPrice = it }, label = { Text("Selling price") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = reorderLevel, onValueChange = { reorderLevel = it }, label = { Text("Reorder level") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = description, onValueChange = { description = it }, label = { Text("Description") }, modifier = Modifier.fillMaxWidth())
        }
    }

    selectedProductForMovement?.let { product ->
        var movementType by remember(product.id) { mutableStateOf(AppRepository.MOVEMENT_IN) }
        var quantity by remember(product.id) { mutableStateOf("1") }
        var unitCost by remember(product.id) { mutableStateOf(product.costPrice.toString()) }
        var referenceDocument by remember(product.id) { mutableStateOf("") }
        var notes by remember(product.id) { mutableStateOf("") }

        FormDialog(
            title = "Stock movement: ${product.name}",
            onDismiss = { selectedProductForMovement = null },
            onConfirm = {
                onAddMovement(product.id, movementType, quantity, unitCost, referenceDocument, notes, AppRepository.today())
                selectedProductForMovement = null
            },
        ) {
            SelectionPicker(
                label = "Movement type",
                options = listOf(AppRepository.MOVEMENT_IN, AppRepository.MOVEMENT_OUT, AppRepository.MOVEMENT_ADJUSTMENT),
                selected = movementType,
                onSelected = { movementType = it },
            )
            OutlinedTextField(
                value = quantity,
                onValueChange = { quantity = it },
                label = { Text(if (movementType == AppRepository.MOVEMENT_ADJUSTMENT) "New stock level" else "Quantity") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(value = unitCost, onValueChange = { unitCost = it }, label = { Text("Unit cost") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = referenceDocument, onValueChange = { referenceDocument = it }, label = { Text("Reference") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = notes, onValueChange = { notes = it }, label = { Text("Notes") }, modifier = Modifier.fillMaxWidth())
        }
    }
}
