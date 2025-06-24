import spacy
from spacy.training.example import Example
from spacy.training.iob_utils import offsets_to_biluo_tags
from spacy.scorer import Scorer
import json
import random
from pathlib import Path
from sklearn.model_selection import train_test_split

# === Chargement brut des données JSON ===
with open("cv_data_final.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# === Prétraitement : nettoyage des entités non alignées ===
nlp_tmp = spacy.blank("fr")  # temporaire pour vérifier alignement
cleaned_data = []

for sample in raw_data:
    text = sample["text"]
    valid_entities = []
    for start, end, label in sample["entities"]:
        span = nlp_tmp.make_doc(text).char_span(start, end, label=label)
        if span is not None:
            valid_entities.append([start, end, label])
        else:
            print(f"⚠️ Entité ignorée (non alignée) : '{text[start:end]}' ({start}-{end}, {label})")
    if valid_entities:
        cleaned_data.append((text, {"entities": valid_entities}))

print(f"\n✅ Total exemples valides : {len(cleaned_data)}")

# === Split en train/test ===
train_data, test_data = train_test_split(cleaned_data, test_size=0.1, random_state=42)

# === Création du modèle vierge ===
nlp = spacy.blank("fr")

# === Ajout du pipeline NER ===
ner = nlp.add_pipe("ner")

# === Ajout des labels au composant NER ===
for _, ann in train_data:
    for start, end, label in ann["entities"]:
        ner.add_label(label)

# === Initialisation (spaCy 3+) ===
nlp.initialize()

# === Entraînement ===
best_loss = float("inf")
output_dir = Path("cv_ner_model_V2")
output_dir.mkdir(exist_ok=True)

def evaluate_model(nlp, examples):
    scorer = Scorer()
    eval_examples = []
    for text, ann in examples:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, ann)
        pred = nlp(text)
        example.predicted = pred
        eval_examples.append(example)
    return scorer.score(eval_examples)

for epoch in range(35):
    print(f"\n🔁 Epoch {epoch+1}")
    random.shuffle(train_data)
    losses = {}

    for text, ann in train_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, ann)
        nlp.update([example], drop=0.2, losses=losses)

    print("📉 Losses:", losses)

    # Évaluation tous les 10 epochs
    if (epoch + 1) % 10 == 0:
        scores = evaluate_model(nlp, test_data)
        print(f"📊 Precision: {scores['ents_p']:.2f} | Recall: {scores['ents_r']:.2f} | F1: {scores['ents_f']:.2f}")

    # Sauvegarde du meilleur modèle
    if losses.get("ner", float("inf")) < best_loss:
        best_loss = losses["ner"]
        nlp.to_disk(output_dir)
        print(f"✅ Nouveau meilleur modèle sauvegardé (loss: {best_loss:.2f})")

print(f"\n🎉 Entraînement terminé. Meilleur modèle sauvegardé dans {output_dir}")
