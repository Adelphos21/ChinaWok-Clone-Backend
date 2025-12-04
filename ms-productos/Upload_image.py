# lambda_upload_image.py
import boto3
import json
import os
import uuid
from datetime import datetime
from utils import response
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['IMAGES_BUCKET']  # ej: "chinawok-product-images"

def lambda_handler(event, context):
    try:
        headers = event.get("headers") or {}
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-Id")
        
        if not tenant_id:
            return response(400, {"error": "Falta x-tenant-id en headers"})
                

        # Obtener el nombre y tipo del archivo
        body = json.loads(event.get("body", "{}"))
        file_name = body.get("fileName", "image.jpg")
        content_type = body.get("contentType", "image/jpeg")
        
        # Validar tipo de archivo
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if content_type not in allowed_types:
            return response(400, {"error": "Tipo de archivo no permitido. Solo JPG, PNG, WEBP"})
            
        
        # Generar nombre único para el archivo
        file_extension = file_name.split('.')[-1]
        unique_filename = f"{tenant_id}/products/{uuid.uuid4()}.{file_extension}"
        
        # Generar URL prefirmada para subir (válida por 5 minutos)
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': unique_filename,
                'ContentType': content_type
            },
            ExpiresIn=300  # 5 minutos
        )
        
        # URL pública del archivo (después de subirlo)
        public_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        
        return response(200, {'uploadUrl': presigned_url,
                'publicUrl': public_url,
                'key': unique_filename})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500,{"error": str(e)})
        