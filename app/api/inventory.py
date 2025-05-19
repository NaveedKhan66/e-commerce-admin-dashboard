from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.database import get_db
from app.models.models import Inventory as InventoryModel, InventoryHistory as InventoryHistoryModel, Product as ProductModel
from app.schemas.schemas import Inventory, InventoryUpdate, InventoryHistory, InventoryStatus, LowStockResponse

router = APIRouter()

@router.get("/", response_model=List[Inventory])
def list_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory = db.query(InventoryModel).options(
        joinedload(InventoryModel.product)
    ).offset(skip).limit(limit).all()
    return inventory


@router.get("/status", response_model=List[InventoryStatus])
def list_inventory_status(db: Session = Depends(get_db)):
    inventory_items = db.query(InventoryModel).options(
        joinedload(InventoryModel.product)
    ).all()
    
    result = []
    for item in inventory_items:
        result.append(
            InventoryStatus(
                product=item.product,
                quantity=item.quantity,
                low_stock_threshold=item.low_stock_threshold,
                is_low_stock=item.quantity <= item.low_stock_threshold
            )
        )
    
    return result


@router.get("/low-stock", response_model=LowStockResponse)
def get_low_stock(db: Session = Depends(get_db)):
    """
    Get products with low stock (where quantity <= low_stock_threshold)
    """
    
    inventory_items = db.query(InventoryModel).options(
        joinedload(InventoryModel.product)
    ).filter(
        InventoryModel.quantity <= InventoryModel.low_stock_threshold
    ).all()
    
    low_stock_items = []
    for item in inventory_items:
        low_stock_items.append(
            InventoryStatus(
                product=item.product,
                quantity=item.quantity,
                low_stock_threshold=item.low_stock_threshold,
                is_low_stock=True
            )
        )
    
    return LowStockResponse(
        low_stock_items=low_stock_items,
        total_count=len(low_stock_items)
    )


@router.get("/{product_id}", response_model=Inventory)
def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = db.query(InventoryModel).filter(
        InventoryModel.product_id == product_id
    ).options(
        joinedload(InventoryModel.product)
    ).first()
    
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory not found"
        )
    
    return inventory


@router.put("/{product_id}", response_model=Inventory)
def update_inventory(
    product_id: int, 
    inventory_update: InventoryUpdate,
    changed_by: str = Body(...),
    change_reason: str = Body(...),
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found"
        )
    
    inventory = db.query(InventoryModel).filter(InventoryModel.product_id == product_id).first()
    if inventory is None:
        # Create inventory if it doesn't exist
        inventory = InventoryModel(
            product_id=product_id,
            quantity=inventory_update.quantity or 0,
            low_stock_threshold=inventory_update.low_stock_threshold or 10
        )
        db.add(inventory)
    else:
        update_data = inventory_update.model_dump(exclude_unset=True)
        
        # Save old quantity for history
        old_quantity = inventory.quantity
        
        for key, value in update_data.items():
            setattr(inventory, key, value)
    
        if 'quantity' in update_data and old_quantity != inventory.quantity:
            history = InventoryHistoryModel(
                product_id=product_id,
                quantity_change=inventory.quantity - old_quantity,
                new_quantity=inventory.quantity,
                change_reason=change_reason,
                changed_by=changed_by
            )
            db.add(history)
    
    db.commit()
    db.refresh(inventory)
    return inventory


@router.get("/history/{product_id}", response_model=List[InventoryHistory])
def get_inventory_history(
    product_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found"
        )

    history = db.query(InventoryHistoryModel).filter(
        InventoryHistoryModel.product_id == product_id
    ).order_by(
        InventoryHistoryModel.change_timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return history 