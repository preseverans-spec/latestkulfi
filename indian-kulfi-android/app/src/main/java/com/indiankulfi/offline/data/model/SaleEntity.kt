package com.indiankulfi.offline.data.model

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "sales",
    foreignKeys = [
        ForeignKey(
            entity = ProductEntity::class,
            parentColumns = ["id"],
            childColumns = ["product_id"],
            onDelete = ForeignKey.CASCADE,
        )
    ],
    indices = [Index(value = ["product_id"]), Index(value = ["sale_date"])]
)
data class SaleEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "product_id") val productId: Int,
    val quantity: Int,
    @ColumnInfo(name = "unit_price") val unitPrice: Double,
    @ColumnInfo(name = "total_price") val totalPrice: Double,
    @ColumnInfo(name = "sale_date") val saleDate: String,
    @ColumnInfo(name = "sale_time") val saleTime: String,
    val notes: String,
    @ColumnInfo(name = "created_at") val createdAt: String,
)
