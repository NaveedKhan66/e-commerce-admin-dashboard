import os
import sys
import csv
from datetime import datetime, timedelta, date
import random
from decimal import Decimal
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import Category, Product, Inventory, InventoryHistory, Sale

Base.metadata.create_all(bind=engine)

CATEGORIES = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Home & Kitchen", "description": "Home appliances and kitchen supplies"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Books", "description": "Books, eBooks, and publications"},
    {"name": "Toys & Games", "description": "Toys, games, and entertainment items"}
]

PRODUCTS = [
    {"name": "Smartphone X", "description": "Latest smartphone with advanced features", "price": 799.99, "category_id": 1, "sku": "EL-PHONE-001", "image_url": "https://example.com/smartphone.jpg"},
    {"name": "Laptop Pro", "description": "High-performance laptop for professionals", "price": 1299.99, "category_id": 1, "sku": "EL-LAPT-001", "image_url": "https://example.com/laptop.jpg"},
    {"name": "Wireless Headphones", "description": "Noise-cancelling wireless headphones", "price": 149.99, "category_id": 1, "sku": "EL-HEAD-001", "image_url": "https://example.com/headphones.jpg"},
    {"name": "Smart Watch", "description": "Fitness and health tracking smart watch", "price": 249.99, "category_id": 1, "sku": "EL-WATC-001", "image_url": "https://example.com/smartwatch.jpg"},
    {"name": "Bluetooth Speaker", "description": "Portable Bluetooth speaker with deep bass", "price": 79.99, "category_id": 1, "sku": "EL-SPKR-001", "image_url": "https://example.com/speaker.jpg"},

    {"name": "Coffee Maker", "description": "Programmable coffee maker with timer", "price": 89.99, "category_id": 2, "sku": "HK-COFF-001", "image_url": "https://example.com/coffeemaker.jpg"},
    {"name": "Blender", "description": "High-speed blender for smoothies and more", "price": 69.99, "category_id": 2, "sku": "HK-BLND-001", "image_url": "https://example.com/blender.jpg"},
    {"name": "Toaster Oven", "description": "Multi-function toaster oven and air fryer", "price": 119.99, "category_id": 2, "sku": "HK-TSTR-001", "image_url": "https://example.com/toasteroven.jpg"},
    {"name": "Knife Set", "description": "Professional chef knife set", "price": 129.99, "category_id": 2, "sku": "HK-KNIF-001", "image_url": "https://example.com/knifeset.jpg"},
    {"name": "Food Storage Containers", "description": "Set of 10 food storage containers", "price": 24.99, "category_id": 2, "sku": "HK-STOR-001", "image_url": "https://example.com/containers.jpg"},
    
    {"name": "Men's T-Shirt", "description": "Cotton crew neck t-shirt", "price": 19.99, "category_id": 3, "sku": "CL-MTSH-001", "image_url": "https://example.com/menshirt.jpg"},
    {"name": "Women's Jeans", "description": "Slim fit women's jeans", "price": 49.99, "category_id": 3, "sku": "CL-WJNS-001", "image_url": "https://example.com/womenjeans.jpg"},
    {"name": "Running Shoes", "description": "Performance running shoes", "price": 89.99, "category_id": 3, "sku": "CL-SHOE-001", "image_url": "https://example.com/shoes.jpg"},
    {"name": "Winter Jacket", "description": "Warm winter jacket with hood", "price": 129.99, "category_id": 3, "sku": "CL-JACK-001", "image_url": "https://example.com/jacket.jpg"},
    {"name": "Sun Hat", "description": "Summer sun hat for UV protection", "price": 24.99, "category_id": 3, "sku": "CL-HAT-001", "image_url": "https://example.com/hat.jpg"},
    
    {"name": "Bestseller Novel", "description": "Latest bestselling fiction novel", "price": 14.99, "category_id": 4, "sku": "BK-NOVL-001", "image_url": "https://example.com/novel.jpg"},
    {"name": "Cookbook", "description": "International cuisine cookbook", "price": 29.99, "category_id": 4, "sku": "BK-COOK-001", "image_url": "https://example.com/cookbook.jpg"},
    {"name": "Self-Help Book", "description": "Popular self-improvement book", "price": 12.99, "category_id": 4, "sku": "BK-SELF-001", "image_url": "https://example.com/selfhelp.jpg"},
    {"name": "Travel Guide", "description": "Comprehensive travel guide", "price": 24.99, "category_id": 4, "sku": "BK-TRVL-001", "image_url": "https://example.com/travelguide.jpg"},
    {"name": "Children's Book", "description": "Illustrated children's book", "price": 9.99, "category_id": 4, "sku": "BK-CHLD-001", "image_url": "https://example.com/childrensbook.jpg"},
    
    {"name": "Board Game", "description": "Family board game", "price": 34.99, "category_id": 5, "sku": "TG-BORD-001", "image_url": "https://example.com/boardgame.jpg"},
    {"name": "Action Figure", "description": "Collectible action figure", "price": 19.99, "category_id": 5, "sku": "TG-ACTN-001", "image_url": "https://example.com/actionfigure.jpg"},
    {"name": "LEGO Set", "description": "LEGO building set", "price": 49.99, "category_id": 5, "sku": "TG-LEGO-001", "image_url": "https://example.com/lego.jpg"},
    {"name": "Plush Toy", "description": "Soft plush animal toy", "price": 14.99, "category_id": 5, "sku": "TG-PLSH-001", "image_url": "https://example.com/plush.jpg"},
    {"name": "Puzzle", "description": "1000-piece jigsaw puzzle", "price": 19.99, "category_id": 5, "sku": "TG-PZZL-001", "image_url": "https://example.com/puzzle.jpg"}
]

PLATFORMS = ["Amazon", "Walmart", "Company Website", "Retail Store"]

def generate_sales_data(db: Session, start_date: date, end_date: date, num_sales: int):
    """Generate random sales data for a date range"""
    products = db.query(Product).all()
    if not products:
        print("No products found. Please ensure products are loaded first.")
        return
    
    date_range = (end_date - start_date).days
    sales = []
    
    order_id_base = 100000
    
    for _ in range(num_sales):
        product = random.choice(products)
        sale_date = start_date + timedelta(days=random.randint(0, date_range))
        quantity = random.randint(1, 5)
        unit_price = product.price
        total_price = unit_price * quantity
        platform = random.choice(PLATFORMS)
        order_id = f"ORD-{order_id_base + _}"
        
        sale = Sale(
            order_id=order_id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            customer_id=f"CUST-{random.randint(1000, 9999)}",
            sales_date=sale_date,
            platform=platform
        )
        sales.append(sale)
    
    db.add_all(sales)
    db.commit()
    print(f"Generated {num_sales} sales records")

def generate_inventory_data(db: Session):
    """Generate inventory data for products"""
    products = db.query(Product).all()
    inventory_records = []
    inventory_history_records = []
    
    for product in products:
        quantity = random.randint(10, 100)
        threshold = random.randint(5, 20)
        
        inventory = Inventory(
            product_id=product.id,
            quantity=quantity,
            low_stock_threshold=threshold
        )
        inventory_records.append(inventory)
        
        history = InventoryHistory(
            product_id=product.id,
            quantity_change=quantity,
            new_quantity=quantity,
            change_reason="Initial stock",
            changed_by="System"
        )
        inventory_history_records.append(history)
    
    db.add_all(inventory_records)
    db.add_all(inventory_history_records)
    db.commit()
    print(f"Generated inventory records for {len(products)} products")

def load_demo_data():
    """Load all demo data into the database"""
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            print("Database already contains data. Skipping demo data loading.")
            return
        
        categories = [Category(**category) for category in CATEGORIES]
        db.add_all(categories)
        db.commit()
        print(f"Added {len(categories)} categories")
    
        products = [Product(**product) for product in PRODUCTS]
        db.add_all(products)
        db.commit()
        print(f"Added {len(products)} products")
        
        generate_inventory_data(db)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        generate_sales_data(db, start_date, end_date, 1000)
        
    except Exception as e:
        print(f"Error loading demo data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Loading demo data...")
    load_demo_data()
    print("Demo data load complete!") 