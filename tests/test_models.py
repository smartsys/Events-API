import pytest
from sqlalchemy.exc import IntegrityError
from app import create_app
from models import db, User


@pytest.fixture
def app():
    """Flask-App mit In-Memory-Datenbank."""
    app = create_app()
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def user(app):
    """Gespeicherter Test-User."""
    user = User(username='john_doe')
    user.set_password('securepassword123')
    db.session.add(user)
    db.session.commit()
    return user


def test_user_password_hashing_behaves_correctly():
    """Passwort wird gehasht, richtiges akzeptiert, falsches abgelehnt."""
    user = User(username='john_doe')
    user.set_password('securepassword123')
    assert user.password_hash != 'securepassword123'
    assert user.check_password('securepassword123')
    assert not user.check_password('wrongpassword')


def test_is_admin_default_false(user):
    """Neuer User ist standardmäßig kein Admin."""
    assert user.is_admin is False


def test_username_unique(user):
    """Username darf nur einmal vergeben werden."""
    duplicate = User(username='john_doe')
    duplicate.set_password('password123')
    db.session.add(duplicate)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_to_dict(user):
    """to_dict liefert die erwarteten Felder ohne Passwort-Hash."""
    data = user.to_dict()
    assert data['id'] == user.id
    assert data['username'] == 'john_doe'
    assert data['is_admin'] is False
    assert data['created_at'] is not None
    assert 'password_hash' not in data
