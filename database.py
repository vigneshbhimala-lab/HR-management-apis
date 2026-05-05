from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgres://foodapp_db_eg2w_user:vH6HLgjrHfxpA63JdYraceJFkXUGmCP9@dpg-d7sseo3rjlhs73d1q78g-a/foodapp_db_eg2w"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()