package com.indiankulfi.offline.data.model

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "products",
    indices = [
        Index(value = ["name"], unique = true),
        Index(value = ["sku"], unique = true),
    ]
)
data class ProductEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val name: String,
    val sku: String,
    val category: String,
    @ColumnInfo(name = "cost_price") val costPrice: Double,
    @ColumnInfo(name = "selling_price") val sellingPrice: Double,
    @ColumnInfo(name = "current_stock") val currentStock: Int,
    @ColumnInfo(name = "reorder_level") val reorderLevel: Int,
    val description: String,
    @ColumnInfo(name = "is_active") val isActive: Boolean = true,
    @ColumnInfo(name = "created_at") val createdAt: String,
    @ColumnInfo(name = "updated_at") val updatedAt: String,
)
