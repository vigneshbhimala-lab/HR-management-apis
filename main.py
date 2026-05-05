from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
app = FastAPI()

# 🔐 Config
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users = []

# 🧾 Models
class User(BaseModel):
    username: str
    password: str

# 🔹 Create Token
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# 🔹 Get Current User
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 🔹 Signup
@app.post("/signup")
def signup(user: User):
    for u in users:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="User exists")
    password = user.password[:72]
    hashed = pwd_context.hash(password)
    users.append({"username": user.username, "password": hashed})

    return {"message": "User created"}

# 🔹 Login (returns token)
@app.post("/login")
def login(user: User):
    for u in users:
        if u["username"] == user.username:
            if pwd_context.verify(user.password, u["password"]):
                token = create_token({"sub": user.username})
                return {"access_token": token, "token_type": "bearer"}
            raise HTTPException(status_code=401, detail="Wrong password")

    raise HTTPException(status_code=404, detail="User not found")

# 🔒 Protected Route
@app.get("/profile")
def profile(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome {current_user} 🔥"}