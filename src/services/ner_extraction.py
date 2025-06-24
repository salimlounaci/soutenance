import spacy
import pandas as pd

def extract_entities(text, model_path="cv_ner_model_V3"):
    nlp = spacy.load(model_path)
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents]
    df = pd.DataFrame(entities, columns=["Texte", "Label"])
    return df
