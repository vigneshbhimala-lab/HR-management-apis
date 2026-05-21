from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Client
from invoice_email import send_email

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("")
def create_client(
    name: str,
    company_name: str,
    email: str,
    phone: str,
    address: str,
    gst_number: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = Client(
        name=name,
        company_name=company_name,
        email=email,
        phone=phone,
        address=address,
        gst_number=gst_number
    )

    db.add(client)
    db.commit()
    db.refresh(client)
    send_email(client.email, client.name)

    return {
        "message": "Client created successfully",
        "client": client
    }


@router.get("")
def get_clients(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    clients = db.query(Client).all()

    return clients


@router.get("/{client_id}")
def get_client(
    client_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.put("/{client_id}")
def update_client(
    client_id: int,
    name: str = None,
    company_name: str = None,
    email: str = None,
    phone: str = None,
    address: str = None,
    gst_number: str = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if name is not None:
        client.name = name

    if company_name is not None:
        client.company_name = company_name

    if email is not None:
        client.email = email

    if phone is not None:
        client.phone = phone

    if address is not None:
        client.address = address

    if gst_number is not None:
        client.gst_number = gst_number

    db.commit()
    db.refresh(client)

    return {
        "message": "Client updated successfully",
        "client": client
    }


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()

    return {"message": "Client deleted successfully"}
