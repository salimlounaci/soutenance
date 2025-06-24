import React, { useEffect, useState } from "react";

function Swipe() {
  const [offres, setOffres] = useState([]);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/offres`)
      .then((res) => res.json())
      .then((data) => {
        setOffres(data);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des offres :", error);
      });
  }, []);


  const handleLike = () => {
    console.log("💚 J'aime :", offres[index]);
    setIndex((prev) => prev + 1);
  };

  const handleSkip = () => {
    console.log("❌ Passé :", offres[index]);
    setIndex((prev) => prev + 1);
  };

  const containerStyle = {
    maxWidth: "600px",
    margin: "40px auto",
    padding: "20px",
    backgroundColor: "#f9f9f9",
    borderRadius: "12px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    textAlign: "center",
  };

  const cardStyle = {
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    marginBottom: "20px",
  };

  const titleStyle = {
    fontWeight: "700",
    fontSize: "1.8rem",
    color: "#222",
  };

  const locationStyle = {
    fontStyle: "italic",
    color: "#666",
    marginBottom: "12px",
  };

  const descriptionStyle = {
    color: "#444",
    marginBottom: "20px",
  };

  const buttonStyle = {
    padding: "12px 25px",
    margin: "0 15px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    color: "white",
    minWidth: "110px",
    transition: "background-color 0.3s",
  };

  if (index >= offres.length) {
    return (
      <div style={containerStyle}>
        <h2>Toutes les offres ont été vues ! 🎉</h2>
      </div>
    );
  }

  const offre = offres[index];

  return (
    <div style={containerStyle}>
        <img
  src="/logo.png"
  alt="Logo JobAI"
  style={{
    width: "150px",
    display: "block",
    margin: "0 auto 20px",
    filter: "drop-shadow(0 0 5px rgba(0,0,0,0.2))"
  }}
/>
      <h1 style={{ marginBottom: "30px" }}>Swipe les Offres</h1>
      <div style={cardStyle}>
        <h2 style={titleStyle}>{offre.intitule}</h2>
        <div style={locationStyle}>{offre.lieuTravail_libelle}</div>
        <p style={descriptionStyle}>{offre.typeContrat}</p>
        <p style={descriptionStyle}>{offre.dateCreation}</p>
        <a
          href={offre.origineOffre_urlOrigine}
          target="_blank"
          rel="noreferrer"
          style={{ color: "#007bff", textDecoration: "underline" }}
        >
          GOOO
        </a>
        <p style={{ fontWeight: "bold", color: "#555" }}>
    Score de correspondance : {(offre.score * 100).toFixed(1)}%
    </p>
      </div>
      <div>
        <button
          onClick={handleSkip}
          style={{ ...buttonStyle, backgroundColor: "#f44336" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#d32f2f")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#f44336")}
        >
          NOPEEE
        </button>
        <button
          onClick={handleLike}
          style={{ ...buttonStyle, backgroundColor: "#4CAF50" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#388e3c")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#4CAF50")}
        >
          YESSSS
        </button>
      </div>
    </div>
  );
}

export default Swipe;
