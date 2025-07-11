'''
Module for handling CRUD operations on database.

Created on 22-06-2025
@author: Harry New

'''
from datetime import datetime

from sqlmodel import Session, select

from app.models import User, UserCreate, Instrument, Order, OrderCreate, OrdersPublic, InstrumentBase, OrderUpdate, Summary, SummaryUpdate
from app.core.security import get_password_hash, verify_password

# - - - - - - - - - - - - - - - - - - -
# USER OPERATIONS

def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create user.

    Args:
        session (Session): SQL session.
        user_create (UserCreate): UserCreate model.

    Returns:
        User: User model.
    """
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get user by email.

    Args:
        session (Session): SQL session.
        email (str): Email address to search for.

    Returns:
        User | None: User model or none.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_username(*, session: Session, username: str) -> User | None:
    """
    Get user by username.

    Args:
        session (Session): SQL session.
        username (str): Username to search for.

    Returns:
        User | None: User model or none.
    """
    statement = select(User).where(User.username == username)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_id(*, session: Session, id: int) -> User | None:
    """
    Get user by id.

    Args:
        session (Session): SQL session.
        id (int): User id.

    Returns:
        User | None: User model.
    """
    statement = select(User).where(User.id == id)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str = None, username: str = None , password: str) -> User | None:
    """
    Authenticate user.

    Args:
        session (Session): SQL session.
        email (str | None): Email address, optional.
        username (str | None): Username, optional.
        password (str): Password.

    Returns:
        User | None: User model or none.
    """
    # Getting user by email or username.
    if email:
        db_user = get_user_by_email(session=session, email=email)
    else:
        db_user = get_user_by_username(session=session, username=username)

    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def change_username(*, session: Session, email: str, new_username: str) -> User:
    """
    Change username.

    Args:
        session (Session): SQL session.
        email (str): Email address.
        new_username (str): New username.

    Returns:
        User: Updated user model.
    """
    # Get user.
    user = get_user_by_email(session=session, email=email)
    # Update username.
    user.username = new_username
    session.commit()
    session.refresh(user)
    return user


def change_password(*, session: Session, email: str, new_password: str) -> User:
    """
    Change password.

    Args:
        session (Session): SQL session.
        email (str): Email address.
        new_password (str): New password.

    Returns:
        User: Updated User model.
    """
    # Get user.
    user = get_user_by_email(session=session, email=email)
    # Update username.
    user.hashed_password = get_password_hash(new_password)
    session.commit()
    session.refresh(user)
    return user


def delete_user(*, session: Session, user: User):
    """
    Delete user.

    Args:
        session (Session): SQL session.
        user (User): User to delete.
    """
    # Delete user.
    session.delete(user)
    session.commit()

# - - - - - - - - - - - - - - - - - - -
# INSTRUMENT OPERATIONS

def create_instrument(*, session: Session, instrument_create: InstrumentBase):
    """
    Creating instrument.

    Args:
        session (Session): 
        instrument_create (InstrumentBase): Instrument details.
    """
    db_obj = Instrument.model_validate(
        instrument_create
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_instrument_by_symbol(*, session: Session, symbol:str) -> Instrument:
    """
    Get instrument by symbol.

    Args:
        session (Session): SQL session.
        symbol (str): Symbol.

    Returns:
        Instrument: Instrument in database.
    """
    statement = select(Instrument).where(Instrument.symbol == symbol)
    session_instrument = session.exec(statement).first()
    return session_instrument


def get_instrument_by_id(*, session: Session, id: int) -> Instrument:
    """
    Get instrument by id.

    Args:
        session (Session): SQL session.
        id (int): Instrument id.

    Returns:
        Instrument: Instrument
    """
    statement = select(Instrument).where(Instrument.id == id)
    session_instrument = session.exec(statement).first()
    return session_instrument


def update_instrument_prices(*, session: Session, instrument: Instrument, open: float, high: float, low: float, close: float) -> Instrument:
    """
    Update prices of an instrument.

    Args:
        session (Session): SQL session.
        instrument (Instrument): Instrument to update.
        open (float): Open price.
        high (float): High price.
        low (float): Low price.
        close (float): Close price.

    Returns:
        Instrument: Updated instrument.
    """
    # Update prices.
    instrument.open = open
    instrument.high = high
    instrument.low = low
    instrument.close = close
    # Commit to db.
    session.commit()
    session.refresh(instrument)
    return instrument


def update_instrument_currency(*, session: Session, instrument: Instrument, currency: str) -> Instrument:
    """
    Update currency of instrument.

    Args:
        session (Session): SQL session.
        instrument (Instrument): Instrument to update.
        currency (str): Currency.

    Returns:
        Instrument: Updated instrument.
    """
    instrument.currency = currency
    session.commit()
    session.refresh(instrument)
    return instrument


def delete_instrument(*, session: Session, instrument: Instrument):
    """
    Delete instrument.

    Args:
        session (Session): SQL session.
        instrument (Instrument): Instrument to delete.
    """
    # Delete instrument.
    session.delete(instrument)
    session.commit()

# - - - - - - - - - - - - - - - - - - -
# ORDER OPERATIONS

def create_order(*, session: Session, user_id: int, order_create: OrderCreate) -> Order:
    """
    Creating a new order.

    Args:
        session (Session): SQL session.
        user_id (int): User id.
        order_create (OrderCreate): Order details.

    Returns:
        Order: New order.
    """
    db_obj = Order.model_validate(
        order_create, 
        update={"user_id":user_id}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_orders(
        *, 
        session: Session,
        user_id: int, 
        instrument_id: int=None, 
        start_date: datetime=None, 
        end_date: datetime=None, 
        type: str=None
    ) -> OrdersPublic:
    """
    Get orders with various filters.

    Args:
        session (Session): SQL session.
        user_id (int): User id.
        instrument_id (int, optional): Instrument id. Defaults to None.
        start_date (datetime, optional): Start date.. Defaults to None.
        end_date (datetime, optional): End date. Defaults to None.
        type (str, optional): Type. Defaults to None.

    Returns:
        OrdersPublic: Returned orders
    """
    # Basic statement.
    statement = select(Order).where(Order.user_id == user_id)

    if instrument_id:
        statement = statement.where(Order.instrument_id == instrument_id)
    if start_date:
        statement = statement.where(Order.date >= start_date)
    if end_date:
        statement = statement.where(Order.date <= end_date)
    if type:
        statement = statement.where(Order.type == type)

    results = session.exec(statement).all()
    return OrdersPublic(data=results,count=len(results))


def get_order_by_id(*, session: Session, order_id: int) -> Order:
    """
    Get order by id.

    Args:
        session (Session): SQL session.
        order_id (int): Order id.

    Returns:
        Order: Order.
    """
    statement = select(Order).where(Order.id == order_id)
    db_obj = session.exec(statement).first()
    return db_obj


def update_order(*, session: Session, order: Order, order_update: OrderUpdate) -> Order:
    """
    Update order.

    Args:
        session (Session): SQL session.
        order (Order): Order to update.
        order_update (OrderUpdate): New details.

    Returns:
        Order: Updated order.
    """
    update_dict = order_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(order, key):
            setattr(order, key, value)
    session.commit()
    session.refresh(order)
    return order


def delete_order(*, session: Session, order: Order) -> None:
    """
    Delete order.

    Args:
        session (Session): SQL session.
        order (Order): Order to delete.
    """
    session.delete(order)
    session.commit()

# - - - - - - - - - - - - - - - - - - -
# SUMMARY OPERATIONS

def create_summary(*, session: Session, user: User) -> Summary:
    """
    Create summary.

    Args:
        session (Session): SQL session.
        user (User): User.

    Returns:
        Summary: New summary.
    """
    db_obj = Summary(user=user)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_summary_by_id(*, session: Session, summary_id: int) -> Summary:
    """
    Get summary by id.

    Args:
        session (Session): SQL session.
        summary_id (int): Summary id.

    Returns:
        Summary: Summary.
    """
    statement = select(Summary).where(Summary.id == summary_id)
    db_obj = session.exec(statement).first()
    return db_obj


def get_summary_by_user_id(*, session: Session, user_id: int) -> Summary:
    """
    Get summary by user id.

    Args:
        session (Session): SQL session.
        user_id (int): User id.

    Returns:
        Summary: Summary.
    """
    column = getattr(Summary,"user_id")
    statement = select(Summary).where(column == user_id)
    db_obj = session.exec(statement).first()
    return db_obj


def update_summary(*, session: Session, summary: Summary, summary_update: SummaryUpdate) -> Summary:
    """
    Update summary.

    Args:
        session (Session): SQL session.
        summary (Summary): Summary to update.
        summary_update (SummaryUpdate): Update summary details.

    Returns:
        Summary: Updated summary.
    """
    update_dict = summary_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(summary, key):
            setattr(summary, key, value)
    session.commit()
    session.refresh(summary)
    return summary


def delete_summary(*, session: Session, summary: Summary) -> None:
    """
    Delete summary.

    Args:
        session (Session): SQL session.
        summary (Summary): Summary to delete.
    """
    session.delete(summary)
    session.commit()