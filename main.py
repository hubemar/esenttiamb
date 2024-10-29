from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.openapi.docs import get_swagger_ui_html
from searchshipping import *
from pydantic import BaseModel, Field, constr
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from html import escape
import pytz
import html
import os
from datetime import datetime, timedelta
from fastapi.openapi.utils import get_openapi


client_ip = ""
# Configura la zona horaria de Colombia
colombia_tz = pytz.timezone('America/Bogota')

# Obtiene la fecha y hora actual de Colombia
now = datetime.now(colombia_tz)

# Imprime la fecha y hora actual de Colombia
todaynow = now.strftime("%Y-%m-%d %H:%M:%S")

# Reemplaza <username>, <password>, <cluster-url> y <database-name> con los valores correspondientes
load_dotenv()
URI = "mongodb+srv://pperez:0lxkUIwb2Xd4AroE@logapisaphana.reaticg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(URI)
db = client.LogHana
collection = db.logconnections

app = FastAPI()
#app.add_middleware(HTTPSRedirectMiddleware)
# Lista de direcciones IP permitidas
ALLOWED_IPS = os.getenv("ALLOWED_IPS")

@app.middleware("http")
async def block_ips(request: Request, call_next):
    global client_ip, new_id
    # Obtener la dirección IP del cliente
    client_ip = request.client.host
    #Insert log
    document = {"ip": client_ip, "token": None, "datetime": todaynow}
    new_id = collection.insert_one(document).inserted_id
    print(ALLOWED_IPS)
    print(document)
    #Verificar que bloqueo esta dashabilitado colocando 0.0.0.0
    if ALLOWED_IPS != '0.0.0.0':
        # Verificar si la dirección IP está permitida
        if client_ip not in ALLOWED_IPS:
            data = {
                "response": "01",
                "message": os.getenv("MESSAGE_BLOCK_IPS").format(client_ip)
                }
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=data)
    
    # Continuar con la solicitud si la dirección IP está permitida
    response = await call_next(request)
    headers = {
            "Cache-Control": "max-age=3600",
            "Strict-Transport-Security": "max-age=31556926; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Permissions-Policy": "geolocation=(self)",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Content-Security-Policy": "base-uri 'self'; frame-ancestors 'none'; form-action 'self'; object-src 'self'; script-src 'self' cdn.jsdelivr.net 'nonce-randomstring' 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; worker-src blob: cdn.jsdelivr.net 'nonce-randomstring' 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; style-src 'self' cdn.jsdelivr.net fonts.googleapis.com 'nonce-randomstring' 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; upgrade-insecure-requests;"
        }
    response.headers.update(headers)
    return response

@app.get("/set-cookie" , include_in_schema=False)
async def set_secure_cookie(response: Response):
    response.set_cookie(
        key="secure_cookie",
        value="secure_value",
        httponly=True,
        samesite="Strict",
        secure=True
    )
    return {"message": "Secure cookie set"}


"""app.title = os.getenv('DOCS_TITLE')
app.version = os.getenv('APP_VERSION')
app.description = os.getenv('DOCS_API_DESCRIPTION')
app.openapi_url = "/openapi.json"
favicon_path = 'favicon.png'
app.swagger_favicon_url = favicon_path"""


uname = os.getenv("UNAME")
email = os.getenv("EMAIL")
hashed_password = os.getenv("HASHED_PASSWORD")
disabled = os.getenv("DISABLED")
db = {
    uname: {
            "username":uname,
            "email":email,
            "hashed_password":hashed_password,
            "disabled ":disabled
    }
}

class Token(BaseModel):
    access_token: str = Field(max_length=125)
    token_type: str = Field(default = "bearer", max_length=6)

class TokenData(BaseModel):
    username: str or None = None

class User(BaseModel):
    username: str = Field(default = None, type = "string", format= "string", pattern="^[a-zA-Z0-9_-]+$", max_length=40)
    email:str = Field(default = None, format= "email", pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", max_length=40)
    disabled:bool or None = None

class UserInDB(User):
    hashed_password: str

class Invoice(BaseModel):
    numberinvoice:str =  Field(max_length=40, format= "string", pattern="^(?:[a-zA-Z0-9_-]+)?$")
    numberbl : str = Field(max_length=40, format= "string", pattern="^(?:[a-zA-Z0-9_-]+)?$")
    datefrom: str = Field(default = "dd/mm/yyyy",  max_length=10, format = "string", pattern="^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$")
    dateto: str = Field(default = "dd/mm/yyyy",   max_length=10, format = "string", pattern="^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)

def authemticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return  False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_access_token(data:dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
        )
    try:
        payload = jwt.decode(token,  os.getenv('SECRET_KEY'),  algorithms=[os.getenv('ALGORITHM')])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

app.title =  str(os.getenv('DOCS_TITLE'))
app.version = os.getenv('APP_VERSION')
app.description = str(os.getenv('DOCS_API_DESCRIPTION'))
app.openapi_url = "/openapi.json"
favicon_path = 'favicon.png'
app.swagger_favicon_url = favicon_path
#Definir faviocn en home y en docs
@app.get('/favicon.png', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        swagger_favicon_url=favicon_path
    )

@app.post("/login", response_model=Token, tags=['Consulta Instrucción de Embarque '])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data.username)
    print(escape(form_data.username).replace(';','').replace('/',''))
    user = authemticate_user(db, escape(form_data.username), escape(form_data.password))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={
                            "response": "44",
                            "message":"Incorrect username or password"
                            },
                            headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = create_access_token(
        data={"sub":user.username}, expires_delta=access_token_expires)
    new_val = {"$set":{"token": access_token}}
    collection.update_one({"_id": new_id}, new_val)
    return {
        "response":"10",
        "access_token": access_token,
        "token_type": "bearer"
        }


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def home():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">  
    <head>  
        <title>Web Services Hubemar/esenttia </title>
        <link rel="icon" type="image/jpg" href="/favicon.png"/>
    </head>
        <body>
            <h1>Hubemar / esenttia
            </h1>
            <a href="/docs">Pruebas y Login</a>
            <br/>
            
            From:{client_ip}
            </p>
        </body>
    </html>
    """
    return HTMLResponse(html_content)
@app.post('/api/v1/shipping', tags=['Consulta Instrucción de Embarque '])
async def shipping(invoice : Invoice, current_user: User = Depends(get_current_active_user)):
    return searchshipping(invoice)
        
# Generate the OpenAPI schema with the modified format

def custom_openapi():
    if app.openapi_schema:
        app.openapi_schema["components"]["schemas"]["Body_login_for_access_token_login_post"]["properties"]["username"] = {
            "type": "string",
            "title":"Username",
            "format": "string", 
            "pattern":"^[a-zA-Z0-9_-]+$",
            "maxLength":40,
        }
        app.openapi_schema["components"]["schemas"]["Body_login_for_access_token_login_post"]["properties"]["password"] = {
            "type": "string",
            "title":"Password",
            "format": "string", 
            "pattern":"^[a-zA-Z0-9_-]+$",
            "maxLength":40,
        }
        app.openapi_schema["components"]["schemas"]["Body_login_for_access_token_login_post"]["properties"]["scope"] = {
            "type": "string",
            "title":"Scope",
            "format": "string", 
            "pattern":"^[a-zA-Z0-9_-]+$",
            "maxLength":40,
        }
        app.openapi_schema["components"]["schemas"]["HTTPValidationError"]["properties"]["detail"] = {
            "properties":{
               "detail":{
                  "maxItems":"10", 
                  "items":{
                     "$ref":"#/components/schemas/ValidationError"
                  },
                  "type":"array",
                  "title":"Detail"
               }
            },
            "type":"object",
            "title":"HTTPValidationError"
        }
        app.openapi_schema["components"]["schemas"]["Token"]["properties"]["access_token"] = {
            "type":"string",
            "maxLength":125,
            "title":"Access Token",
            "format":"string",
            "pattern":"^[a-zA-Z0-9_-]{1,125}$"
        }
        app.openapi_schema["components"]["schemas"]["Token"]["properties"]["token_type"] = {
            "type":"string",
            "maxLength":6,
            "title":"Token Type",
            "default":"bearer",
            "format":"string",
            "pattern":"^[a-zA-Z]{1,6}$"
        }
        app.openapi_schema["components"]["schemas"]["ValidationError"]["properties"]["loc"] = {
            "maxItems":"10", 
            "items":{
                    "anyOf":[
                        {
                            "type":"string"
                        },
                        {
                            "type":"integer"
                        }
                    ]
                },
                "type":"array",
                "title":"Location"
        }
        app.openapi_schema["components"]["schemas"]["ValidationError"]["properties"]["msg"] = {
            "type":"string",
            "maxLength":20,
            "title":"Message",
            "format":"string",
            "pattern":"^[a-zA-Z]{1,6}$"
        }
        app.openapi_schema["components"]["schemas"]["ValidationError"]["properties"]["type"] = {
            "type":"string",
            "maxLength":20,
            "title":"Error Type",
            "format":"string",
            "pattern":"^[a-zA-Z]{1,6}$"
        }
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=str(os.getenv('DOCS_TITLE')),
        version= os.getenv('APP_VERSION'),
        summary="",
        description= os.getenv('DOCS_API_DESCRIPTION'),
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://hubemar.com/wp-content/uploads/2019/10/hubemar-logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

#print(get_password_hash("4nPBP.nX"))
