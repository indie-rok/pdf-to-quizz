from flask import request, jsonify
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from io import BytesIO
import base64
from openai import OpenAI
import tempfile
import os
from generate_quiz_prompt import generate_quiz_prompt
from flask_parameter_validation import ValidateParameters, Form
import logging

from app import app, logger, OPENAI_API_KEY, SHARED_SECRET

model_name = "gpt-4o"
client = OpenAI(api_key=OPENAI_API_KEY)

def validate_auth_token(auth_token):
    if auth_token != SHARED_SECRET:
        return False
    return True

def validate_pdf_file(pdf_file):
    if not pdf_file:
        return "No PDF file provided"
    if pdf_file.filename.split('.')[-1].lower() != 'pdf':
        return "File is not a PDF"
    return None

def validate_pdf_size(pdf_file):
    if pdf_file.tell() == 0:
        return "PDF file is empty"
    return None

def validate_page_range(first_page, last_page):
    if first_page > last_page:
        return "First page cannot be greater than last_page"
    if last_page - first_page > 10:
        return "Page range exceeds the maximum allowed of 10 pages"
    return None

def validate_at_least_one_question(fill_the_blanks, multiple_options, order_the_words):
    if fill_the_blanks + multiple_options + order_the_words == 0:
        return "There should be at least one question"
    return None

def convert_pdf_to_images(pdf_path, first_page, last_page):
    return convert_from_path(pdf_path, first_page=first_page, last_page=last_page)

def encode_images_to_base64(images):
    image_messages = []
    for image in images:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        image_messages.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    return image_messages

def create_chat_completion(client, model_name, image_messages, fill_the_blanks, multiple_options, order_the_words):
    messages = [
        {"role": "system", "content": "You are an excellent curriculum designer"},
        {"role": "user", "content": generate_quiz_prompt(fill_the_blanks, multiple_options, order_the_words)},
        {"role": "user", "content": image_messages}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.0,
    )
    return response

@app.route('/quizz', methods=['POST'])
@ValidateParameters()
def process_pdf(
        first_page: int = Form(min_int=0),
        last_page: int = Form(min_int=1),
        fill_the_blanks: int = Form(min_int=0, max_int=15),
        multiple_options: int = Form(min_int=0, max_int=15),
        order_the_words: int = Form(min_int=0, max_int=15)
    ):
    
    auth_token = request.headers.get('Authorization')
    if not validate_auth_token(auth_token):
        return jsonify({"error": "Unauthorized"}), 401

    pdf_file = request.files.get('pdf_file')
    error = validate_pdf_file(pdf_file)
    if error:
        return jsonify({"error": error}), 400

    error = validate_page_range(first_page, last_page)
    if error:
        return jsonify({"error": error}), 400

    error = validate_at_least_one_question(fill_the_blanks, multiple_options, order_the_words)
    if error:
        return jsonify({"error": error}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, secure_filename(pdf_file.filename))
        pdf_file.save(temp_pdf_path)
        
        error = validate_pdf_size(pdf_file)
        
        if error:
            return jsonify({"error": error}), 400

        try:
            logger.info("CREATING images:", '\n')
            images = convert_pdf_to_images(temp_pdf_path, first_page, last_page)
            image_messages = encode_images_to_base64(images)
            logger.info("SENDING to openai images images:", '\n')
            response = create_chat_completion(client, model_name, image_messages, fill_the_blanks, multiple_options, order_the_words)

            logger.info("TOKENS USED:", response.usage.total_tokens, '\n')

            return jsonify({"summary": response.choices[0].message.content})

        except Exception as e:
            logger.info("quiz with error:", response.choices[0].message.content, '\n')
            return jsonify({"error": str(e)}), 500
