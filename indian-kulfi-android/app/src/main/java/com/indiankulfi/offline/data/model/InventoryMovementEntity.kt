package com.indiankulfi.offline.data.model

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "inventory_movements",
    foreignKeys = [
        ForeignKey(
            entity = ProductEntity::class,
            parentColumns = ["id"],
            childColumns = ["product_id"],
            onDelete = ForeignKey.CASCADE,
        )
    ],
    indices = [Index(value = ["product_id"])]
)
data class InventoryMovementEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "product_id") val productId: Int,
    @ColumnInfo(name = "movement_type") val movementType: String,
    val quantity: Int,
    @ColumnInfo(name = "unit_cost") val unitCost: Double,
    @ColumnInfo(name = "reference_document") val referenceDocument: String,
    val notes: String,
    @ColumnInfo(name = "movement_date") val movementDate: String,
    @ColumnInfo(name = "created_at") val createdAt: String,
    @ColumnInfo(name = "updated_at") val updatedAt: String,
)
