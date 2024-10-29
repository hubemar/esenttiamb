# Api RESTful Hubemar / esenttia

## Try Connection
py connection.py

## Local Web 
uvicorn main:app --reaload

## Production URI
https://esenttia-pt.onrender.com/

## API Reference v1

#### login For Access Token

```http
  POST /login
```
| Request Body | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**.  |
| `password` | `string` | **Required**.  |

##### Response
```
{
  "response":"10",
  "access_token": access_token,
  "token_type": "bearer"
}
```

TOKEN_EXPIRE_MINUTES = 525600 (1 año)

#### Consultas

```http
  POST /api/v1/shipping
```

| Request Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `numberinvoice`      | `string` | **Opcional** 
| `numberbl`      | `string` | **Opcional** 
| `datefrom`      | `dd/mm/yyyy` | **Opcional** 
| `numberto`      | `dd/mm/yyyy` | **Opcional** 

##### Ejemplos
```
{
  "numberinvoice": "900170",
  "numberbl": "string",
  "datefrom": "dd/mm/yyyy",
  "dateto": "dd/mm/yyyy"
}
```
```
{
  "numberinvoice": "string",
  "numberbl": "SUDU23BOG009359A",
  "datefrom": "dd/mm/yyyy",
  "dateto": "dd/mm/yyyy"
}
```
```
{
  "numberinvoice": "string",
  "numberbl": "string",
  "datefrom": "02/08/2023",
  "dateto": "30/08/2023"
}
```
## Dependencias
pip freeze > .\requirements-local.txt 

## Documentación

[Test Login y pruebas](https://esenttia-pt.onrender.com/docs)

[Documentacíon](https://esenttia-pt.onrender.com/redoc)