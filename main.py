import uvicorn
from fastapi import FastAPI


from configuration.database_config import engine, Base

from fastapi.middleware.cors import CORSMiddleware

from controllers import booking_controller, inventory_controller, member_controller, auth_controller

app = FastAPI()
app.include_router(booking_controller.router)
app.include_router(inventory_controller.router)
app.include_router(member_controller.router)
app.include_router(auth_controller.router)


Base.metadata.create_all(engine,checkfirst=True)

origins = [
  '*',
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)


if __name__ == "__main__":
  uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)

