# utils.py
import json
from decimal import Decimal

def clean_decimals(obj):
    if isinstance(obj, list):
        return [clean_decimals(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


def response(status, body):
    body = clean_decimals(body)
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": (
                "Content-Type,X-Amz-Date,Authorization,X-Api-Key,"
                "X-Amz-Security-Token,x-tenant-id"
            ),
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE,PATCH",
        },
        "body": json.dumps(body, default=str),
    }