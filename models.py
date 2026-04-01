from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)  # можно использовать Numeric для decimal
    in_stock = Column(Boolean, default=True)