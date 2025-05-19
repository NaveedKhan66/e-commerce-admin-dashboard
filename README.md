# E-Commerce Admin Dashboard API

Backend API for an e-commerce admin dashboard providing sales analytics, inventory management, and product registration capabilities.

## Features

1. **Sales Status**
   - Retrieve, filter, and analyze sales data
   - Revenue analysis by day, week, month, and year
   - Compare revenue across different periods and categories
   - Sales data filtering by date range, product, and category

2. **Inventory Management**
   - View current inventory status with low stock alerts
   - Update inventory levels
   - Track inventory changes over time

3. **Product Management**
   - Register new products
   - Update product information

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd e-commerce-admin-dashboard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/ecommerce_dashboard
   ```

5. Initialize the database:
   ```
   alembic upgrade head
   ```

6. Load demo data:
   ```
   python scripts/load_demo_data.py
   ```

7. Start the API server:
   ```
   uvicorn app.main:app --reload
   ```

8. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Sales Status

- `GET /api/sales`: Get all sales records
- `GET /api/sales/filter`: Filter sales by date range, product, or category
- `GET /api/revenue/daily`: Get daily revenue
- `GET /api/revenue/weekly`: Get weekly revenue
- `GET /api/revenue/monthly`: Get monthly revenue
- `GET /api/revenue/yearly`: Get yearly revenue
- `POST /api/revenue/compare`: Compare revenue between two periods

### Inventory Management

- `GET /api/inventory`: Get current inventory status
- `GET /api/inventory/low-stock`: Get products with low stock
- `PUT /api/inventory/{product_id}`: Update inventory level
- `GET /api/inventory/history/{product_id}`: Get inventory history for a product

### Product Management

- `POST /api/products`: Register a new product
- `GET /api/products`: Get all products
- `GET /api/products/{product_id}`: Get a specific product
- `PUT /api/products/{product_id}`: Update a product
- `DELETE /api/products/{product_id}`: Delete a product

## Database Schema

The database consists of the following tables:

- **products**: Stores product information
- **inventory**: Tracks current inventory levels
- **inventory_history**: Records inventory changes
- **sales**: Records sales data
- **categories**: Product categories

For detailed schema information, see the `DATABASE.md` file. 