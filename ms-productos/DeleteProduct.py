import boto3
import os
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

        # Verificar que existe
        resp = table.get_item(Key={"tenant_id": tenant_id, "product_id": product_id})
        if "Item" not in resp:
            return response(404, {"error": "Producto no encontrado"})

        # Eliminar
        table.delete_item(Key={"tenant_id": tenant_id, "product_id": product_id})

        return response(200, {
            "success": True,
            "message": "Producto eliminado exitosamente"
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": str(e)})