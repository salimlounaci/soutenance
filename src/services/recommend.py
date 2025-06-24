import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
load_dotenv()

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

def recommander_offres(profil_text, top_n=1000):
    try:
        conn = get_connection()
        query = """
            SELECT id, intitule, description, lieuTravail_libelle
            FROM francetravail
            WHERE intitule IS NOT NULL AND description IS NOT NULL AND lieuTravail_libelle IS NOT NULL
        """
        offres = pd.read_sql(query, conn)
        conn.close()

        print("Nb offres chargées depuis la base :", offres.shape[0])
        print("Profil text utilisé :", profil_text[:200])

        # Construction du champ texte concaténé pour vectorisation
        offres["texte"] = (
            offres["intitule"].fillna("") + " " +
            offres["description"].fillna("") + " " +
            offres["lieuTravail_libelle"].fillna("")
        )

        # Vectorisation TF-IDF
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(offres["texte"].tolist() + [profil_text])

        profil_vector = X[-1]
        offres_vectors = X[:-1]

        # Calcul des similarités cosinus
        scores = cosine_similarity(profil_vector, offres_vectors).flatten()
        offres["score"] = scores

        # Sélection des offres les plus pertinentes
        top = offres.sort_values(by="score", ascending=False).head(top_n)

        return top[["id", "intitule", "score", "lieuTravail_libelle"]]

    except Exception as e:
        return pd.DataFrame() 


def ajuster_scores_par_feedback(df, user_id="test_user"):
    conn = get_connection()
    feedback = pd.read_sql(f"""
        SELECT offre_id, feedback FROM feedback_offre
        WHERE user_id = '{user_id}'
    """, conn)
    conn.close()

    # Merge feedback dans les offres
    df = df.merge(feedback, how="left", left_on="id", right_on="offre_id")

    # Ajustement : -1 pour "non", +1 pour "oui"
    df["score_adjusted"] = df["score"]
    df.loc[df["feedback"] == "oui", "score_adjusted"] += 1.0
    df.loc[df["feedback"] == "non", "score_adjusted"] -= 1.0

    df = df.sort_values(by="score_adjusted", ascending=False)
    return df
