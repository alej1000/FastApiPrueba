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

#region Funciones de respuesta
class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

def respuesta_exitosa(data):
    return {"success": True, "code": 200, "message": "OK", "data": data}

def respuesta_fallida(mensaje, code=400):
    raise CustomException(message=mensaje, code=code)

#endregion


#region funciones de la base de datos
def get_connection():
    conn = psycopg2.connect(
        dbname='aotdlhvi',
        user='aotdlhvi',
        password='yJMYPFXps-4hLoQ2KO5iEzXs7o-bJxyJ',
        host='trumpet.db.elephantsql.com',
        port='5432')
    if conn:
        print('Conectado a la base de datos')
    else:
        print('Error al conectar a la base de datos')
    return conn

def realizar_consulta(sql:str, params=None):
    if not sql.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="La consulta debe ser de tipo SELECT")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    column_names = [desc[0] for desc in cursor.description]  # get the column names from the cursor
    results = [dict(zip(column_names, row)) for row in cursor.fetchall()]  # convert each row to a dictionary
    cursor.close()
    conn.close()
    return results

def realizar_consulta_conexion(conn,sql:str, params=None):
    if not sql.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="La consulta debe ser de tipo SELECT")
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
    except:
        #print the error message
        import traceback
        traceback.print_exc()  # print the traceback of the error
    column_names = [desc[0] for desc in cursor.description]  # get the column names from the cursor
    results = [dict(zip(column_names, row)) for row in cursor.fetchall()]  # convert each row to a dictionary
    cursor.close()
    return results

def realizar_insercion(nombre_tabla: str, data: dict):
    conn = get_connection()
    #region verificar que la tabla exista
    sql = 'SELECT * FROM %s LIMIT 1'
    table_name = AsIs(nombre_tabla)
    params = (table_name,)
    try:
        realizar_consulta_conexion(conn, sql, params)
    except:
        return {"success": False, "code": 400, "message": f"La tabla {nombre_tabla} no existe"}
    #endregion
    
    #region establecer el valor de pk al nombre de la columna que es clave primaria
    sql_pk = "SELECT kcu.column_name FROM information_schema.key_column_usage kcu JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name WHERE kcu.table_name = %s AND tc.constraint_type = 'PRIMARY KEY';"
    params = (nombre_tabla,)
    pk = realizar_consulta_conexion(conn,sql_pk, params)[0]["column_name"]
    #endregion

    #region Verificar que la columna de la clave primaria no se haya enviado en el diccionario o que su valor sea None
    if pk in data and data[pk] is not None:
        return {"success": False, "code": 400, "message": f"No se puede enviar el valor de la clave primaria '{pk}'"}
      # obtener los nombres de las columnas de la tabla
    sql ='SELECT column_name FROM information_schema.columns WHERE table_name = %s'
    columnas = realizar_consulta_conexion(conn,sql,params)
    columnas = [columna["column_name"] for columna in columnas]
    #endregion

    #region revisar que todas las columnas enviadas existan en la tabla
    for columna in data:
        if columna not in columnas:
            return {"success": False, "code": 400, "message": f"La columna '{columna}' no existe en la tabla '{nombre_tabla}'"}
    #endregion

    #region eliminar las columnas que no estén presentes en data
    columnas = [columna for columna in columnas if columna in data]
    #endregion

    #region agregar columnas que no están presentes en el diccionario como None
    valores = [data.get(columna, None) for columna in columnas]
    #endregion

    #region construir la consulta omitiendo la columna de la clave primaria
    sql = f"INSERT INTO {nombre_tabla} ({', '.join(columna for columna in columnas if columna != pk)}) VALUES ({', '.join(['%s' for columna in columnas if columna != pk])})"
    params = (*valores,)
    try:
        insertar_datos_conexion(conn,sql, valores)
    except IntegrityError:
        return {"success": False, "code": 400, "message": f"Ya existe un registro con la clave primaria '{data[pk]}'"}
    #endregion

    #region obtener el valor de la clave primaria del nuevo registro
    sql = f"SELECT currval(pg_get_serial_sequence('{nombre_tabla}', '{pk}'))"
    pk_value = realizar_consulta_conexion(conn, sql)[0]["currval"]
    #endregion

    #region devolver el registro insertado
    query = 'SELECT * FROM %s WHERE %s = %s'
    params = (table_name, AsIs(pk), pk_value)
    resultado = realizar_consulta_conexion(conn, query, params)
    #endregion
    conn.close()
    return resultado


def insertar_datos_conexion(conn,sql, params=None):
    #revisamos si es un insert y no un select o update o delete...
    #if any of the params is None change it to NULL
    params = [None if param is None else param for param in params]
    if not sql.upper().startswith("INSERT"):
        #si es un insert, obtenemos los datos
        return "Error"
    cursor = conn.cursor()
    #print the query with the params
    print(cursor.mogrify(sql, params))
    cursor.execute(sql, params)
    print("he insertado los datos")
    #si no hay errores retornamos el id del registro insertado
    conn.commit()
    cursor.close()
    return cursor.lastrowid

#endregion


def obtener_records():
    query = "SELECT * FROM scores ORDER BY fecha DESC LIMIT 10"
    records = db.realizar_consulta(query)
    return records

def insertar_record(data: dict):
    nombre_tabla = "scores"
    record = db.realizar_insercion(nombre_tabla, data)
    return record

# a partir de aquí se definen las rutas

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

