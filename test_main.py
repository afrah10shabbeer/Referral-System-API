from fastapi.testclient import TestClient
import pytest
from main import app
from fastapi import HTTPException,exceptions
from unittest.mock import MagicMock, patch
import mysql.connector

client = TestClient(app)

def replace_do_something():
    raise Exception()
    return

def test_register_user():
    # Define user data for registration
    user_data = {
        "name": "lob Doe",
        "email": "lob.doe@example.com",
        "password": "secretpassword",
        "referral_code": "REF1234"
    }

    response = client.post("/register/",json=user_data)

    assert response.status_code == 200
    assert response.json() == {"message":f"Registration Successful! Your unique ID is: {1}"}


def test_register_user_duplicate():
    # Define user data for registration
    user_data = {
        "name": "lob Doe",
        "email": "lob.doe@example.com",
        "password": "secretpassword",
        "referral_code": "REF1234"
    }

    with pytest.raises(HTTPException) as e:
        client.post("/register/", json=user_data)
    
    assert e.type == HTTPException

    


    
    