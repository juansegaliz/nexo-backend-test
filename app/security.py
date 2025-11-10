import re, datetime as dt, jwt
from argon2 import PasswordHasher
from config import Settings

from functools import wraps
from flask import request, jsonify


ph = PasswordHasher()

PWD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{7,}$")


def hash_password(pw: str) -> str:
    return ph.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, pw)
    except Exception:
        return False


def is_valid_password(pw: str) -> bool:
    return bool(PWD_RE.match(pw))


def is_adult(birthdate) -> bool:
    today = dt.date.today()
    years = (today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day)))
    return years >= 18


def make_access_token(user_uuid: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": user_uuid,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=Settings.JWT_EXPIRES_MIN)).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, Settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> str | None:
    try:   
        payload = jwt.decode(token, Settings.JWT_SECRET, algorithms=["HS256"])      
        return payload.get("sub")
    except Exception:
        return None


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify(error="Unauthorized"), 401
        sub = decode_access_token(auth.split(" ", 1)[1])
        if not sub:
            return jsonify(error="Unauthorized"), 401
        request.user_uuid = sub  
        return fn(*args, **kwargs)
    return wrapper