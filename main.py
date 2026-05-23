from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import create_token, get_current_user, pwd_context
from clients import router as clients_router
from database import engine, Base, get_db
from invoices import router as invoices_router
from models import Employee, User
from email_utils import send_email

app = FastAPI()


Base.metadata.create_all(bind=engine)
app.include_router(clients_router)

app.include_router(invoices_router)



@app.get("/")
def home():
    return {"message": "Employee Management API Running "}

@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(password)

    new_user = User(
        username=username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/employees")
def create_employee(
    name: str,
    email:str,
    dob: str,
    gender: str,
    nationality: str,
    education: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    employee = Employee(
        name=name,
        email=email,
        dob=dob,
        gender=gender,
        nationality=nationality,
        education=education
    )

    db.add(employee)
    db.commit()

    
    db.refresh(employee)
    try:
        send_email(employee.email, employee.name)
    except Exception as e:
        print(f"Error sending email: {e}")

    return {
        "message": "Employee created successfully",
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "dob": employee.dob,
            "gender": employee.gender,
            "nationality": employee.nationality,
            "education": employee.education
        }
    }

@app.get("/employees")
def get_employees(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    employees = db.query(Employee).all()

    return employees


@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    name: str = None,
    dob: str = None,
    gender: str = None,
    nationality: str = None,
    education: str = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Update only provided fields
    if name is not None:
        employee.name = name

    if dob is not None:
        employee.dob = dob

    if gender is not None:
        employee.gender = gender

    if nationality is not None:
        employee.nationality = nationality

    if education is not None:
        employee.education = education

    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee updated successfully",
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "dob": employee.dob,
            "gender": employee.gender,
            "nationality": employee.nationality,
            "education": employee.education
        }
    }

@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


@app.get("/profile")
def get_profile(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome {current_user}"}
