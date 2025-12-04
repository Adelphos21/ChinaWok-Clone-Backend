import boto3
import json
import os
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

        product_id = (event.get("pathParameters") or {}).get("product_id")
        if not product_id:
            return response(400, {"error": "product_id es requerido"})

        body = json.loads(event.get("body", "{}"))

        # Verificar que el producto existe
        resp = table.get_item(Key={"tenant_id": tenant_id, "product_id": product_id})
        if "Item" not in resp:
            return response(404, {"error": "Producto no encontrado"})

        # Construir UpdateExpression dinámicamente
        update_expr = "SET updated_at = :updated_at"
        expr_values = {":updated_at": datetime.now(timezone.utc).isoformat()}
        expr_names = {}

        updatable_fields = ["name", "description", "price", "originalPrice", "discount", "category", "tag", "imageUrl", "available"]
        
        for field in updatable_fields:
            if field in body:
                update_expr += f", #{field} = :{field}"
                expr_values[f":{field}"] = body[field]
                expr_names[f"#{field}"] = field

        table.update_item(
            Key={"tenant_id": tenant_id, "product_id": product_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names if expr_names else None
        )

        return response(200, {
            "success": True,
            "message": "Producto actualizado exitosamente"
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": str(e)})