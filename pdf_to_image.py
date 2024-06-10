import io
import os
import tempfile
import subprocess
from PIL import Image
from flask import request, jsonify
from pdf2image import convert_from_path
import boto3
from botocore.exceptions import NoCredentialsError
import logging

from app import app, logger, S3_BUCKET, AWS_DEFAULT_REGION

s3_client = boto3.client('s3')

def download_from_s3(url):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_filename = os.path.join(temp_dir, 'original.pdf')

    # Download PDF from S3 using curl
    subprocess.run(['curl', '-o', temp_filename, url], check=True)

    return temp_filename

@app.route('/pdf_to_image', methods=['POST'])
def pdf_to_images():
    try:
        data = request.get_json()
        url = data.get('pdf_url')
        file_uuid = data.get('file_uuid')

        if not url or not file_uuid:
            return jsonify({"error": "Missing parameters"}), 400

        temp_pdf_path = download_from_s3(url)
        slides_images_urls = []
        
        images = convert_from_path(temp_pdf_path)

        for page_num, image in enumerate(images):
            # The directory is: <name of the pdf>-num_pages-<number of pages in the pdf>
            directory = file_uuid

            # Then save the image and name it: <name of the pdf>-page<page number>.FMT
            location = f"{directory}/pdf_images/{str(page_num)}.png"
            buffer = io.BytesIO()
            image.save(buffer, 'PNG')
            buffer.seek(0)

            mimetype = 'image/png'
            s3_client.upload_fileobj(
                Fileobj=buffer,
                Bucket=S3_BUCKET,
                Key=location,
                ExtraArgs={
                    "ContentType": mimetype,
                    "ACL":"public-read",
                    "Metadata": {
                        'PAGE_NUMBER': str(page_num),
                        'PAGE_COUNT': str(len(images))
                    }
                }
            )

            prod_url = f"https://{S3_BUCKET}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{location}"

            slides_images_urls.append( { "url": prod_url} )

        return jsonify({"slides": slides_images_urls })

    except Exception as e:
        logger.error("error:", e ,'\n')
        return jsonify({"error": str(e)}), 500
