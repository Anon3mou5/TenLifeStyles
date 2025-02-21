# This a FastAPI application which uses 'uvicorn' to run underneath, it's a lightweight asynchronous framework.

## How to run:
  1) Install all requirements from requirements.txt
  2) Swap config.py with the file provided over email ( contains db URL and jwt secret)
  3) Run uvicorn main:app --reload
  4) Once the application is up and you can visit http://localhost:8000/docs for swagger to test API's

## How to use API's
  1) Register as a user to generate a token( for accessing other URLs), its path is authentication/create ( use swagger for request body )
  2) Generate token by using username password through authentication/login
  3) Use the jwt token as an Authorization header and run the other APIs

## NOTE
  1) Database is created through SQLAlchemy
