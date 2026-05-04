from fastapi import FastAPI

app = FastAPI()

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