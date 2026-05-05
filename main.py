from fastapi import FastAPI, HTTPException, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Order

app = FastAPI()

# 🔐 Config
SECRET_KEY = "secret123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- DATABASE SETUP ---------------- #

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- FOOD APIs ---------------- #

foods = [
    {"id": 1, "name": "Biryani", "price": 150},
    {"id": 2, "name": "Pizza", "price": 200},
    {"id": 3, "name": "Burger", "price": 120}
]


@app.get("/")
def home():
    return {"message": "Food API Running 🚀"}


@app.get("/foods")
def get_foods():
    return foods


@app.get("/foods/{food_id}")
def get_food(food_id: int):
    for food in foods:
        if food["id"] == food_id:
            return food
    raise HTTPException(status_code=404, detail="Food not found")


# ---------------- AUTH HELPERS ---------------- #

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------- AUTH APIs ---------------- #

@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(password)

    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()

    return {"message": "User created successfully ✅"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# ---------------- ORDER APIs ---------------- #

@app.post("/order")
def place_order(food_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    for food in foods:
        if food["id"] == food_id:
            new_order = Order(
                item=food["name"],
                price=food["price"],
                user=current_user
            )
            db.add(new_order)
            db.commit()

            return {"message": "Order placed"}

    raise HTTPException(status_code=400, detail="Invalid food id")


@app.get("/orders")
def get_orders(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_orders = db.query(Order).filter(Order.user == current_user).all()
    return user_orders


# ---------------- PROFILE ---------------- #

@app.get("/profile")
def get_profile(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome {current_user} 🔥"}