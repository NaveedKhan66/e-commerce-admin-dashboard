# Database Schema Documentation

## Overview

The database schema for the E-Commerce Admin Dashboard uses PostgreSQL and is designed to efficiently support all required operations for sales analysis, inventory management, and product registration.

## Tables

### Categories

Stores product categories.

| Column     | Type         | Constraints  | Description               |
|------------|--------------|--------------|---------------------------|
| id         | INTEGER      | PK           | Unique identifier         |
| name       | VARCHAR(100) | NOT NULL     | Category name             |
| description| TEXT         |              | Category description      |
| created_at | TIMESTAMP    | NOT NULL     | Record creation timestamp |
| updated_at | TIMESTAMP    | NOT NULL     | Record update timestamp   |

### Products

Stores product information.

| Column       | Type         | Constraints     | Description                |
|--------------|--------------|-----------------|----------------------------|
| id           | INTEGER      | PK              | Unique identifier          |
| name         | VARCHAR(200) | NOT NULL        | Product name               |
| description  | TEXT         |                 | Product description        |
| price        | DECIMAL(10,2)| NOT NULL        | Product price              |
| category_id  | INTEGER      | FK → Categories | Associated category        |
| sku          | VARCHAR(50)  | NOT NULL, UNIQUE| Stock keeping unit         |
| image_url    | VARCHAR(255) |                 | Product image URL          |
| is_active    | BOOLEAN      | NOT NULL        | Product availability status|
| created_at   | TIMESTAMP    | NOT NULL        | Record creation timestamp  |
| updated_at   | TIMESTAMP    | NOT NULL        | Record update timestamp    |

### Inventory

Tracks current inventory levels.

| Column       | Type      | Constraints    | Description                |
|--------------|-----------|----------------|----------------------------|
| id           | INTEGER   | PK             | Unique identifier          |
| product_id   | INTEGER   | FK → Products  | Associated product         |
| quantity     | INTEGER   | NOT NULL       | Current quantity in stock  |
| low_stock_threshold | INTEGER | NOT NULL  | Low stock alert threshold  |
| created_at   | TIMESTAMP | NOT NULL       | Record creation timestamp  |
| updated_at   | TIMESTAMP | NOT NULL       | Record update timestamp    |

### Inventory History

Records inventory changes over time.

| Column       | Type      | Constraints    | Description                |
|--------------|-----------|----------------|----------------------------|
| id           | INTEGER   | PK             | Unique identifier          |
| product_id   | INTEGER   | FK → Products  | Associated product         |
| quantity_change | INTEGER | NOT NULL      | Change in quantity         |
| new_quantity | INTEGER   | NOT NULL       | New inventory quantity     |
| change_reason | VARCHAR(100) | NOT NULL   | Reason for change          |
| change_timestamp | TIMESTAMP | NOT NULL   | When the change occurred   |
| changed_by   | VARCHAR(100) | NOT NULL    | User who made the change   |

### Sales

Records sales data.

| Column       | Type          | Constraints    | Description                |
|--------------|---------------|----------------|----------------------------|
| id           | INTEGER       | PK             | Unique identifier          |
| order_id     | VARCHAR(50)   | NOT NULL       | External order identifier  |
| product_id   | INTEGER       | FK → Products  | Associated product         |
| quantity     | INTEGER       | NOT NULL       | Quantity sold              |
| unit_price   | DECIMAL(10,2) | NOT NULL       | Price at time of sale      |
| total_price  | DECIMAL(10,2) | NOT NULL       | Total price for this item  |
| customer_id  | VARCHAR(100)  |                | Customer identifier        |
| sales_date   | DATE          | NOT NULL       | Date of sale               |
| platform     | VARCHAR(50)   |                | Sales platform (e.g., Amazon) |
| created_at   | TIMESTAMP     | NOT NULL       | Record creation timestamp  |

## Indexes

- `products_sku_idx`: Index on `Products.sku` for quick lookups
- `sales_date_idx`: Index on `Sales.sales_date` for fast date filtering
- `sales_product_id_idx`: Index on `Sales.product_id` for product-based filtering
- `inventory_product_id_idx`: Index on `Inventory.product_id` for quick inventory lookups

## Relationships

1. **Products → Categories**: Many-to-one relationship (many products can belong to one category)
2. **Inventory → Products**: One-to-one relationship (each product has one inventory record)
3. **Inventory History → Products**: Many-to-one relationship (many history records for one product)
4. **Sales → Products**: Many-to-one relationship (many sales for one product)

## Database Functions and Triggers

1. **update_inventory_trigger**: Updates inventory when a sale is recorded
2. **update_inventory_history_trigger**: Adds a record to inventory history when inventory changes
3. **update_timestamps_trigger**: Automatically updates the `updated_at` column when a record is modified 