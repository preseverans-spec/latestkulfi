package com.indiankulfi.offline.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
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
import com.indiankulfi.offline.data.model.ExpenseEntity
import com.indiankulfi.offline.data.model.SaleSummary

@Composable
fun ReportsScreen(
    weeklyReport: List<DailyReportSnapshot>,
    recentSales: List<SaleSummary>,
    recentExpenses: List<ExpenseEntity>,
) {
    val weeklyRevenue = weeklyReport.sumOf { it.revenue }
    val weeklyNetProfit = weeklyReport.sumOf { it.netProfit }
    val weeklyExpenses = recentExpenses.take(7).sumOf { it.amount }
    val unitsSold = recentSales.take(20).sumOf { it.quantity }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            SectionTitle(
                title = "Reports",
                subtitle = "Seven-day offline summary using data stored on the device.",
            )
        }

        item {
            MetricCard(title = "7-day revenue", value = formatCurrency(weeklyRevenue))
        }

        item {
            MetricCard(title = "7-day net profit", value = formatCurrency(weeklyNetProfit))
        }

        item {
            MetricCard(title = "Recent expense total", value = formatCurrency(weeklyExpenses))
        }

        item {
            MetricCard(title = "Units sold snapshot", value = unitsSold.toString())
        }

        item {
            SectionTitle(
                title = "Daily breakdown",
                subtitle = "Revenue, cost, and expense rollup per day.",
            )
        }

        if (weeklyReport.isEmpty()) {
            item { EmptyCard("No reporting data available yet.") }
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
                        LabelValueRow("Cost", formatCurrency(row.cost))
                        LabelValueRow("Expenses", formatCurrency(row.expenses))
                        LabelValueRow("Net profit", formatCurrency(row.netProfit))
                    }
                }
            }
        }
    }
}
