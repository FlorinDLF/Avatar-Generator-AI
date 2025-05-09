import os
import base64
import requests
import uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from deepface import DeepFace

# Incarca cheia API din .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configurare Flask
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/download/<filename>")
def download_avatar(filename):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

@app.route("/upload_and_generate_avatar", methods=["POST"])
def upload_and_generate_avatar():
    if 'image' not in request.files or 'style' not in request.form:
        return jsonify({"error": "Trebuie să trimiți o imagine și să selectezi un stil."}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{base64_image}"

    style = request.form['style'].lower()
    
    style_descriptions = {
        "cartoon": (
            "in exaggerated cartoon style similar to Bitmoji, with large expressive eyes, flat colors, clean outlines, "
            "simple shading, and playful features"
        ),
        "anime": (
            "in Japanese anime style with sharp linework, glossy large eyes, smooth shadows, stylized hair and clothing, "
            "like a character from a modern anime series"
        ),
        "pixar": (
            "in Pixar-style 3D animation, with rounded facial features, detailed textures, expressive eyes, soft lighting, "
            "and childlike proportions similar to characters from Luca or Turning Red"
        ),
        "3d": (
            "in flat stylized 3D cartoon style, toy-like appearance, shiny plastic materials, simple color palette, "
            "and minimal realistic features"
        )
    }

    style_prompt = style_descriptions.get(style, "in stylized digital art style")

    if style not in ["cartoon", "anime", "pixar", "3d"]:
        return jsonify({"error": "Stil invalid. Alege între: cartoon, anime, pixar, 3D."}), 400

    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4().hex}.jpg")
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        rezultat = DeepFace.analyze(
            img_path=temp_path,
            actions=["age", "gender", "emotion", "race"],
            enforce_detection=False
        )[0]

        sex = rezultat.get("dominant_gender", "necunoscut")
        age = rezultat.get("age", "necunoscut")
        emotion = rezultat.get("dominant_emotion", "necunoscut")
        ethnicity = rezultat.get("dominant_race", "necunoscut")

        print(f"Sex: {sex}, Vârstă: {age}, Emoție: {emotion}, Etnie: {ethnicity}")

        descriere_extra = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Descrie hainele, fundalul, accesoriile si parul facial ale unei persoane dintr-o imagine."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analizează această imagine și descrie hainele, fundalul, accesoriile și parul facial."},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                    ]
                }
            ],
            max_tokens=300
        )

        descriere_text = descriere_extra.choices[0].message.content.strip()

        print("\n===== DESCRIERE GPT (haine, fundal, etc) =====")
        print(descriere_text)
        print("===== SFÂRȚIT DESCRIERE GPT =====\n")

        if "nu pot" in descriere_text.lower() or "i'm sorry" in descriere_text.lower():
            descriere_text = "Vestimentație casual, fundal neutru, fără accesorii vizibile."

        final_prompt = (
            f"Stylized avatar of a person {style_prompt}: A {sex}, around {age} years old, "
            f"with {emotion} facial expression, and {ethnicity} ethnicity. {descriere_text}. "
            f"Upper body portrait, centered, white background, colorful and artistic."
        )


        print("===== PROMPT FINAL CĂTRE DALL-E =====")
        print(final_prompt)
        print("===== SFÂRȚIT PROMPT =====\n")

        dalle_response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1024x1024"
        )

        image_url = dalle_response.data[0].url

        image_data = requests.get(image_url).content
        filename = f"avatar_{style}_{uuid.uuid4().hex[:8]}.png"
        save_path = os.path.join(PROCESSED_FOLDER, filename)
        with open(save_path, "wb") as f:
            f.write(image_data)

        return jsonify({
            "style": style,
            "local_path": f"/processed/{filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route("/processed/<filename>")
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route("/")
def home():
    return "Serverul funcționează. Folosește /upload_and_generate_avatar pentru a genera un avatar."

if __name__ == '__main__':
    app.run(debug=True)
