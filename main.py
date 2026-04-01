from fastapi import FastAPI, HTTPException, Query, status
from typing import Optional

import crud, schemas, database  # Убрали точки

# Инициализация базы данных
database.init_db()

app = FastAPI(title="Products Catalog API")

@app.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate):
    """Создать новый продукт"""
    # Проверка уникальности имени
    existing = crud.get_product_by_name(product.name)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    result = crud.create_product(product)
    return result

@app.get("/products", response_model=list[schemas.Product])
def list_products(
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Получить список продуктов с фильтрацией"""
    # Валидация min_price <= max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price must be <= max_price")
    
    return crud.get_products(
        min_price=min_price, 
        max_price=max_price, 
        in_stock=in_stock,
        skip=skip, 
        limit=limit
    )

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int):
    """Получить продукт по ID"""
    product = crud.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate):
    """Полное обновление продукта"""
    # Проверка существования продукта
    existing = crud.get_product(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверка уникальности имени при обновлении
    name_taken = crud.get_product_by_name(product.name)
    if name_taken and name_taken["id"] != product_id:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    updated = crud.update_product(product_id, product)
    return updated

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    """Удалить продукт"""
    if not crud.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return None
