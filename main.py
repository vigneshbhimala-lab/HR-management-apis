from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy database
foods = [
    {"id": 1, "name": "Biryani", "price": 150},
    {"id": 2, "name": "Pizza", "price": 200},
    {"id": 3, "name": "Burger", "price": 120}
]

orders = []


@app.get("/")
def home():
    return {"message": "Food API Running 🚀"}


# 🔹 Get all foods
@app.get("/foods")
def get_foods():
    return foods


# 🔹 Get single food by ID
@app.get("/foods/{food_id}")
def get_food(food_id: int):
    for food in foods:
        if food["id"] == food_id:
            return food
    return {"error": "Food not found"}


# 🔹 Create order
@app.post("/order")
def place_order(food_id: int):
    for food in foods:
        if food["id"] == food_id:
            order = {
                "order_id": len(orders) + 1,
                "item": food["name"],
                "price": food["price"]
            }
            orders.append(order)
            return {"message": "Order placed", "order": order}
    
    return {"error": "Invalid food id"}


# 🔹 Get all orders
@app.get("/orders")
def get_orders():
    return orders

# fake database
users = []

# 🔹 Signup
@app.post("/signup")
def signup(username: str, password: str):
    for user in users:
        if user["username"] == username:
            raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(password)

    user = {
        "username": username,
        "password": hashed_password
    }

    users.append(user)

    return {"message": "User created successfully ✅"}


# 🔹 Login
@app.post("/login")
def login(username: str, password: str):
    for user in users:
        if user["username"] == username:
            if pwd_context.verify(password, user["password"]):
                return {"message": "Login successful 🔥"}
            else:
                raise HTTPException(status_code=401, detail="Wrong password")

    raise HTTPException(status_code=404, detail="User not found")