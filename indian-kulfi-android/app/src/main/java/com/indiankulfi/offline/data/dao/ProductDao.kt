package com.indiankulfi.offline.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.indiankulfi.offline.data.model.ProductEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductDao {
    @Query("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
    fun observeAllActive(): Flow<List<ProductEntity>>

    @Query("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
    suspend fun getAllActive(): List<ProductEntity>

    @Query("SELECT * FROM products WHERE is_active = 1 AND current_stock <= reorder_level ORDER BY current_stock ASC, name ASC")
    fun observeLowStock(): Flow<List<ProductEntity>>

    @Query("SELECT COALESCE(SUM(current_stock), 0) FROM products WHERE is_active = 1")
    fun observeTotalStock(): Flow<Int?>

    @Query("SELECT * FROM products WHERE id = :productId LIMIT 1")
    suspend fun getById(productId: Int): ProductEntity?

    @Query("SELECT COUNT(*) FROM products")
    suspend fun countAll(): Int

    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insert(product: ProductEntity): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertAll(products: List<ProductEntity>)

    @Query("UPDATE products SET current_stock = :newStock, updated_at = :updatedAt WHERE id = :productId")
    suspend fun updateStock(productId: Int, newStock: Int, updatedAt: String)
}
