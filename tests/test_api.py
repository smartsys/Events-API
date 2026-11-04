import requests

EVENT_DATA = {
    'title': 'Test Event',
    'description': 'Event aus den Integrationstests',
    'date': '2026-12-24T18:00:00',
    'location': 'Berlin',
}


def create_event(base_url, token, **fields):
    """Legt ein Event an und gibt die Antwort zurück."""
    return requests.post(
        f'{base_url}/events',
        json={**EVENT_DATA, **fields},
        headers={'Authorization': f'Bearer {token}'},
    )


def test_health_endpoint_returns_healthy(base_url):
    """Health-Endpunkt meldet eine fehlerfreie API."""
    response = requests.get(f'{base_url}/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_register_user_creates_new_user(base_url, unique_username):
    """Registrierung legt einen neuen User an."""
    response = requests.post(
        f'{base_url}/auth/register',
        json={'username': unique_username, 'password': 'securepassword123'},
    )
    assert response.status_code == 201
    assert response.json()['user']['username'] == unique_username


def test_login_returns_jwt_token(base_url, unique_username):
    """Login mit bekanntem User liefert ein Access-Token."""
    credentials = {'username': unique_username, 'password': 'securepassword123'}
    requests.post(f'{base_url}/auth/register', json=credentials)
    response = requests.post(f'{base_url}/auth/login', json=credentials)
    assert response.status_code == 200
    assert response.json()['access_token']


def test_create_public_event_requires_auth_and_succeeds_with_token(base_url, auth_token):
    """Event wird mit gültigem Token angelegt."""
    response = create_event(base_url, auth_token)
    assert response.status_code == 201
    event = response.json()
    assert event['title'] == EVENT_DATA['title']
    assert event['description'] == EVENT_DATA['description']
    assert event['date'] == EVENT_DATA['date']
    assert event['location'] == EVENT_DATA['location']
    assert event['is_public'] is True


def test_rsvp_to_public_event_succeeds(base_url, auth_token):
    """RSVP zu einem öffentlichen Event ist erfolgreich."""
    event_id = create_event(base_url, auth_token).json()['id']
    response = requests.post(
        f'{base_url}/rsvps/event/{event_id}',
        json={'attending': True},
        headers={'Authorization': f'Bearer {auth_token}'},
    )
    assert response.status_code == 201
    assert response.json()['event_id'] == event_id
    assert response.json()['attending'] is True


def test_register_duplicate_username_returns_400(base_url, unique_username):
    """Zweite Registrierung mit gleichem Username schlägt fehl."""
    credentials = {'username': unique_username, 'password': 'securepassword123'}
    first = requests.post(f'{base_url}/auth/register', json=credentials)
    second = requests.post(f'{base_url}/auth/register', json=credentials)
    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()['error'] == 'Username already exists'


def test_create_event_without_auth_returns_401(base_url):
    """Event anlegen ohne Token wird abgelehnt."""
    response = requests.post(f'{base_url}/events', json=EVENT_DATA)
    assert response.status_code == 401


def test_rsvp_to_private_event_without_auth_returns_401(base_url, auth_token):
    """RSVP zu einem nicht-öffentlichen Event ohne Token wird abgelehnt."""
    event_id = create_event(base_url, auth_token, is_public=False).json()['id']
    response = requests.post(f'{base_url}/rsvps/event/{event_id}', json={'attending': True})
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication required for this event'
