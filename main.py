from fastapi import FastAPI
from db import init_db
from routes.eventRoutes import router as eventRouter
from routes.userRoutes import router as userRouter



app = FastAPI()
init_db()
app.include_router(eventRouter)
app.include_router(userRouter)


