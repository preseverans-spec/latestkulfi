package com.indiankulfi.offline.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.indiankulfi.offline.data.model.DailyReportSnapshot
import com.indiankulfi.offline.data.model.DashboardSnapshot
import com.indiankulfi.offline.data.model.ProductEntity

@Composable
fun DashboardScreen(
    dashboard: DashboardSnapshot,
    lowStockProducts: List<ProductEntity>,
    weeklyReport: List<DailyReportSnapshot>,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            SectionTitle(
                title = "The Indian Kulfi",
                subtitle = "Offline operations dashboard for daily stock, sales, and expenses.",
            )
        }

        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary),
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Text(
                        text = "Today's net position",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.78f),
                    )
                    Text(
                        text = formatCurrency(dashboard.netProfit),
                        style = MaterialTheme.typography.displaySmall,
                        color = MaterialTheme.colorScheme.onPrimary,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = "Revenue ${formatCurrency(dashboard.revenue)}  •  Expenses ${formatCurrency(dashboard.expenses)}",
                        color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.86f),
                    )
                }
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                MetricCard(
                    title = "Units in stock",
                    value = dashboard.totalStock.toString(),
                    modifier = Modifier.weight(1f),
                )
                MetricCard(
                    title = "Sales today",
                    value = dashboard.salesCount.toString(),
                    modifier = Modifier.weight(1f),
                )
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                MetricCard(
                    title = "Gross profit",
                    value = formatCurrency(dashboard.grossProfit),
                    modifier = Modifier.weight(1f),
                )
                MetricCard(
                    title = "Low stock items",
                    value = dashboard.lowStockCount.toString(),
                    modifier = Modifier.weight(1f),
                )
            }
        }

        item {
            SectionTitle(
                title = "Low stock watchlist",
                subtitle = "Products already at or below their reorder level.",
            )
        }

        if (lowStockProducts.isEmpty()) {
            item { EmptyCard("No low-stock alerts right now.") }
        } else {
            items(lowStockProducts, key = { it.id }) { product ->
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(product.name, fontWeight = FontWeight.SemiBold)
                        LabelValueRow("Current stock", "${product.currentStock} pcs")
                        LabelValueRow("Reorder level", "${product.reorderLevel} pcs")
                        LabelValueRow("SKU", product.sku)
                    }
                }
            }
        }

        item {
            SectionTitle(
                title = "Last 7 days",
                subtitle = "Quick offline performance summary.",
            )
        }

        if (weeklyReport.isEmpty()) {
            item { EmptyCard("No sales or expense activity yet.") }
        } else {
            items(weeklyReport, key = { it.date }) { row ->
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(row.date, fontWeight = FontWeight.SemiBold)
                        LabelValueRow("Units sold", row.salesCount.toString())
                        LabelValueRow("Revenue", formatCurrency(row.revenue))
                        LabelValueRow("Gross profit", formatCurrency(row.grossProfit))
                        LabelValueRow("Net profit", formatCurrency(row.netProfit))
                    }
                }
            }
        }
    }
}
