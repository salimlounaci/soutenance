# === Standard Libraries ===
import os
import re
import io
import uuid
import logging
import hashlib
from datetime import datetime
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

import pandas as pd
import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.services.extract_text import extract_text_from_pdf
from src.services.ner_extraction import extract_entities
from src.services.profil_builder import profil_to_text, construire_profil
 

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

def get_connection():
    connection_string = (
        f"DRIVER={{{os.getenv('SQL_DRIVER')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import tempfile

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    try:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex
        extension = os.path.splitext(file.filename)[1]
        blob_filename = f"{timestamp}_{unique_id}{extension}"

        file.seek(0)
        container_client.upload_blob(name=blob_filename, data=file, overwrite=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.seek(0)
            tmp.write(file.read())
            tmp_path = tmp.name

        result = extract_text_from_pdf(tmp_path) 
        df_entities = extract_entities(result)
        profil = construire_profil(df_entities)
        
        global profil_text
        profil_text = profil_to_text(profil)

        print("Texte vectorisé du profil :\n", profil_text)

        return jsonify({
            "blob_filename": blob_filename,
            "extraction": profil_text
        })

    except Exception as e:
        logger.error(f"Erreur globale : {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/offres", methods=["GET"])
def get_offres():
    try:
        conn = get_connection()
        query = """
            SELECT id, intitule, description, dateCreation, typeContrat,
                   lieuTravail_libelle, origineOffre_urlOrigine
            FROM francetravail
        """
        df = pd.read_sql(query, conn)
        conn.close()

        # Colonnes nécessaires
        colonnes_voulues = [
            "intitule", "description", "dateCreation",
            "typeContrat", "lieuTravail_libelle", "origineOffre_urlOrigine"
        ]

        df = df.dropna(subset=["intitule", "description", "lieuTravail_libelle"])
        df["texte"] = (
            df["intitule"].fillna("") + " " +
            df["description"].fillna("") + " " +
            df["lieuTravail_libelle"].fillna("")
        )

        global profil_text
        if not profil_text:
            return jsonify({'error': 'Profil utilisateur non généré'}), 400

        # Vectorisation du profil + offres
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(df["texte"].tolist() + [profil_text])

        profil_vector = X[-1]
        offres_vectors = X[:-1]

        # Similarité cosinus
        scores = cosine_similarity(profil_vector, offres_vectors).flatten()
        df["score"] = scores

        # Trier par score décroissant
        df = df.sort_values(by="score", ascending=False)

        # Ajouter la colonne "score" au JSON retourné
        colonnes_avec_score = colonnes_voulues + ["score"]
        df_filtre = df[colonnes_avec_score]

        return df_filtre.to_json(orient="records", force_ascii=False)

    except Exception as e:
        logger.error(f"Erreur dans /offres : {e}")
        return jsonify({'error': str(e)}), 500


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    prenom = data.get('prenom')
    nom = data.get('nom')
    email = data.get('email')
    password = hash_password(data.get('password'))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (prenom, nom, email, password) VALUES (?, ?, ?, ?)",
                       (prenom, nom, email, password))
        conn.commit()
        return jsonify({"message": "Compte créé avec succès"}), 201
    except pyodbc.IntegrityError:
        return jsonify({"error": "Email déjà utilisé"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = hash_password(data.get('password'))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT prenom, nom FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
    except Exception as e:
        return jsonify({"error": f"Erreur base de données : {str(e)}"}), 500
    finally:
        conn.close()

    if user:
        return jsonify({
            "message": "Connexion réussie",
            "user": {
                "prenom": user[0],
                "nom": user[1],
                "email": email
            }
        })
    else:
        return jsonify({"error": "Email ou mot de passe invalide"}), 401



@app.route("/feedback", methods=["POST"])
def enregistrer_feedback():
    data = request.get_json()
    user_id = data.get("user_id", "test_user")  # par défaut
    offre_id = data.get("offre_id")
    feedback = data.get("feedback")  # "oui" ou "non"

    if not offre_id or feedback not in ["oui", "non"]:
        return jsonify({"error": "offre_id ou feedback invalide"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback_offre (user_id, offre_id, feedback)
            VALUES (?, ?, ?)
        """, (user_id, offre_id, feedback))
        conn.commit()
        conn.close()

        return jsonify({"message": "Feedback enregistré"}), 200

    except Exception as e:
        logger.error(f"Erreur d'enregistrement du feedback : {e}")
        return jsonify({'error': str(e)}), 500

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True, port=5000)