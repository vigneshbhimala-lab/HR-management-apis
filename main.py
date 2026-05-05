from fastapi import FastAPI, HTTPException, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# 🔐 Config
SECRET_KEY = "secret123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- FOOD APIs ---------------- #

foods = [
    {"id": 1, "name": "Biryani", "price": 150},
    {"id": 2, "name": "Pizza", "price": 200},
    {"id": 3, "name": "Burger", "price": 120}
]

orders = []


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
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# 🔒 Protect order API
@app.post("/order")
def place_order(food_id: int, user: str = Depends(get_current_user)):
    for food in foods:
        if food["id"] == food_id:
            order = {
                "order_id": len(orders) + 1,
                "item": food["name"],
                "price": food["price"],
                "user": user
            }
            orders.append(order)
            return {"message": "Order placed", "order": order}

    raise HTTPException(status_code=400, detail="Invalid food id")


@app.get("/orders")
def get_orders():
    return orders


# ---------------- AUTH APIs ---------------- #

users = []


def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Signup
@app.post("/signup")
def signup(username: str, password: str):
    for user in users:
        if user["username"] == username:
            raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(password)

    users.append({
        "username": username,
        "password": hashed_password
    })

    return {"message": "User created successfully ✅"}


# 🔐 Login (OAuth2 standard)
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    for user in users:
        if user["username"] == username:
            if pwd_context.verify(password, user["password"]):
                token = create_token({"sub": username})
                return {"access_token": token, "token_type": "bearer"}
            else:
                raise HTTPException(status_code=401, detail="Wrong password")

    raise HTTPException(status_code=404, detail="User not found")