from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.extensions import SessionLocal
from app.models import User, AuthLocal
from app.security import hash_password, verify_password, is_valid_password, is_adult, make_access_token

bp = Blueprint("auth", __name__)

@bp.post("/auth/register")
def register():
    data = request.get_json(force=True, silent=False)
    required = ["nombre", "apellido", "email", "fecha_nacimiento", "username", "password"]
    if not all(k in data for k in required):
        return jsonify(error="Faltan campos"), 400

    try:
        fecha = datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify(error="fecha_nacimiento inválida"), 422
    if not is_adult(fecha):
        return jsonify(error="Debe ser mayor de 18"), 422
    if not is_valid_password(data["password"]):
        return jsonify(error="Password no cumple política"), 422
    email = data["email"].strip().lower()
    username = data["username"].strip().lower()

    with SessionLocal() as db:
        exists_email = db.execute(select(AuthLocal.id).where(AuthLocal.email == email)).first()
        if exists_email:
            return jsonify(error="Email ya registrado"), 409

        exists_username = db.execute(select(User.id).where(User.username == username)).first()
        if exists_username:
            return jsonify(error="Username ya registrado"), 409
        try:
            u = User(nombre=data["nombre"].strip(), apellido=data["apellido"].strip(), username=username, fecha_nacimiento=fecha,)
            db.add(u)
            db.flush()  
            a = AuthLocal(user_id=u.id, email=email, password_hash=hash_password(data["password"]),)
            db.add(a)
            db.commit()
            db.refresh(u)
        except IntegrityError:
            db.rollback()
            return jsonify(error="Conflicto de unicidad"), 409
        return jsonify(user_uuid=u.user_uuid), 201


@bp.post("/auth/login")
def login():
    data = request.get_json(force=True, silent=False)

    if not data or "email" not in data or "password" not in data:
        return jsonify(error="Credenciales faltantes"), 400

    email = data["email"].strip().lower()

    with SessionLocal() as db:
        a = db.execute(select(AuthLocal).where(AuthLocal.email == email)).scalars().first()

        if not a or not verify_password(data["password"], a.password_hash):
            return jsonify(error="Credenciales inválidas"), 401

        user = a.user
        token = make_access_token(user.user_uuid)
        me = {
            "user_uuid": user.user_uuid,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "email": a.email,
            "username": user.username,
        }
        
        return jsonify(access_token=token, user=me), 200


@bp.post("/auth/logout")
def logout():
    return jsonify(status="ok"), 200
