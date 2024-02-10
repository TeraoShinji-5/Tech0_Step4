from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    number: int
    altitude: int

class Item2(BaseModel):
    altitude: int

@app.post("/double")
def double_number(item: Item):
    return {"result": item.number * 2}

@app.post("/otanisann")
def altitude_otanisann(item: Item2):
    altitude = item.altitude
    ohtani_height = 1.97
    otanisann = round(altitude / ohtani_height)
    return  {"result": otanisann}
