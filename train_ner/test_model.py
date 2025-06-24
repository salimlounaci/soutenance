import spacy
import fitz  # PyMuPDF
import pandas as pd
import argparse
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

import spacy
import fitz  # PyMuPDF
import pandas as pd
import argparse
import pytesseract
from PIL import Image
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            text += page_text
        else:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img, lang='fra')
            text += ocr_text

    return text


def construire_profil(df):
    profil = {
        "PERSON": [],
        "JOB": [],
        "COMPANY": [],
        "EMAIL": [],
        "PHONE": [],
        "ADDRESS": [],
        "SKILL": []
    }

    for _, row in df.iterrows():
        label = row["Label"]
        texte = row["Texte"].strip()
        if label in profil:
            profil[label].append(texte)

    return profil


def profil_to_text(profil):
    texte = (
        " ".join(profil.get("JOB", [])) + " " +
        " ".join(profil.get("SKILL", [])) + " " +
        " ".join(profil.get("ADDRESS", [])) + " " +
        " ".join(profil.get("COMPANY", []))
    )
    return texte


def recommander_offres(profil_text, fichier_offres="offres.csv", top_n=5):
    offres = pd.read_csv(fichier_offres)
    offres["texte"] = offres["intitule"] + " " + offres["description"] + " " + offres["lieuTravail_libelle"]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(offres["texte"].tolist() + [profil_text])

    profil_vector = X[-1]
    offres_vectors = X[:-1]

    scores = cosine_similarity(profil_vector, offres_vectors).flatten()
    offres["score"] = scores

    top = offres.sort_values(by="score", ascending=False).head(top_n)
    return top[["id", "intitule", "description","score", "lieuTravail_libelle"]]

def main():
    parser = argparse.ArgumentParser(description="Extraction des entités depuis un CV en PDF")
    parser.add_argument("--pdf_path", required=True, help="Chemin vers le fichier PDF")
    args = parser.parse_args()

    text = extract_text_from_pdf(args.pdf_path)

    nlp = spacy.load("cv_ner_model_V3")
    doc = nlp(text)

    entities = [(ent.text, ent.label_) for ent in doc.ents]
    df = pd.DataFrame(entities, columns=["Texte", "Label"])
    print("Entités extraites :")
    print(df)

    profil = construire_profil(df)
    profil_text = profil_to_text(profil)

    print("\nProfil vectorisé :")
    print(profil_text)

    print("\nOffres recommandées :")
    recommandations = recommander_offres(profil_text)
    print(recommandations)


if __name__ == "__main__":
    main()
