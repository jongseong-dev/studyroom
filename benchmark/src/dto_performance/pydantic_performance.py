import time
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, validator, field_validator
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
import os
# Define SQLAlchemy models
DATABASE_URL = "sqlite:///./test1.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

users_table = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("age", Integer),
)

def reset_database():
    session.close()
    engine.dispose()
    if os.path.exists("./test1.db"):
        os.remove("./test1.db")

metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Define Models
class UserBaseModel(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    age: int

    @field_validator("age")
    @classmethod
    def validate_age(cls, value):
        if value < 0:
            raise ValueError("Age must be a positive integer")
        return value

class UserTypedDict(TypedDict):
    id: int
    name: str
    age: int

@dataclass
class UserDataClass:
    id: int
    name: str
    age: int

def measure_performance(label, func):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    print(f"{label}: {end_time - start_time:.6f} seconds")

def insert_test_data():
    session.execute(
        users_table.insert(),
        [{"id": i, "name": f"User{i}", "age": 20 + i % 10} for i in range(1, 10001)]
    )
    session.commit()

def query_and_convert(model_type):
    results = session.execute(users_table.select()).fetchall()
    if model_type == "pydantic":
        _ = [UserBaseModel(id=r.id, name=r.name, age=r.age) for r in results]
    elif model_type == "typed_dict":
        _ = [UserTypedDict(id=r.id, name=r.name, age=r.age) for r in results]
    elif model_type == "dataclass":
        _ = [UserDataClass(id=r.id, name=r.name, age=r.age) for r in results]
    elif model_type == "dict":
        _ = [{"id": r.id, "name": r.name, "age": r.age} for r in results]

if __name__ == "__main__":
    reset_database()
    metadata.create_all(engine)
    insert_test_data()
    measure_performance("Pydantic BaseModel", lambda: query_and_convert("pydantic"))
    measure_performance("TypedDict", lambda: query_and_convert("typed_dict"))
    measure_performance("Dataclass", lambda: query_and_convert("dataclass"))
    measure_performance("Dict", lambda: query_and_convert("dict"))
