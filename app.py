"""Kurgusal demo proje / Fictional demo project: SQLite inventory REST API."""
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
import os
import sqlite3

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    price_cents: int = Field(ge=0, le=100_000_000, strict=True)
    stock: int = Field(ge=0, le=1_000_000, strict=True)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank / Ad boş olamaz")
        return value


class ProductPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price_cents: int | None = Field(default=None, ge=0, le=100_000_000, strict=True)
    stock: int | None = Field(default=None, ge=0, le=1_000_000, strict=True)


class Product(ProductInput):
    id: int


def create_app(database: str | Path | None = None):
    db_path = Path(database or os.getenv("DATABASE_PATH", "data/inventory.sqlite"))

    @contextmanager
    def connection():
        db = sqlite3.connect(db_path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @asynccontextmanager
    async def lifespan(_):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0))""")
        yield

    api = FastAPI(title="Demo Inventory API / Demo Stok API", version="1.0.0", lifespan=lifespan,
                  description="Kurgusal demo proje / Fictional demo project. Prices are TRY cents / Fiyatlar TL kuruşudur.")

    @api.get("/health")
    def health():
        with connection() as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ok"}

    @api.get("/products", response_model=list[Product])
    def list_products(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
        with connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?", (limit, offset))]

    @api.get("/summary")
    def summary():
        with connection() as db:
            row = db.execute("SELECT COUNT(*) AS products, COALESCE(SUM(stock), 0) AS units, COALESCE(SUM(price_cents * stock), 0) AS value_cents FROM products").fetchone()
            return {**dict(row), "currency": "TRY"}

    @api.post("/products", response_model=Product, status_code=201)
    def add_product(product: ProductInput):
        with connection() as db:
            cursor = db.execute("INSERT INTO products (name, price_cents, stock) VALUES (?, ?, ?)",
                                (product.name, product.price_cents, product.stock))
            return {"id": cursor.lastrowid, **product.model_dump()}

    @api.get("/products/{product_id}", response_model=Product)
    def get_product(product_id: int):
        with connection() as db:
            row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Product not found / Ürün bulunamadı")
            return dict(row)

    @api.patch("/products/{product_id}", response_model=Product)
    def update_product(product_id: int, patch: ProductPatch):
        changes = patch.model_dump(exclude_unset=True)
        if not changes or any(value is None for value in changes.values()):
            raise HTTPException(422, "Non-null changes required / Boş olmayan değişiklik gerekir")
        current = get_product(product_id)
        try:
            updated = ProductInput.model_validate({**{key:current[key] for key in ("name", "price_cents", "stock")}, **changes})
        except ValueError:
            raise HTTPException(422, "Invalid product / Geçersiz ürün") from None
        with connection() as db:
            db.execute("UPDATE products SET name = ?, price_cents = ?, stock = ? WHERE id = ?",
                       (updated.name, updated.price_cents, updated.stock, product_id))
            return {"id": product_id, **updated.model_dump()}

    @api.delete("/products/{product_id}", status_code=204)
    def delete_product(product_id: int):
        with connection() as db:
            cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            if not cursor.rowcount:
                raise HTTPException(404, "Product not found / Ürün bulunamadı")
        return Response(status_code=204)

    return api


app = create_app()
