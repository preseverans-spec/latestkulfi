package com.indiankulfi.offline.data.seed

import com.indiankulfi.offline.data.model.ProductEntity

object SeedData {
    fun defaultProducts(now: String): List<ProductEntity> {
        return listOf(
            ProductEntity(name = "Malai", sku = "IK-001", category = "Classic", costPrice = 24.17, sellingPrice = 40.0, currentStock = 0, reorderLevel = 12, description = "Signature creamy malai kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Kesar Badam", sku = "IK-002", category = "Classic", costPrice = 24.17, sellingPrice = 40.0, currentStock = 0, reorderLevel = 12, description = "Saffron and almond kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Kesar Pista", sku = "IK-003", category = "Classic", costPrice = 24.17, sellingPrice = 40.0, currentStock = 0, reorderLevel = 12, description = "Saffron pistachio blend.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Pista Badam", sku = "IK-004", category = "Premium", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 10, description = "Premium pista badam kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Chocolate", sku = "IK-005", category = "Premium", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 10, description = "Rich chocolate kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Strawberry", sku = "IK-006", category = "Fruit", costPrice = 24.17, sellingPrice = 40.0, currentStock = 0, reorderLevel = 10, description = "Fresh strawberry flavor.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Mango Malai", sku = "IK-007", category = "Fruit", costPrice = 24.17, sellingPrice = 40.0, currentStock = 0, reorderLevel = 10, description = "Mango with creamy finish.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Dry Fruit", sku = "IK-008", category = "Premium", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 10, description = "Loaded dry fruit kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Rose", sku = "IK-009", category = "Special", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 8, description = "Rose essence kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Blackcurrant", sku = "IK-010", category = "Special", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 8, description = "Tangy blackcurrant kulfi.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Caramel Coffee", sku = "IK-011", category = "Special", costPrice = 26.67, sellingPrice = 45.0, currentStock = 0, reorderLevel = 8, description = "Coffee and caramel fusion.", createdAt = now, updatedAt = now),
            ProductEntity(name = "Paan", sku = "IK-012", category = "Signature", costPrice = 26.67, sellingPrice = 50.0, currentStock = 0, reorderLevel = 8, description = "Popular paan kulfi.", createdAt = now, updatedAt = now),
        )
    }
}
