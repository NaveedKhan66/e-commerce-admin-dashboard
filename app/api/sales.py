from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, cast, Integer, Numeric, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.db.database import get_db
from app.models.models import Sale as SaleModel, Product as ProductModel
from app.schemas.schemas import (
    Sale,
    SaleCreate,
    SalesFilter,
    DateRangeFilter,
    RevenueComparison,
)
from app.schemas.schemas import RevenueData, RevenueResponse, RevenueComparisonResponse

router = APIRouter()


@router.post("/", response_model=Sale, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == sale.product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found",
        )

    db_sale = SaleModel(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[Sale])
def list_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sales = (
        db.query(SaleModel)
        .options(joinedload(SaleModel.product))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return sales


@router.get("/filter", response_model=List[Sale])
def filter_sales(
    start_date: date = Query(..., description="Start date for filtering sales"),
    end_date: date = Query(..., description="End date for filtering sales"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Filter sales by date range, product, category, or platform
    """
    query = db.query(SaleModel).options(joinedload(SaleModel.product))

    query = query.filter(
        SaleModel.sales_date >= start_date, SaleModel.sales_date <= end_date
    )
    
    if product_id is not None:
        query = query.filter(SaleModel.product_id == product_id)

    if category_id is not None:
        query = query.join(ProductModel).filter(ProductModel.category_id == category_id)
        
    if platform is not None:
        query = query.filter(SaleModel.platform == platform)

    sales = query.order_by(SaleModel.sales_date.desc()).offset(skip).limit(limit).all()
    return sales


@router.get("/revenue/daily", response_model=RevenueResponse)
def get_daily_revenue(
    start_date: date = Query(..., description="Start date for revenue calculation"),
    end_date: date = Query(..., description="End date for revenue calculation"),
    db: Session = Depends(get_db),
):
    revenue_data = (
        db.query(
            SaleModel.sales_date.label("date"),
            func.sum(SaleModel.total_price).label("revenue"),
        )
        .filter(SaleModel.sales_date >= start_date, SaleModel.sales_date <= end_date)
        .group_by(SaleModel.sales_date)
        .order_by(SaleModel.sales_date)
        .all()
    )
    result = [
        RevenueData(date=item.date, revenue=item.revenue) for item in revenue_data
    ]
    total_revenue = sum(item.revenue for item in result)

    return RevenueResponse(data=result, total_revenue=total_revenue)


@router.get("/revenue/weekly", response_model=RevenueResponse)
def get_weekly_revenue(
    start_date: date = Query(..., description="Start date for revenue calculation"),
    end_date: date = Query(..., description="End date for revenue calculation"),
    db: Session = Depends(get_db),
):
    revenue_data = (
        db.query(
            extract("year", SaleModel.sales_date).label("year"),
            extract("week", SaleModel.sales_date).label("week"),
            func.min(SaleModel.sales_date).label(
                "date"
            ),  # Use first day of week as date
            func.sum(SaleModel.total_price).label("revenue"),
        )
        .filter(SaleModel.sales_date >= start_date, SaleModel.sales_date <= end_date)
        .group_by(
            extract("year", SaleModel.sales_date), extract("week", SaleModel.sales_date)
        )
        .order_by(
            extract("year", SaleModel.sales_date), extract("week", SaleModel.sales_date)
        )
        .all()
    )
    result = [
        RevenueData(date=item.date, revenue=item.revenue) for item in revenue_data
    ]

    total_revenue = sum(item.revenue for item in result)

    return RevenueResponse(data=result, total_revenue=total_revenue)


@router.get("/revenue/monthly", response_model=RevenueResponse)
def get_monthly_revenue(
    start_date: date = Query(..., description="Start date for revenue calculation"),
    end_date: date = Query(..., description="End date for revenue calculation"),
    db: Session = Depends(get_db),
):
    revenue_data = (
        db.query(
            extract("year", SaleModel.sales_date).label("year"),
            extract("month", SaleModel.sales_date).label("month"),
            func.min(SaleModel.sales_date).label(
                "date"
            ),  # Use first day of month as date
            func.sum(SaleModel.total_price).label("revenue"),
        )
        .filter(SaleModel.sales_date >= start_date, SaleModel.sales_date <= end_date)
        .group_by(
            extract("year", SaleModel.sales_date),
            extract("month", SaleModel.sales_date),
        )
        .order_by(
            extract("year", SaleModel.sales_date),
            extract("month", SaleModel.sales_date),
        )
        .all()
    )
    result = [
        RevenueData(date=item.date, revenue=item.revenue) for item in revenue_data
    ]
    total_revenue = sum(item.revenue for item in result)

    return RevenueResponse(data=result, total_revenue=total_revenue)


@router.get("/revenue/yearly", response_model=RevenueResponse)
def get_yearly_revenue(
    start_date: date = Query(..., description="Start date for revenue calculation"),
    end_date: date = Query(..., description="End date for revenue calculation"),
    db: Session = Depends(get_db),
):
    revenue_data = (
        db.query(
            extract("year", SaleModel.sales_date).label("year"),
            func.make_date(
                cast(extract("year", SaleModel.sales_date), Integer), 1, 1
            ).label(
                "date"
            ), 
            func.sum(SaleModel.total_price).label("revenue"),
        )
        .filter(SaleModel.sales_date >= start_date, SaleModel.sales_date <= end_date)
        .group_by(extract("year", SaleModel.sales_date))
        .order_by(extract("year", SaleModel.sales_date))
        .all()
    )
    result = [
        RevenueData(date=item.date, revenue=item.revenue) for item in revenue_data
    ]
    total_revenue = sum(item.revenue for item in result)

    return RevenueResponse(data=result, total_revenue=total_revenue)


@router.post("/revenue/compare", response_model=RevenueComparisonResponse)
def compare_revenue(comparison: RevenueComparison, db: Session = Depends(get_db)):
    """
    Compare revenue between two periods
    """
    query = db.query(func.sum(SaleModel.total_price).label("revenue"))

    if comparison.category_id is not None:
        query = query.join(ProductModel).filter(
            ProductModel.category_id == comparison.category_id
        )

    period1_revenue = query.filter(
        SaleModel.sales_date >= comparison.period1_start,
        SaleModel.sales_date <= comparison.period1_end,
    ).scalar() or Decimal("0.0")

    period2_revenue = query.filter(
        SaleModel.sales_date >= comparison.period2_start,
        SaleModel.sales_date <= comparison.period2_end,
    ).scalar() or Decimal("0.0")

    if period1_revenue == 0:
        percentage_change = Decimal("100.0") if period2_revenue > 0 else Decimal("0.0")
    else:
        percentage_change = (
            (period2_revenue - period1_revenue) / period1_revenue
        ) * 100

    period1_days = (comparison.period1_end - comparison.period1_start).days + 1
    period2_days = (comparison.period2_end - comparison.period2_start).days + 1

    return RevenueComparisonResponse(
        period1={
            "start_date": comparison.period1_start,
            "end_date": comparison.period1_end,
            "revenue": period1_revenue,
            "days": period1_days,
            "daily_avg": (
                period1_revenue / period1_days if period1_days > 0 else Decimal("0.0")
            ),
        },
        period2={
            "start_date": comparison.period2_start,
            "end_date": comparison.period2_end,
            "revenue": period2_revenue,
            "days": period2_days,
            "daily_avg": (
                period2_revenue / period2_days if period2_days > 0 else Decimal("0.0")
            ),
        },
        percentage_change=percentage_change,
    )
