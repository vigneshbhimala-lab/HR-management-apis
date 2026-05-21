from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Client, Invoice


router = APIRouter(prefix="/invoices", tags=["invoices"])


def calculate_invoice_totals(amount: float, gst_percent: float):
    gst_amount = round(amount * gst_percent / 100, 2)
    total_amount = round(amount + gst_amount, 2)

    return gst_amount, total_amount


@router.post("")
def create_invoice(
    client_id: int,
    invoice_number: str,
    invoice_date: str,
    description: str,
    amount: float,
    gst_percent: float,
    status: str = "unpaid",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    existing_invoice = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number
    ).first()

    if existing_invoice:
        raise HTTPException(status_code=400, detail="Invoice number already exists")

    gst_amount, total_amount = calculate_invoice_totals(amount, gst_percent)

    invoice = Invoice(
        client_id=client_id,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        description=description,
        amount=amount,
        gst_percent=gst_percent,
        gst_amount=gst_amount,
        total_amount=total_amount,
        status=status
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    

    return {
        "message": "Invoice created successfully",
        "invoice": invoice
    }


@router.get("")
def get_invoices(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invoices = db.query(Invoice).all()

    return invoices


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


@router.put("/{invoice_id}")
def update_invoice(
    invoice_id: int,
    client_id: int = None,
    invoice_number: str = None,
    invoice_date: str = None,
    description: str = None,
    amount: float = None,
    gst_percent: float = None,
    status: str = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if client_id is not None:
        client = db.query(Client).filter(Client.id == client_id).first()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        invoice.client_id = client_id

    if invoice_number is not None:
        existing_invoice = db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number,
            Invoice.id != invoice_id
        ).first()

        if existing_invoice:
            raise HTTPException(status_code=400, detail="Invoice number already exists")

        invoice.invoice_number = invoice_number

    if invoice_date is not None:
        invoice.invoice_date = invoice_date

    if description is not None:
        invoice.description = description

    if amount is not None:
        invoice.amount = amount

    if gst_percent is not None:
        invoice.gst_percent = gst_percent

    if status is not None:
        invoice.status = status

    invoice.gst_amount, invoice.total_amount = calculate_invoice_totals(
        invoice.amount,
        invoice.gst_percent
    )

    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice updated successfully",
        "invoice": invoice
    }


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted successfully"}
