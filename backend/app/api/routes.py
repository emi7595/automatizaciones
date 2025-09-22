from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.contact import ContactCreate, ContactRead
from app.models.contact import Contact
from app.db import get_db

router = APIRouter(prefix="/contacts", tags=["contacts"])

# Crear contacto
@router.post("/", response_model=ContactRead)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.phone == contact.phone).first()
    if db_contact:
        raise HTTPException(status_code=400, detail="El contacto ya existe")
    new_contact = Contact(name=contact.name, phone=contact.phone)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

# Obtener todos los contactos
@router.get("/", response_model=list[ContactRead])
def get_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).all()

# Obtener un contacto por ID
@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return contact

# Eliminar contacto
@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    db.delete(contact)
    db.commit()
    return {"msg": "Contacto eliminado"}