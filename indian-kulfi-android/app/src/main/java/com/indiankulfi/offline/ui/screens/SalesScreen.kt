package com.indiankulfi.offline.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AddShoppingCart
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.indiankulfi.offline.data.model.ProductEntity
import com.indiankulfi.offline.data.model.SaleSummary

@Composable
fun SalesScreen(
    products: List<ProductEntity>,
    recentSales: List<SaleSummary>,
    onAddSale: (Int, String, String, String, String) -> Unit,
) {
    var showSaleDialog by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            contentPadding = PaddingValues(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            item {
                SectionTitle(
                    title = "Sales",
                    subtitle = "Capture offline sales and deduct stock in the same step.",
                )
            }

            if (recentSales.isEmpty()) {
                item { EmptyCard("No sales recorded yet.") }
            } else {
                items(recentSales, key = { it.id }) { sale ->
                    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text(sale.productName, fontWeight = FontWeight.SemiBold)
                            LabelValueRow("Quantity", sale.quantity.toString())
                            LabelValueRow("Revenue", formatCurrency(sale.totalPrice))
                            LabelValueRow("Date", "${sale.saleDate} ${sale.saleTime}")
                            if (sale.notes.isNotBlank()) {
                                Text(sale.notes, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f))
                            }
                        }
                    }
                }
            }
        }

        FloatingActionButton(
            onClick = { showSaleDialog = true },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(20.dp),
        ) {
            Icon(Icons.Outlined.AddShoppingCart, contentDescription = "Add sale")
        }
    }

    if (showSaleDialog) {
        var selectedProductId by remember { mutableIntStateOf(0) }
        var quantity by remember { mutableStateOf("1") }
        var unitPrice by remember { mutableStateOf("40") }
        var notes by remember { mutableStateOf("") }

        FormDialog(
            title = "Record sale",
            onDismiss = { showSaleDialog = false },
            onConfirm = {
                if (selectedProductId > 0) {
                    onAddSale(selectedProductId, quantity, unitPrice, notes, com.indiankulfi.offline.data.repository.AppRepository.today())
                }
                showSaleDialog = false
            },
        ) {
            ProductPicker(
                products = products,
                selectedProductId = selectedProductId.takeIf { it > 0 },
                onSelected = { product ->
                    selectedProductId = product.id
                    unitPrice = product.sellingPrice.toString()
                },
            )
            OutlinedTextField(value = quantity, onValueChange = { quantity = it }, label = { Text("Quantity") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = unitPrice, onValueChange = { unitPrice = it }, label = { Text("Unit price") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = notes, onValueChange = { notes = it }, label = { Text("Notes") }, modifier = Modifier.fillMaxWidth())
        }
    }
}
