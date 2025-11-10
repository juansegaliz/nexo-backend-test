from flask import Blueprint, request, jsonify
from sqlalchemy import select, or_
from app.extensions import SessionLocal
from app.models import User, Friendship
from app.security import auth_required


bp = Blueprint("friends", __name__)


def _by_uuid(db, user_uuid:str) -> User | None:
    return db.execute(select(User).where(User.user_uuid == user_uuid)).scalars().first()

def _norm(a:int, b:int) -> tuple[int,int]:
    return (a, b) if a < b else (b, a)


@bp.get("/friends")
@auth_required
def list_friends():
    status = request.args.get("status")
    with SessionLocal() as db:
        me = db.execute(select(User).where(User.user_uuid == request.user_uuid)).scalars().first()
        if not me:
            return jsonify(error="Not found"), 404
        q = select(Friendship).where(or_(Friendship.user_low_id==me.id, Friendship.user_high_id==me.id))
        if status:
            q = q.where(Friendship.status == status)
        rows = db.execute(q.order_by(Friendship.updated_at.desc())).scalars().all()

        def serialize(fs: Friendship):            
            other_id = fs.user_high_id if fs.user_low_id == me.id else fs.user_low_id
            other = db.get(User, other_id)
            return {
                "user_uuid": other.user_uuid,
                "nombre": other.nombre,
                "apellido": other.apellido,
                "username": other.username,
                "status": fs.status,
                "requested_by_me": (fs.requested_by_id == me.id)
            }

        return jsonify(items=[serialize(fs) for fs in rows]), 200


@bp.post("/friends/request")
@auth_required
def request_friend():
    data = request.get_json(force=True)
    to_uuid = data.get("to_user_uuid")
    if not to_uuid:
        return jsonify(error="to_user_uuid requerido"), 400
    with SessionLocal() as db:
        me = _by_uuid(db, request.user_uuid)
        other = _by_uuid(db, to_uuid)
        if not me or not other:
            return jsonify(error="Not found"), 404
        if me.id == other.id:
            return jsonify(error="No se permite self-request"), 400
        low, high = _norm(me.id, other.id)
        fs = db.execute(select(Friendship).where(
            Friendship.user_low_id==low, Friendship.user_high_id==high
        )).scalars().first()
        if not fs:
            fs = Friendship(user_low_id=low, user_high_id=high, status="pending", requested_by_id=me.id)
            db.add(fs)
            db.commit()
            return jsonify(status="pending"), 201
        if fs.status in ("rejected", "removed"):
            fs.status = "pending"
            fs.requested_by_id = me.id
            db.commit()
            return jsonify(status="pending"), 200

        return jsonify(status=fs.status), 200


@bp.post("/friends/accept")
@auth_required
def accept_friend():
    data = request.get_json(force=True)
    from_uuid = data.get("user_uuid")
    if not from_uuid:
        return jsonify(error="user_uuid requerido"), 400
    with SessionLocal() as db:
        me = _by_uuid(db, request.user_uuid)
        other = _by_uuid(db, from_uuid)
        if not me or not other:
            return jsonify(error="Not found"), 404
        low, high = _norm(me.id, other.id)
        fs = db.execute(select(Friendship).where(
            Friendship.user_low_id==low, Friendship.user_high_id==high
        )).scalars().first()
        if not fs or fs.status != "pending":
            return jsonify(error="No hay solicitud pendiente"), 409         
        if me.id == fs.requested_by_id:
            return jsonify(error="Solo el receptor puede aceptar"), 403
        fs.status = "accepted"
        db.commit()
        return jsonify(status="accepted"), 200


@bp.post("/friends/reject")
@auth_required
def reject_friend():
    data = request.get_json(force=True)
    from_uuid = data.get("user_uuid")
    if not from_uuid:
        return jsonify(error="user_uuid requerido"), 400
    with SessionLocal() as db:
        me = _by_uuid(db, request.user_uuid)
        other = _by_uuid(db, from_uuid)
        if not me or not other:
            return jsonify(error="Not found"), 404
        low, high = _norm(me.id, other.id)
        fs = db.execute(select(Friendship).where(
            Friendship.user_low_id==low, Friendship.user_high_id==high
        )).scalars().first()
        if not fs or fs.status != "pending":
            return jsonify(error="No hay solicitud pendiente"), 409
        if me.id == fs.requested_by_id:
            return jsonify(error="Solo el receptor puede rechazar"), 403
        fs.status = "rejected"
        db.commit()
        return jsonify(status="rejected"), 200


@bp.post("/friends/unfriend")
@auth_required
def unfriend():
    data = request.get_json(force=True)
    user_uuid = data.get("user_uuid")
    if not user_uuid:
        return jsonify(error="user_uuid requerido"), 400
    with SessionLocal() as db:
        me = _by_uuid(db, request.user_uuid)
        other = _by_uuid(db, user_uuid)
        if not me or not other:
            return jsonify(error="Not found"), 404  
        low, high = _norm(me.id, other.id)
        fs = db.execute(select(Friendship).where(
            Friendship.user_low_id==low, Friendship.user_high_id==high
        )).scalars().first()
        if not fs:
            return jsonify(status="removed"), 200  
        if fs.status == "accepted":
            fs.status = "removed"
            db.commit()
            return jsonify(status="removed"), 200
        return jsonify(status=fs.status), 200
