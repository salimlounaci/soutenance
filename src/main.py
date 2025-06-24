import argparse
from services.extract_text import extract_text_from_pdf
from services.ner_extraction import extract_entities
from services.profil_builder import construire_profil, profil_to_text
from services.recommend import recommander_offres

def main():
    parser = argparse.ArgumentParser(description="Pipeline CV → Recommandation")
    parser.add_argument("--pdf_path", required=True, help="Chemin vers le fichier PDF du CV")
    args = parser.parse_args()

    print("Extraction texte...")
    text = extract_text_from_pdf(args.pdf_path)

    print("Extraction des entités NER...")
    df_entities = extract_entities(text)
    print(df_entities)

    print("Construction du profil...")
    profil = construire_profil(df_entities)
    profil_text = profil_to_text(profil)
    print("Texte vectorisé du profil :\n", profil_text)

    print("Offres recommandées :")
    recommandations = recommander_offres(profil_text)
    print(recommandations)

if __name__ == "__main__":
    main()
