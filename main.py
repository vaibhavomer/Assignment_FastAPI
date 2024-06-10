from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlite3 import connect

app = FastAPI()
conn = connect("addresses.db")
cursor = conn.cursor()

class Address(BaseModel):
    id: int
    name: str
    coordinates: tuple  # (latitude, longitude)
    address: str

@app.post("/addresses/")
async def create_address(address: Address):
    cursor.execute("""
        INSERT INTO addresses (name, coordinates, address)
        VALUES (?, ?, ?)
    """, (address.name, address.coordinates[0], address.coordinates[1], address.address))
    conn.commit()
    return {"message": "Address created successfully"}

@app.get("/addresses/")
async def get_all_addresses():
    cursor.execute("SELECT * FROM addresses")
    addresses = cursor.fetchall()
    return [{"id": addr[0], "name": addr[1], "coordinates": (addr[2], addr[3]), "address": addr[4]} for addr in addresses]

@app.get("/addresses/{id}")
async def get_address(id: int):
    cursor.execute("SELECT * FROM addresses WHERE id = ?", (id,))
    address = cursor.fetchone()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"id": address[0], "name": address[1], "coordinates": (address[2], address[3]), "address": address[4]}

@app.put("/addresses/{id}")
async def update_address(id: int, address: Address):
    cursor.execute("""
        UPDATE addresses
        SET name = ?, coordinates = ?, address = ?
        WHERE id = ?
    """, (address.name, address.coordinates[0], address.coordinates[1], address.address))
    conn.commit()
    return {"message": "Address updated successfully"}

@app.delete("/addresses/{id}")
async def delete_address(id: int):
    cursor.execute("DELETE FROM addresses WHERE id = ?", (id,))
    conn.commit()
    return {"message": "Address deleted successfully"}

@app.get("/addresses/near/{latitude}/{longitude}/{distance}")
async def get_addresses_nearby(latitude: float, longitude: float, distance: float):
    cursor.execute("""
        SELECT * FROM addresses
        WHERE (ABS(?) - ?) <= (SELECT ABS((?) - ?) FROM addresses)
        AND (ABS(?) - ?) <= (SELECT ABS((?) - ?) FROM addresses)
    """, (latitude, distance, latitude, longitude, longitude, distance))
    addresses = cursor.fetchall()
    return [{"id": addr[0], "name": addr[1], "coordinates": (addr[2], addr[3]), "address": addr[4]} for addr in addresses]