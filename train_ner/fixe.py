import json
import spacy
from spacy.training import offsets_to_biluo_tags
from tqdm import tqdm

# Charge ton modèle spaCy (langue française ici)
nlp = spacy.blank("fr")

def is_entity_aligned(text, entities):
    """Vérifie si toutes les entités sont bien alignées avec les tokens du texte"""
    doc = nlp.make_doc(text)
    try:
        tags = offsets_to_biluo_tags(doc, entities)
        return "-" not in tags
    except:
        return False

def clean_dataset(input_json_path, output_json_path):
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    for entry in tqdm(data, desc="Nettoyage"):
        text = entry["text"]
        entities = entry.get("entities", [])

        # On vérifie les entités une par une
        valid_entities = []
        for start, end, label in entities:
            try:
                substring = text[start:end]
                doc = nlp.make_doc(text)
                biluo = offsets_to_biluo_tags(doc, [[start, end, label]])
                if "-" not in biluo:
                    valid_entities.append([start, end, label])
            except:
                continue

        # Ajoute l'entrée uniquement si elle a des entités valides
        if valid_entities:
            cleaned_data.append({
                "text": text,
                "entities": valid_entities
            })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Dataset nettoyé enregistré dans : {output_json_path}")

clean_dataset("cv_train_data.json", "cleaned_dataset.json")
