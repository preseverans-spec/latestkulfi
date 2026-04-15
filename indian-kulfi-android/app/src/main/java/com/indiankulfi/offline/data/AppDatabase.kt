package com.indiankulfi.offline.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.indiankulfi.offline.data.dao.ExpenseDao
import com.indiankulfi.offline.data.dao.InventoryMovementDao
import com.indiankulfi.offline.data.dao.ProductDao
import com.indiankulfi.offline.data.dao.SaleDao
import com.indiankulfi.offline.data.model.ExpenseEntity
import com.indiankulfi.offline.data.model.InventoryMovementEntity
import com.indiankulfi.offline.data.model.ProductEntity
import com.indiankulfi.offline.data.model.SaleEntity

@Database(
    entities = [ProductEntity::class, InventoryMovementEntity::class, SaleEntity::class, ExpenseEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun inventoryMovementDao(): InventoryMovementDao
    abstract fun saleDao(): SaleDao
    abstract fun expenseDao(): ExpenseDao

    companion object {
        @Volatile
        private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "indian_kulfi_offline.db"
                ).build().also { instance = it }
            }
        }
    }
}
