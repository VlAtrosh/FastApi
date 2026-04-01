import database
import schemas

def get_product(product_id: int):
    """Получить продукт по ID"""
    with database.get_connection() as conn:
        result = conn.execute(
            "SELECT id, name, price, in_stock FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        return dict(result) if result else None

def get_product_by_name(name: str):
    """Получить продукт по имени"""
    with database.get_connection() as conn:
        result = conn.execute(
            "SELECT id, name, price, in_stock FROM products WHERE name = ?",
            (name,)
        ).fetchone()
        return dict(result) if result else None

def get_products(min_price: int = None, max_price: int = None, 
                 in_stock: bool = None, skip: int = 0, limit: int = 100):
    """Получить список продуктов с фильтрацией"""
    with database.get_connection() as conn:
        query = "SELECT id, name, price, in_stock FROM products WHERE 1=1"
        params = []
        
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        
        if in_stock is not None:
            query += " AND in_stock = ?"
            params.append(1 if in_stock else 0)
        
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        results = conn.execute(query, params).fetchall()
        return [dict(row) for row in results]

def create_product(product: schemas.ProductCreate):
    """Создать новый продукт"""
    with database.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO products (name, price, in_stock) VALUES (?, ?, ?)",
            (product.name, product.price, 1 if product.in_stock else 0)
        )
        conn.commit()
        
        # Получить созданный продукт
        return get_product(cursor.lastrowid)

def update_product(product_id: int, product: schemas.ProductUpdate):
    """Обновить продукт"""
    with database.get_connection() as conn:
        conn.execute(
            "UPDATE products SET name = ?, price = ?, in_stock = ? WHERE id = ?",
            (product.name, product.price, 1 if product.in_stock else 0, product_id)
        )
        conn.commit()
        
        # Получить обновленный продукт
        return get_product(product_id)

def delete_product(product_id: int):
    """Удалить продукт"""
    with database.get_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
