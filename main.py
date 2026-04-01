from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Products Catalog API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Проверка уникальности имени
    existing = crud.get_product_by_name(db, product.name)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    return crud.create_product(db, product)

@app.get("/products", response_model=list[schemas.Product])
def list_products(
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Валидация min_price <= max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price must be <= max_price")
    
    return crud.get_products(db, skip=skip, limit=limit, 
                            min_price=min_price, max_price=max_price, in_stock=in_stock)

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    # Проверка существования продукта
    existing = crud.get_product(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверка уникальности имени при обновлении
    name_taken = crud.get_product_by_name(db, product.name)
    if name_taken and name_taken.id != product_id:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    updated = crud.update_product(db, product_id, product)
    return updated

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return None