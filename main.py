from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi import HTTPException
import json
import db
import os
import urllib


host_server = os.environ.get('host_server','localhost')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port','5432')))
database_name = os.environ.get('database_name','Records')
db_username = urllib.parse.quote_plus(str(os.environ.get('db_username','postgres')))
db_password = urllib.parse.quote_plus(str(os.environ.get('db_password','C@ndyCrosh')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))

DATABASE_URL = f'postgresql://{db_username}:{db_password}@{host_server}:{db_server_port}/{database_name}?sslmode={ssl_mode}'

app = FastAPI(title = "Mi Maldita Prueba Usando FastAPI")


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/bye")
async def bye():
    return {"message": "Bye World"}


@app.get("/records")
async def get_records():
    """
    Este endpoint devuelve todos los records
    """
    return {"Coño": "Joder"}
    #records = obtener_records()
    #return respuesta_exitosa(records)

# @router.get("/records/{id}")
# async def get_record(id: int):
#     """
#     Este endpoint devuelve un record en particular
#     """
#     try:
#         record = logica.obtener_record(id)
#         if len(record) == 0:
#             raise logica.CustomException(message="No se encontró el record con id " + str(id), code=404)
#         return logica.respuesta_exitosa(record)
#     except logica.CustomException as e:
#         raise HTTPException(status_code=e.code, detail=e.message)

@app.post("/records")
async def post_record(request: Request):
    """
    Crear un nuevo record con los datos recibidos en el body
    """
    #data es un diccionario con los datos que se reciben en el form data
    data = await request.json()
    record = insertar_record(data)
    return respuesta_exitosa(record)

