'''
Module for testing assets endpoint.

Created on 04-07-2025
@author: Harry New

'''
from datetime import datetime

from sqlmodel import Session
from fastapi.testclient import TestClient

from app.models import Portfolio, Instrument, User, Asset
from app import crud

# - - - - - - - - - - - - - - - - - - -
# GET /USERS/{USER_ID}/PORTFOLIO/ASSETS TESTS

def test_get_assets(client: TestClient, db: Session, portfolio: Portfolio, instrument: Instrument):
    """
    Test get assets in user's portfolio.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument
    """
    # Create asset.
    asset_properties = {
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1
    }
    asset = crud.create_asset(session=db, portfolio=portfolio, instrument=instrument, **asset_properties)
    
    # Send get request.
    response = client.get(f"/users/{portfolio.user_id}/portfolio/assets")
    assets_json = response.json()
    assert response.status_code == 200
    assert len(assets_json["data"]) == 1
    assert assets_json["count"] == 1
    assert assets_json["data"][0]["id"] == asset.id


def test_get_assets_invalid_user(client: TestClient):
    """
    Test get assets for invalid user.

    Args:
        client (TestClient): Test client.
    """
    # Send get request.
    response = client.get("/users/1/portfolio/assets")
    assert response.status_code == 400


def test_get_assets_invalid_portfolio(client: TestClient, user: User):
    """
    Test get assets with invalid portfolio.

    Args:
        client (TestClient): Test client.
    """
    # Send get request.
    response = client.get(f"/users/{user.id}/portfolio/assets")
    assert response.status_code == 400

# - - - - - - - - - - - - - - - - - - -
# CREATE /USERS/{USER_ID}/PORTFOLIO/ASSETS TESTS

def test_create_asset(client: TestClient, portfolio: Portfolio, instrument: Instrument):
    """
    Test creating asset endpoint.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Send request to create asset.
    response = client.post(f"/users/{portfolio.user_id}/portfolio/assets", json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":instrument.id
    })
    asset_json = response.json()
    assert response.status_code == 200
    assert asset_json["instrument_id"] == instrument.id
    assert asset_json["portfolio_id"] == portfolio.id
    assert asset_json["buy_price"] == 1
    assert asset_json["volume"] == 1


def test_create_asset_invalid_user(client: TestClient):
    """
    Test create asset for an invalid user.

    Args:
        client (TestClient): SQL session.
    """
    # Send post request.
    response = client.post(f"/users/1/portfolio/assets/", json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":1
    })
    assert response.status_code == 400


def test_create_asset_invalid_portfolio(client: TestClient, user: User):
    """
    Test create asset for invalid portfolio.

    Args:
        client (TestClient): Test client.
        user (User): Test user.
    """
    # Send post request.
    response = client.post(f"/users/{user.id}/portfolio/assets/",json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":1
    })
    assert response.status_code == 400


def test_create_asset_invalid_instrument(client: TestClient, portfolio: Portfolio):
    """
    Test create asset for invalid instrument.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
    """
    # Send post request.
    response = client.post(f"/users/{portfolio.user_id}/portfolio/assets/",json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":1
    })
    assert response.status_code == 400

# - - - - - - - - - - - - - - - - - - -
# DELETE /USERS/{USER_ID}/PORTFOLIO/ASSETS

def test_delete_assets(client: TestClient, db: Session, portfolio: Portfolio, instrument: Instrument):
    """
    Test delete assets from portfolio.

    Args:
        client (TestClient): Test client.
        db (Session): SQL session.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Send request to create asset.
    for i in range(10):
        response = client.post(f"/users/{portfolio.user_id}/portfolio/assets", json={
            "buy_date":datetime.now().strftime("%d/%m/%Y"),
            "buy_price":1,
            "volume":1,
            "instrument_id":instrument.id
        })
    assets = crud.get_assets_by_portfolio(session=db,portfolio=portfolio)
    assert len(assets) == 10

    # Send delete request.
    response = client.delete(f"/users/{portfolio.user_id}/portfolio/assets")
    deleted_assets_json = response.json()
    assets = crud.get_assets_by_portfolio(session=db,portfolio=portfolio)
    assert response.status_code == 200
    assert len(assets) == 0
    assert len(deleted_assets_json["data"]) == 10


def test_delete_assets_invalid_user(client: TestClient):
    """
    Test delete assets for invalid user.

    Args:
        client (TestClient): Test client.
    """
    # Send delete request.
    response = client.delete("/users/1/portfolio/assets")
    assert response.status_code == 400


def test_delete_assets_invalid_portfolio(client: TestClient, user: User):
    """
    Test delete assets for user with invalid portfolio.

    Args:
        client (TestClient): Test client.
        user (User): Test user.
    """
    # Send delete request.
    response = client.delete(f"/users/{user.id}/portfolio/assets")
    assert response.status_code == 400

# - - - - - - - - - - - - - - - - - - -
# GET /USERS/{USER_ID}/PORTFOLIO/ASSETS/{ASSET_ID} TESTS

def test_get_asset(client: TestClient, portfolio: Portfolio, instrument: Instrument):
    """
    Test getting an asset.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Create asset.
    response = client.post(f"/users/{portfolio.user_id}/portfolio/assets", json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":instrument.id
    })
    create_asset_json = response.json()
    # Send get request.
    response = client.get(f"/users/{portfolio.user_id}/portfolio/assets/{create_asset_json['id']}")
    asset_json = response.json()
    assert response.status_code == 200
    assert asset_json["id"] == create_asset_json["id"]


def test_get_asset_invalid_asset(client: TestClient, portfolio: Portfolio, instrument: Instrument):
    """
    Test get asset for invalid asset.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Send get request.
    response = client.get(f"/users/{portfolio.user_id}/portfolio/assets/1")
    assert response.status_code == 400

# - - - - - - - - - - - - - - - - - - -
# UPDATE /USERS/{USER_ID}/PORTFOLIO/ASSETS/{ASSET_ID} TESTS

def test_update_asset(client: TestClient, portfolio: Portfolio, instrument: Instrument):
    """
    Test updating asset.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Create asset.
    response = client.post(f"/users/{portfolio.user_id}/portfolio/assets", json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":instrument.id
    })
    response_json = response.json()
    
    # Send put request for updating buy price.
    new_buy_price = 2
    response = client.put(f"/users/{portfolio.user_id}/portfolio/assets/{response_json['id']}",json={
        "buy_price":new_buy_price
    })
    updated_asset_json = response.json()
    assert response.status_code == 200
    assert updated_asset_json["buy_price"] == new_buy_price

    # Send put request for updating volume.
    new_volume = 2
    response = client.put(f"/users/{portfolio.user_id}/portfolio/assets/{response_json['id']}",json={
        "volume":new_volume
    })
    updated_asset_json = response.json()
    assert response.status_code == 200
    assert updated_asset_json["volume"] == new_volume

    # Send put request for updating both buy price and volume.
    response = client.put(f"/users/{portfolio.user_id}/portfolio/assets/{response_json['id']}",json={
        "buy_price":1,
        "volume":1
    })
    updated_asset_json = response.json()
    assert response.status_code == 200
    assert updated_asset_json["buy_price"] == 1
    assert updated_asset_json["volume"] == 1

# - - - - - - - - - - - - - - - - - - -
# DELETE /USERS/{USER_ID}/PORTFOLIO/ASSETS/{ASSET_ID} TESTS

def test_delete_asset(client: TestClient, portfolio: Portfolio, instrument: Instrument):
    """
    Test delete asset.

    Args:
        client (TestClient): Test client.
        portfolio (Portfolio): Test portfolio.
        instrument (Instrument): Test instrument.
    """
    # Create asset.
    response = client.post(f"/users/{portfolio.user_id}/portfolio/assets", json={
        "buy_date":datetime.now().strftime("%d/%m/%Y"),
        "buy_price":1,
        "volume":1,
        "instrument_id":instrument.id
    })
    response_json = response.json()

    # Send delete request.
    response = client.delete(f"/users/{portfolio.user_id}/portfolio/assets/{response_json['id']}")
    asset_json = response.json()
    assert response.status_code == 200
    assert asset_json["id"] == response_json["id"]