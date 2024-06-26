import os
import shutil
import tempfile
import subprocess
from flask import request, jsonify
from pdf2image import convert_from_path
import boto3

from app import app, logger, S3_BUCKET, AWS_DEFAULT_REGION, SHARED_SECRET

s3_client = boto3.client("s3")

def download_from_s3(url):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_filename = os.path.join(temp_dir, "original.pdf")

    # Download PDF from S3 using curl
    subprocess.run(["curl", "-o", temp_filename, url], check=True)

    return temp_filename


def validate_auth_token(auth_token):
    if auth_token != SHARED_SECRET:
        return False
    return True

@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_images():
    try:
        data = request.get_json()

        auth_token = request.headers.get("Authorization")
        if not validate_auth_token(auth_token):
            return jsonify({"error": "Unauthorized"}), 401

        url = data.get("pdf_url")
        file_uuid = data.get("file_uuid")

        if not url or not file_uuid:
            return jsonify({"error": "Missing parameters"}), 400

        temp_pdf_path = download_from_s3(url)
        slides_images_urls = []

        temp_image_dir = tempfile.mkdtemp()

        images_paths = convert_from_path(
            temp_pdf_path,
            output_folder=temp_image_dir,
            fmt="jpeg",
            jpegopt={"quality": 10, "optimize": "y"},
            paths_only=True,
            thread_count=4,
            use_pdftocairo=True,
        )

        for page_number, image_path in enumerate(images_paths):
            image_filename = os.path.basename(image_path)
            directory = file_uuid
            aws_location = f"{directory}/pdf_images/{image_filename}"

            with open(image_path, "rb") as f:
                mimetype = "image/jpeg"
                s3_client.upload_fileobj(
                    Fileobj=f,
                    Bucket=S3_BUCKET,
                    Key=aws_location,
                    ExtraArgs={
                        "ContentType": mimetype,
                        "ACL": "public-read",
                        "Metadata": {
                            'PAGE_NUMBER': str(page_number),
                            'PAGE_COUNT': str(len(images_paths))
                        }
                    },
                )

            prod_url = f"https://{S3_BUCKET}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{aws_location}"
            slides_images_urls.append({"url": prod_url})

        os.remove(temp_pdf_path)
        shutil.rmtree(temp_image_dir)

        return jsonify({"slides": slides_images_urls})

    except Exception as e:
        logger.error("error:", e, "\n")
        return jsonify({"error": str(e)}), 500
