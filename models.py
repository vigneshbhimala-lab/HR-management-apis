from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String)
    dob = Column(String)
    gender = Column(String)
    nationality = Column(String)
    education = Column(String)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    company_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    gst_number = Column(String)

    invoices = relationship("Invoice", back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    invoice_number = Column(String, unique=True, index=True)
    invoice_date = Column(String)
    description = Column(String)
    amount = Column(Float)
    gst_percent = Column(Float)
    gst_amount = Column(Float)
    total_amount = Column(Float)
    status = Column(String)

    client = relationship("Client", back_populates="invoices")
