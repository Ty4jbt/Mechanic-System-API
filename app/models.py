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

    customer: Mapped["Customer"] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates='service_tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(150), unique=True)
    phone: Mapped[str] = mapped_column(db.String(20))
    salary: Mapped[float] = mapped_column(db.Float)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic)