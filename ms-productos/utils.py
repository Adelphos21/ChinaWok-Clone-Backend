import json
from decimal import Decimal

def clean_decimals(obj):
    """Convierte Decimals de DynamoDB a int/float para JSON"""
    if isinstance(obj, list):
        return [clean_decimals(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def response(status, body):
    """Respuesta HTTP con headers CORS completos"""
    body = clean_decimals(body)
    
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-tenant-id",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,PATCH,DELETE",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, default=str)
    }