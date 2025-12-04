import boto3
import hashlib
import json
import os
import jwt
from datetime import datetime, timedelta
from utils import response
from boto3.dynamodb.conditions import Attr

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # -------- tenant_id --------
        headers = event.get("headers") or {}
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-Id")
        if not tenant_id:
            return response(400, {"error": "Falta x-tenant-id en headers"})

        # Parsear body
        body = json.loads(event.get("body", "{}"))

        correo = body.get("correo")
        password = body.get("password")

        if not correo or not password:
            return response(400, {"error": "correo y password son obligatorios"})

        hashed_password = hash_password(password)

        # Conectar DynamoDB
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(os.environ["USERS_TABLE"])

        # Buscar por correo dentro del tenant
        resp = table.scan(
            FilterExpression=Attr("tenant_id").eq(tenant_id) & Attr("correo").eq(correo)
        )

        if resp.get("Count", 0) == 0:
            return response(403, {"error": "Usuario no existe en este tenant"})

        usuario = resp["Items"][0]

        # Validar contraseña
        if hashed_password != usuario["password"]:
            return response(403, {"error": "Password incorrecto"})

        # GENERAR JWT
        secret = os.environ["JWT_SECRET"]

        payload = {
            "tenant_id": tenant_id,
            "user_id": usuario["user_id"],
            "correo": usuario["correo"],
            "rol": usuario["rol"],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        return response(200, {
            "message": "Login exitoso",
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": "expira en 1 hora",
            "user": {
                "tenant_id": tenant_id,
                "user_id": usuario["user_id"],
                "correo": usuario["correo"],
                "nombre": usuario.get("nombre", usuario.get("nombres", "")),
                "apellidos": usuario.get("apellidos", ""),
                "dni": usuario.get("dni", ""),
                "rol": usuario["rol"]
            }
        })

    except Exception as e:
        return response(500, {"error": str(e)})
