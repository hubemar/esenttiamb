import mysql.connector
import os, json
from dotenv import load_dotenv

load_dotenv()
host=os.getenv('HOST_PROD')
port=os.getenv('PORT_PROD')
user=os.getenv('USER_PROD')
password=os.getenv('PASS_PROD')
database=os.getenv('DB_PROD')
def goconnector():

    if os.getenv("MODE") != "[DEMO]":
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    else:
        with open("Invoice.json", "r") as f:
            connection = json.load(f)
    return connection