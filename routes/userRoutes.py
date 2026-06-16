from fastapi import APIRouter, Response, HTTPException
from models.schemas import User as UserORM
from models.userModels import UserModels
from utils.sqlErrorMap import SQLITE_ERROR_MAP
from sqlalchemy.exc import IntegrityError
from schemas.pydantic_schemas import UserEssentialSchema, UserSchema

router = APIRouter() 

@router.post("/register-user")
async def register_user(item: UserSchema, response: Response):
    response.status_code = 201
    try:
        orm_user = UserORM(
            username=item.username,
            event_id=item.event_id,
            timestamp=str(item.timestamp),
        )
        registered = UserModels.register(orm_user)
        if not registered:
            raise HTTPException(status_code=409, detail="Event is full or does not exist")
        return {"message": "User Registered Successfully"}
    except IntegrityError as e:
        error = e.orig
        error_name = getattr(error, "sqlite_errorname", None)
        if error_name in SQLITE_ERROR_MAP:
            error_status = SQLITE_ERROR_MAP[error_name]
            raise HTTPException(status_code=error_status[0], detail=error_status[1])
        raise HTTPException(status_code=500, detail="DB ERROR")

@router.delete("/cancel-user-registration")
async def cancel_user_reg(item: UserEssentialSchema):
    try:
        orm_user = UserORM(
            username=item.username,
            event_id=item.event_id,
            timestamp="",  
        )
        is_deleted = UserModels.delete_registration(orm_user)
        if not is_deleted:
            raise HTTPException(status_code=404, detail="User registration does not exist")
        return {"message": "Cancelled Successfully"}
    except IntegrityError:
        raise HTTPException(status_code=500, detail="DB ERROR")
