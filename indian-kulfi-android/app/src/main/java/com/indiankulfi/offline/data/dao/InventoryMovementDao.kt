package com.indiankulfi.offline.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.indiankulfi.offline.data.model.InventoryMovementEntity
import com.indiankulfi.offline.data.model.InventoryMovementSummary
import kotlinx.coroutines.flow.Flow

@Dao
interface InventoryMovementDao {
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insert(movement: InventoryMovementEntity)

    @Query(
        """
        SELECT inventory_movements.id AS id,
               products.name AS productName,
               inventory_movements.movement_type AS movementType,
               inventory_movements.quantity AS quantity,
               inventory_movements.unit_cost AS unitCost,
               inventory_movements.movement_date AS movementDate,
               inventory_movements.notes AS notes
        FROM inventory_movements
        INNER JOIN products ON products.id = inventory_movements.product_id
        ORDER BY inventory_movements.created_at DESC
        LIMIT :limit
        """
    )
    fun observeRecent(limit: Int): Flow<List<InventoryMovementSummary>>
}
