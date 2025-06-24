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
        texte = row["Texte"]
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
