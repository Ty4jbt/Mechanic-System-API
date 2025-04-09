from datetime import date
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanic = db.Table(
    'service_mechanic',
    Base.metadata,
    db.Column('mechanic_id', db.ForeignKey('mechanics.id')),
    db.Column('ticket_id', db.ForeignKey('service_tickets.id'))
)

service_inventory = db.Table(
    'service_inventory',
    Base.metadata,
    db.Column('inventory_id', db.ForeignKey('inventory.id')),
    db.Column('ticket_id', db.ForeignKey('service_tickets.id'))
)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates='customer', cascade='all, delete')

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)
    date_created: Mapped[date]
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    VIN: Mapped[str] = mapped_column(db.String(20), nullable=False)
    total_cost: Mapped[float] = mapped_column(db.Float(), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates='service_tickets')
    inventory_items: Mapped[List["Inventory"]] = db.relationship(secondary=service_inventory, back_populates='service_tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates='mechanics', cascade='all, delete')
    orders: Mapped[List["Order"]] = db.relationship(back_populates='mechanic', cascade='all, delete')

class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(db.Integer, default=0)

    order_items: Mapped[List["OrderItems"]] = db.relationship(back_populates='inventory_item')
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_inventory, back_populates='inventory_items')

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(nullable=False)
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey('mechanics.id'), nullable=False)
    total_cost: Mapped[float] = mapped_column(db.Float(), nullable=False)

    mechanic: Mapped["Mechanic"] = db.relationship(back_populates='orders')
    order_items: Mapped[List["OrderItems"]] = db.relationship(back_populates='order')

class OrderItems(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(db.ForeignKey('orders.id'), nullable=False)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    order: Mapped["Order"] = db.relationship(back_populates='order_items')    
    inventory_item: Mapped["Inventory"] = db.relationship(back_populates='order_items')

class ServiceInventoryQuantity(Base):
    __tablename__ = 'service_inventory_quantity'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=False)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    service_ticket: Mapped["ServiceTicket"] = db.relationship()
    inventory_item: Mapped["Inventory"] = db.relationship()