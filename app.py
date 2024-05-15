from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from io import BytesIO
import base64
from openai import OpenAI 
import tempfile
import os
from dotenv import load_dotenv
from generate_quiz_prompt import generate_quiz_prompt

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SHARED_SECRET = os.getenv('SHARED_SECRET')
model_name = "gpt-4o"

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/quizz', methods=['POST'])
def process_pdf():
    auth_token = request.headers.get('Authorization')
    if auth_token != SHARED_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400


    pdf_file = request.files['pdf_file']
    if pdf_file.filename.split('.')[-1].lower() != 'pdf':
        return jsonify({"error": "File is not a PDF"}), 400

    try:
        first_page = int(request.form.get('first_page', 1))
        last_page = int(request.form.get('last_page', 1))
    except ValueError:
        return jsonify({"error": "Page numbers must be integers"}), 400

    if first_page > last_page:
        return jsonify({"error": "First page cannot be greater than last page"}), 400

    if last_page - first_page > 10:
        return jsonify({"error": "Page range exceeds the maximum allowed of 10 pages"}), 400

    # Save the file to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, secure_filename(pdf_file.filename))
        pdf_file.save(temp_pdf_path)

        pdf_size = pdf_file.tell()

        if pdf_size == 0:
            return jsonify({"error": "PDF file is empty"}), 400

        try:
            images_from_memory = convert_from_path(temp_pdf_path, first_page=first_page,last_page=last_page)
            print("Conversion done: ", pdf_file.filename)
            
            image_messages = []

            # Encode all images to base64 and prepare their message format
            for image in images_from_memory:
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')
                base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                image_messages.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            # Creating the completion request with all images in a single message
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an excelent curriculum designer"},
                    {"role": "user", "content": generate_quiz_prompt()},
                    {"role": "user", "content": image_messages}
                ],
                temperature=0.0,
            )

            print("TOKENS USED:", response.usage.total_tokens,'\n')

            # Return the response from the model
            return jsonify({"summary": response.choices[0].message.content})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
