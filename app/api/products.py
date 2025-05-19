from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import Product as ProductModel
from app.schemas.schemas import Product, ProductCreate, ProductUpdate

router = APIRouter()

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.sku == product.sku).first()
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU {product.sku} already exists"
        )
    
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[Product])
def list_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None, 
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)
    
    if category_id is not None:
        query = query.filter(ProductModel.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(ProductModel.is_active == is_active)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=Product)
def retrieve_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found"
        )
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found"
        )
    
    if product.sku is not None and product.sku != db_product.sku:
        sku_exists = db.query(ProductModel).filter(
            ProductModel.sku == product.sku, 
            ProductModel.id != product_id
        ).first()
        if sku_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU {product.sku} already exists"
            )
    
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    db.delete(db_product)
    db.commit()
    return None 