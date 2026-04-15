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
import androidx.compose.material.icons.outlined.NoteAdd
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.indiankulfi.offline.data.model.ExpenseEntity

@Composable
fun ExpensesScreen(
    recentExpenses: List<ExpenseEntity>,
    onAddExpense: (String, String, String) -> Unit,
) {
    var showExpenseDialog by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            contentPadding = PaddingValues(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            item {
                SectionTitle(
                    title = "Operations expenses",
                    subtitle = "Track daily offline spending for net profit visibility.",
                )
            }

            if (recentExpenses.isEmpty()) {
                item { EmptyCard("No expense entries yet.") }
            } else {
                items(recentExpenses, key = { it.id }) { expense ->
                    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text(expense.details, fontWeight = FontWeight.SemiBold)
                            LabelValueRow("Amount", formatCurrency(expense.amount))
                            LabelValueRow("Date", expense.operationDate)
                        }
                    }
                }
            }
        }

        FloatingActionButton(
            onClick = { showExpenseDialog = true },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(20.dp),
        ) {
            Icon(Icons.Outlined.NoteAdd, contentDescription = "Add expense")
        }
    }

    if (showExpenseDialog) {
        var details by remember { mutableStateOf("") }
        var amount by remember { mutableStateOf("") }

        FormDialog(
            title = "Add expense",
            onDismiss = { showExpenseDialog = false },
            onConfirm = {
                onAddExpense(details, amount, com.indiankulfi.offline.data.repository.AppRepository.today())
                showExpenseDialog = false
            },
        ) {
            OutlinedTextField(value = details, onValueChange = { details = it }, label = { Text("Details") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = amount, onValueChange = { amount = it }, label = { Text("Amount") }, modifier = Modifier.fillMaxWidth())
        }
    }
}
