from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category_id: Optional[int] = None
    sku: str
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(..., ge=0)

class InventoryCreate(InventoryBase):
    product_id: int

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)

class Inventory(InventoryBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

# Inventory History Schemas
class InventoryHistoryBase(BaseModel):
    product_id: int
    quantity_change: int
    new_quantity: int
    change_reason: str
    changed_by: str

class InventoryHistoryCreate(InventoryHistoryBase):
    pass

class InventoryHistory(InventoryHistoryBase):
    id: int
    change_timestamp: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

# Sale Schemas
class SaleBase(BaseModel):
    order_id: str
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)
    customer_id: Optional[str] = None
    sales_date: date
    platform: Optional[str] = None

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    created_at: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

# Filter Schemas
class DateRangeFilter(BaseModel):
    start_date: date
    end_date: date

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SalesFilter(DateRangeFilter):
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    platform: Optional[str] = None

class RevenueComparison(BaseModel):
    period1_start: date
    period1_end: date
    period2_start: date
    period2_end: date
    category_id: Optional[int] = None

    @validator('period1_end')
    def period1_end_must_be_after_period1_start(cls, v, values):
        if 'period1_start' in values and v < values['period1_start']:
            raise ValueError('period1_end must be after period1_start')
        return v

    @validator('period2_end')
    def period2_end_must_be_after_period2_start(cls, v, values):
        if 'period2_start' in values and v < values['period2_start']:
            raise ValueError('period2_end must be after period2_start')
        return v

# Response Models
class RevenueData(BaseModel):
    date: date
    revenue: Decimal

class RevenueResponse(BaseModel):
    data: List[RevenueData]
    total_revenue: Decimal

class RevenueComparisonResponse(BaseModel):
    period1: Dict[str, Any]
    period2: Dict[str, Any]
    percentage_change: Decimal

class InventoryStatus(BaseModel):
    product: Product
    quantity: int
    low_stock_threshold: int
    is_low_stock: bool

class LowStockResponse(BaseModel):
    low_stock_items: List[InventoryStatus]
    total_count: int 