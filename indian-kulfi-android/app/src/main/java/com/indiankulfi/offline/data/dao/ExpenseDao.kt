package com.indiankulfi.offline.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.indiankulfi.offline.data.model.ExpenseEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ExpenseDao {
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insert(expense: ExpenseEntity)

    @Query("SELECT * FROM expenses ORDER BY operation_date DESC, created_at DESC LIMIT :limit")
    fun observeRecent(limit: Int): Flow<List<ExpenseEntity>>

    @Query("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE operation_date = :operationDate")
    fun observeTotalForDate(operationDate: String): Flow<Double?>

    @Query("SELECT * FROM expenses ORDER BY operation_date DESC, created_at DESC")
    fun observeAll(): Flow<List<ExpenseEntity>>
}
