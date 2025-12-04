import boto3
import json
import os
import uuid
from datetime import datetime, timezone
from utils import response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["PRODUCTS_TABLE"])

def lambda_handler(event, context):
    try:
        headers = event.get("headers") or {}
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-Id")
        
        if not tenant_id:
            return response(400, {"error": "Falta x-tenant-id en headers"})

        # TODO: Validar que el usuario sea ADMIN (requiere JWT validation)

        body = json.loads(event.get("body", "{}"))

        # Validar campos requeridos
        required = ["name", "description", "price", "category", "imageUrl"]
        for field in required:
            if not body.get(field):
                return response(400, {"error": f"El campo '{field}' es requerido"})

        product_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "tenant_id": tenant_id,
            "product_id": product_id,
            "name": body["name"],
            "description": body["description"],
            "price": body["price"],
            "originalPrice": body.get("originalPrice"),
            "discount": body.get("discount"),
            "category": body["category"],
            "tag": body.get("tag"),
            "imageUrl": body["imageUrl"],
            "available": body.get("available", True),
            "created_at": now,
            "updated_at": now
        }

        table.put_item(Item=item)

        return response(201, {
            "success": True,
            "message": "Producto creado exitosamente",
            "data": item
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": str(e)})