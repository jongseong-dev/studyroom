import time
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, validator, field_validator
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, ForeignKey
from sqlalchemy.orm import sessionmaker
import os

# Define SQLAlchemy models
DATABASE_URL = "sqlite:///./test2.db"

def reset_database():
    return
    # if os.path.exists("./test2.db"):
    #     os.remove("./test2.db")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

addresses_table = Table(
    "addresses", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("city", String),
    Column("postcode", String),
)

users_table = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("age", Integer),
)

metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Define Models
class AddressBaseModel(BaseModel):
    city: str
    postcode: str

class UserBaseModel(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    age: int
    address: AddressBaseModel

    @field_validator("age")
    @classmethod
    def validate_age(cls, value):
        if value < 0:
            raise ValueError("Age must be a positive integer")
        return value

class AddressTypedDict(TypedDict):
    city: str
    postcode: str

class UserTypedDict(TypedDict):
    id: int
    name: str
    age: int
    address: AddressTypedDict

class UserBaseTypeDictModel(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    age: int
    address: AddressTypedDict

    @field_validator("age")
    @classmethod
    def validate_age(cls, value):
        if value < 0:
            raise ValueError("Age must be a positive integer")
        return value

@dataclass
class AddressDataClass:
    city: str
    postcode: str

@dataclass
class UserDataClass:
    id: int
    name: str
    age: int
    address: AddressDataClass

def measure_performance(label, func):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    print(f"{label}: {end_time - start_time:.6f} seconds")

def insert_test_data():
    user_data = [{"id": i, "name": f"User{i}", "age": 20 + i % 10} for i in range(1, 10001)]
    address_data = [{"user_id": i, "city": f"City{i%10}", "postcode": f"1000{i%100}"} for i in range(1, 10001)]
    session.execute(users_table.insert(), user_data)
    session.execute(addresses_table.insert(), address_data)
    session.commit()

def query_and_convert(model_type):
    results = session.execute(
        users_table.join(addresses_table, users_table.c.id == addresses_table.c.user_id).select()
    ).fetchall()
    if model_type == "pydantic":
        _ = [
            UserBaseModel(
                id=r.id, name=r.name, age=r.age,
                address=AddressBaseModel(city=r.city, postcode=r.postcode)
            ) for r in results
        ]
    elif model_type == "typed_dict":
        _ = [
            UserTypedDict(
                id=r.id, name=r.name, age=r.age,
                address=AddressTypedDict(city=r.city, postcode=r.postcode)
            ) for r in results
        ]
    elif model_type == "py_nested_typed_dict":
        _ = [
            UserBaseTypeDictModel(
                id=r.id, name=r.name, age=r.age,
                address=AddressTypedDict(city=r.city, postcode=r.postcode)
            ) for r in results
        ]
    elif model_type == "dataclass":
        _ = [
            UserDataClass(
                id=r.id, name=r.name, age=r.age,
                address=AddressDataClass(city=r.city, postcode=r.postcode)
            ) for r in results
        ]
    elif model_type == "dict":
        _ = [
            {
                "id": r.id, "name": r.name, "age": r.age,
                "address": {"city": r.city, "postcode": r.postcode}
            } for r in results
        ]

if __name__ == "__main__":
    reset_database()
    metadata.create_all(engine)
    insert_test_data()
    measure_performance("Pydantic BaseModel", lambda: query_and_convert("pydantic"))
    measure_performance("TypedDict", lambda: query_and_convert("typed_dict"))
    measure_performance("Pydantic Nested TypedDict", lambda: query_and_convert("py_nested_typed_dict"))
    measure_performance("Dataclass", lambda: query_and_convert("dataclass"))
    measure_performance("Dict", lambda: query_and_convert("dict"))
