from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import products, inventory, sales, categories

app = FastAPI(
    title="E-Commerce Admin Dashboard API",
    description="API for e-commerce admin dashboard with sales analytics and inventory management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["Products"])

app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])

app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])

app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the E-Commerce Admin Dashboard API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
