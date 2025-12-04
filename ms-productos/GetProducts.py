import boto3
import os
from utils import response
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["PRODUCTS_TABLE"])

def lambda_handler(event, context):
    try:
        # Obtener tenant_id
        headers = event.get("headers") or {}
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-Id")
        
        if not tenant_id:
            return response(400, {"error": "Falta x-tenant-id en headers"})

        # Query params opcionales
        query_params = event.get("queryStringParameters") or {}
        category = query_params.get("category")
        
        # Si hay categoría, usar CategoryIndex
        if category:
            resp = table.query(
                IndexName="CategoryIndex",
                KeyConditionExpression=Key("tenant_id").eq(tenant_id) & Key("category").eq(category)
            )
        else:
            # Listar todos los productos del tenant
            resp = table.query(
                KeyConditionExpression=Key("tenant_id").eq(tenant_id)
            )

        items = resp.get("Items", [])
        
        # Ordenar por created_at desc (más recientes primero)
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return response(200, {
            "success": True,
            "data": items,
            "count": len(items)
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": str(e)})