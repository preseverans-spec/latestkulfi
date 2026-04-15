package com.indiankulfi.offline.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.indiankulfi.offline.data.model.SaleEntity
import com.indiankulfi.offline.data.model.SaleReportItem
import com.indiankulfi.offline.data.model.SaleSummary
import kotlinx.coroutines.flow.Flow

@Dao
interface SaleDao {
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insert(sale: SaleEntity)

    @Query(
        """
        SELECT sales.id AS id,
               products.name AS productName,
               sales.quantity AS quantity,
               sales.unit_price AS unitPrice,
               sales.total_price AS totalPrice,
               sales.sale_date AS saleDate,
               sales.sale_time AS saleTime,
               sales.notes AS notes
        FROM sales
        INNER JOIN products ON products.id = sales.product_id
        ORDER BY sales.sale_date DESC, sales.sale_time DESC, sales.id DESC
        LIMIT :limit
        """
    )
    fun observeRecent(limit: Int): Flow<List<SaleSummary>>

    @Query("SELECT COUNT(*) FROM sales WHERE sale_date = :saleDate")
    fun observeSalesCountForDate(saleDate: String): Flow<Int>

    @Query("SELECT COALESCE(SUM(total_price), 0) FROM sales WHERE sale_date = :saleDate")
    fun observeRevenueForDate(saleDate: String): Flow<Double?>

    @Query(
        """
        SELECT COALESCE(SUM((sales.unit_price - products.cost_price) * sales.quantity), 0)
        FROM sales
        INNER JOIN products ON products.id = sales.product_id
        WHERE sales.sale_date = :saleDate
        """
    )
    fun observeGrossProfitForDate(saleDate: String): Flow<Double?>

    @Query(
        """
        SELECT sales.id AS id,
               sales.product_id AS productId,
               products.name AS productName,
               sales.quantity AS quantity,
               sales.unit_price AS unitPrice,
               sales.total_price AS totalPrice,
               sales.sale_date AS saleDate,
               sales.sale_time AS saleTime,
               products.cost_price AS costPrice,
               sales.notes AS notes
        FROM sales
        INNER JOIN products ON products.id = sales.product_id
        ORDER BY sales.sale_date DESC, sales.sale_time DESC, sales.id DESC
        """
    )
    fun observeAllReportItems(): Flow<List<SaleReportItem>>
}
