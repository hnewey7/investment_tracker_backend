'''
Module for handling user endpoints.

Created on 22-06-2025
@author: Harry New

'''
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select, func

from app import crud
from app.models import UserCreate, UserPublic, User, UsersPublic, UserUpdate
from app.api.deps import SessionDep
from app.api.routes import orders, summary

# - - - - - - - - - - - - - - - - - - -

router = APIRouter(prefix="/users",tags=["users"])
router.include_router(orders.router, prefix="/{user_id}/orders", tags=["orders"])
router.include_router(summary.router, prefix="/{user_id}/summary", tags=["summary"])

# - - - - - - - - - - - - - - - - - - -
# /USERS ENDPOINT

@router.get(
    "/",
    response_model=UsersPublic
)
def get_users(*, session: SessionDep, skip: int=0, limit: int=100, email: str=None, username: str=None):
    """
    Get users.

    Args:
        session (SessionDep): SQL session.
        skip (int, optional): Skip results. Defaults to 0.
        limit (int, optional): Limit results. Defaults to 100.
        email (str, optional): Email address. Defaults to None.
        username (str, optional): Username. Defaults to None.
    """
    # Counts all users, independent of what users returned.
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    # Statement for returning users.
    statement = select(User).offset(skip).limit(limit)
    if email:
        statement = statement.where(User.email == email)
    elif username:
        statement = statement.where(User.username == username)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/",
    response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> User:
    """
    Create new user.

    Args:
        session (SessionDep): Database session.
        user_in (UserCreate): UserCreate model.

    Returns:
        UserPublic: UserPublic model after creation.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)

    # Create summary for user.
    crud.create_summary(session=session, user=user)

    return user

# - - - - - - - - - - - - - - - - - - -
# /USERS/{USER_ID} ENDPOINT

@router.get(
    "/{user_id}/",
    response_model=UserPublic
)
def get_user_by_id(*, session: SessionDep, user_id: int):
    """
    Get user by id.

    Args:
        session (SessionDep): SQL session.
        user_id (int): User ID.
    """
    user = crud.get_user_by_id(session=session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="No user exists with this id."
        )
    return user


@router.put(
    "/{user_id}/",
    response_model = UserPublic
)
def update_user(*, session: SessionDep, user_id: int, data: UserUpdate) -> User:
    """
    Update user by user id.

    Args:
        session (SessionDep): SQL session.
        data (UserUpdate): Updated details.

    Returns:
        User: Updated user.
    """
    # Get user to update.
    user = crud.get_user_by_id(session=session,id=user_id)

    if not data.username and not data.password:
        raise HTTPException(
            status_code=400,
            detail="No user details to update."
        )
    
    if data.username:
        updated_user = crud.change_username(session=session,email=user.email,new_username=data.username)

    if data.password:
        updated_user = crud.change_password(session=session,email=user.email,new_password=data.password)

    return updated_user


@router.delete(
    "/{user_id}/",
    response_model=UserPublic
)
def delete_user(*, session: SessionDep, user_id: int):
    """
    Delete user by id.

    Args:
        session (SessionDep): SQL session.
        user_id (int): User id.
    """
    user = crud.get_user_by_id(session=session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Unable to find user with id."
        )
    
    # Delete any orders.
    for order in user.orders:
        crud.delete_order(session=session, order=order)

    # Delete corresponding summary.
    summary = crud.get_summary_by_user_id(session=session,user_id=user_id)
    crud.delete_summary(session=session,summary=summary)

    crud.delete_user(session=session,user=user)
    return user

# - - - - - - - - - - - - - - - - - - -