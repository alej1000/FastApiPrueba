from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
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
