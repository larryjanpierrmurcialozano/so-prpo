import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from backend.models import User

def test_password_hash():
    u = User()
    u.username = 'testuser'
    u.email = 'test@example.com'
    u.set_password('secret')
    assert u.check_password('secret')
    assert not u.check_password('wrong')
