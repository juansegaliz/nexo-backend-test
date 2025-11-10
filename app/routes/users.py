import os, uuid, datetime as dt
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.extensions import SessionLocal
from app.models import User, AuthLocal
from app.security import hash_password, is_valid_password, is_adult, auth_required
from config import Settings
from sqlalchemy import or_

bp = Blueprint("users", __name__)

def _me(db, user_uuid: str) -> User | None:
    return db.execute(select(User).where(User.user_uuid == user_uuid)).scalars().first()


@bp.get("/users/me")
@auth_required
def me():
    with SessionLocal() as db:
        u = _me(db, request.user_uuid)
        if not u:
            return jsonify(error="Not found"), 404
        a = db.execute(select(AuthLocal).where(AuthLocal.user_id == u.id)).scalars().first()
        return jsonify({
            "user_uuid": u.user_uuid,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "email": a.email if a else None,
            "username": u.username,
            "avatar_url": f"/{u.avatar_path}" if u.avatar_path else None,
            "fecha_nacimiento": u.fecha_nacimiento.isoformat(),
            "created_at": u.created_at.isoformat()
        }), 200


@bp.patch("/users/me")
@auth_required
def me_update():
    data = request.get_json(force=True, silent=False)
    allowed = {"nombre","apellido","email","fecha_nacimiento","username","password"}
    unknown = set(data.keys()) - allowed
    if unknown:
        return jsonify(error=f"Campos no permitidos: {', '.join(sorted(unknown))}"), 422

    with SessionLocal() as db:
        u = _me(db, request.user_uuid)
        if not u:
            return jsonify(error="Not found"), 404
        a = db.execute(select(AuthLocal).where(AuthLocal.user_id == u.id)).scalars().first()

        if "email" in data:
            new_email = data["email"].strip().lower()
            if a and new_email != a.email:
                dup = db.execute(select(AuthLocal.id).where(AuthLocal.email == new_email)).first()
                if dup:
                    return jsonify(error="Email ya registrado"), 409
                a.email = new_email

        if "username" in data:
            new_username = data["username"].strip().lower()
            if new_username != u.username:
                dup = db.execute(select(User.id).where(User.username == new_username)).first()
                if dup:
                    return jsonify(error="Username ya registrado"), 409
                u.username = new_username

        if "nombre" in data: u.nombre = data["nombre"].strip()
        if "apellido" in data: u.apellido = data["apellido"].strip()

        if "fecha_nacimiento" in data:
            try:
                fecha = dt.datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify(error="fecha_nacimiento inválida"), 422
            if not is_adult(fecha):
                return jsonify(error="Debe ser mayor de 18"), 422
            u.fecha_nacimiento = fecha

        if "password" in data:
            if not a:
                return jsonify(error="No tiene credencial local"), 400
            if not is_valid_password(data["password"]):
                return jsonify(error="Password no cumple política"), 422
            a.password_hash = hash_password(data["password"])

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return jsonify(error="Conflicto de unicidad"), 409

        return jsonify(status="ok"), 200


@bp.patch("/users/me/avatar")
@auth_required
def me_avatar():
    if "avatar" not in request.files:
        return jsonify(error="Falta archivo 'avatar'"), 400
    f = request.files["avatar"]

    if not f.mimetype or not f.mimetype.startswith("image/"):
        return jsonify(error="MIME no permitido"), 422
    max_bytes = Settings.MAX_AVATAR_MB * 1024 * 1024
    content_len = request.content_length or 0
    if content_len > max_bytes:
        return jsonify(error="Archivo excede tamaño máximo"), 413

    ext = (os.path.splitext(f.filename)[1] or "").lower()
    if ext not in [".jpg",".jpeg",".png",".gif",".webp"]:
        return jsonify(error="Extensión no permitida"), 422

    today = dt.date.today()
    rel_dir = os.path.join(Settings.UPLOAD_ROOT, f"{today.year}", f"{today.month:02d}")
    os.makedirs(rel_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    rel_path = os.path.join(rel_dir, filename)

    with SessionLocal() as db:
        u = _me(db, request.user_uuid)
        if not u:
            return jsonify(error="Not found"), 404
        f.save(rel_path)
        u.avatar_path = rel_path.replace("\\", "/")
        db.commit()

        return jsonify(avatar_url=f"/{u.avatar_path}"), 200


@bp.get("/users/<user_uuid>")
def user_public(user_uuid: str):
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.user_uuid == user_uuid)).scalars().first()
        if not u:
            return jsonify(error="Not found"), 404
        return jsonify({
            "user_uuid": u.user_uuid,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "username": u.username,
            "avatar_url": f"/{u.avatar_path}" if u.avatar_path else None,
            "created_at": u.created_at.isoformat()
        }), 200


@bp.get("/users/search")
def users_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify(items=[], paging={"next_cursor": None}), 200
    try:
        limit = min(int(request.args.get("limit", 20)), 50)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        return jsonify(error="limit/offset inválidos"), 422

    term = f"%{q.lower()}%"
    with SessionLocal() as db:
        stmt = (
            select(User)
            .outerjoin(AuthLocal, AuthLocal.user_id == User.id)
            .where(
                or_(
                    User.nombre.ilike(term),
                    User.apellido.ilike(term),
                    User.username.ilike(term),
                    AuthLocal.email.ilike(term),
                )
            )
            .order_by(User.created_at.desc())
            .limit(limit + 1)
            .offset(offset)
        )
        rows = db.execute(stmt).scalars().all()
        has_more = len(rows) > limit
        users = rows[:limit]

        items = [{
            "user_uuid": u.user_uuid,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "username": u.username,
            "avatar_url": f"/{u.avatar_path}" if u.avatar_path else None,
        } for u in users]

        next_cursor = offset + limit if has_more else None
        return jsonify(items=items, paging={"next_cursor": next_cursor}), 200