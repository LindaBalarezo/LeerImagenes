from flask import Flask, render_template, request
import requests

app = Flask(__name__)

VISION_KEY = '37JKlfyAQXBr4CcFLjrvTCuLImwCGsJSIiCtwIdXZZkn4HZ55zJLJQQJ99BGAC4f1cMXJ3w3AAAFACOGpIxK'
VISION_ENDPOINT = 'https://lkbc-cv-2025-3.cognitiveservices.azure.com/'

@app.route("/", methods=["GET", "POST"])
def index():
    description = ""
    language = ""
    if request.method == "POST":
        image_file = request.files.get("image_file")
        image_url = request.form.get("image_url", "").strip()

        headers = {
            "Ocp-Apim-Subscription-Key": VISION_KEY,
        }

        # Opción 1: Si se subió una imagen desde el PC
        if image_file and image_file.filename != "":
            headers["Content-Type"] = "application/octet-stream"
            image_data = image_file.read()

            response = requests.post(
                VISION_ENDPOINT + "/vision/v3.2/ocr",
                headers=headers,
                data=image_data
            )

        # Opción 2: Si se ingresó una URL
        elif image_url:
            headers["Content-Type"] = "application/json"
            data = {"url": image_url}

            response = requests.post(
                VISION_ENDPOINT + "/vision/v3.2/ocr",
                headers=headers,
                json=data
            )
        else:
            description = "Debes subir una imagen o proporcionar una URL."
            language = "desconocido"
            return render_template("index.html", description=description, language=language)

        # Procesamiento de la respuesta
        if response.status_code == 200:
            result = response.json()
            lines = []
            for region in result.get("regions", []):
                for line in region.get("lines", []):
                    text_line = " ".join([word["text"] for word in line["words"]])
                    lines.append(text_line)
            description = "\n".join(lines) if lines else "No se detectó texto."
            language = result.get("language", "desconocido")
        else:
            description = f"Error en la API: {response.status_code} - {response.text}"
            language = "desconocido"

    return render_template("index.html", description=description, language=language)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
