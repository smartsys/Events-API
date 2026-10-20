import os
import time
import pytest
import requests

# Muss vor dem Import der App gesetzt werden, damit nicht die echte Datenbank benutzt wird
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

BASE_URL = 'http://localhost:5000/api'


@pytest.fixture
def base_url():
    """Basis-URL der laufenden Events-API."""
    return BASE_URL


@pytest.fixture
def unique_username():
    """Eindeutiger Username mit Zeitstempel."""
    return f'user_{time.time_ns()}'


@pytest.fixture
def auth_token(base_url, unique_username):
    """Registriert einen User, meldet ihn an und gibt das JWT-Token zurück."""
    credentials = {'username': unique_username, 'password': 'securepassword123'}
    requests.post(f'{base_url}/auth/register', json=credentials)
    response = requests.post(f'{base_url}/auth/login', json=credentials)
    return response.json()['access_token']
