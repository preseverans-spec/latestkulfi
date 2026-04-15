package com.indiankulfi.offline.data.model

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(tableName = "expenses", indices = [Index(value = ["operation_date"])])
data class ExpenseEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "operation_date") val operationDate: String,
    val details: String,
    val amount: Double,
    @ColumnInfo(name = "created_at") val createdAt: String,
)
