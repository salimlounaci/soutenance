import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Upload() {
  const API_URL = process.env.REACT_APP_API_URL;

  const [selectedFile, setSelectedFile] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [user, setUser] = useState({ prenom: '', nom: '', email: '' });

  const navigate = useNavigate();

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      alert("Aucun fichier sélectionné");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/extract`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Erreur lors de l'extraction");
      }

      const data = await response.json();
      console.log("Réponse du backend :", data);
      setCvData(data);
    } catch (error) {
      console.error("Erreur :", error);
    }
  };

  const handleGoSwipe = () => {
    navigate("/swipe");
  };


  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <img src="/logo.png" alt="Logo JobAI" style={styles.logo} />
        <h1 style={styles.title}>Bienvenue {user.prenom} {user.nom}</h1>
        <p style={styles.subtitle}>Téléverse ton CV ici (PDF uniquement)</p>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={styles.fileInput}
        />
        <button onClick={handleUpload} style={styles.button}>Uploader mon CV</button>

        {cvData && (
          <div style={styles.result}>
            <div style={styles.resultTitle}>📄 Informations extraites :</div>
            <div style={styles.resultItem}><strong>Nom :</strong> {cvData.nom}</div>
            <div style={styles.resultItem}><strong>Email :</strong> {cvData.email}</div>
            <div style={styles.resultItem}><strong>Téléphone :</strong> {cvData.telephone}</div>
            <div style={styles.resultItem}><strong>Compétences :</strong> {cvData.competences}</div>
            <div style={styles.resultItem}><strong>Adresse :</strong> {cvData.adresse}</div>
            <button onClick={handleGoSwipe} style={styles.swipeButton}>
              Go Swipe →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


  const styles = {
    container: {
      background: 'linear-gradient(135deg, #1f1c2c, #928dab)',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px',
    },
    card: {
      backgroundColor: '#ffffff',
      padding: '40px 30px',
      borderRadius: '16px',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
      width: '100%',
      maxWidth: '500px',
      textAlign: 'center',
    },
    logo: {
      width: '140px',
      marginBottom: '20px',
      display: 'block',
      marginLeft: 'auto',
      marginRight: 'auto',
      filter: 'drop-shadow(0 0 6px rgba(0, 0, 0, 0.25))',
      backgroundColor: '#fff',
      padding: '6px',
      borderRadius: '12px',
    },
    title: {
      fontSize: '22px',
      marginBottom: '8px',
      color: '#333',
      fontWeight: '600',
    },
    subtitle: {
      fontSize: '14px',
      color: '#777',
      marginBottom: '24px',
    },
    input: {
      marginBottom: '16px',
      display: 'block',
      marginLeft: 'auto',
      marginRight: 'auto',
    },
    fileInput: {
      padding: '10px',
      borderRadius: '8px',
      border: '1px solid #ccc',
      fontSize: '15px',
      width: '100%',
      maxWidth: '320px',
      marginBottom: '16px',
    },
    button: {
      backgroundColor: '#e63946',
      color: '#fff',
      border: 'none',
      padding: '12px',
      borderRadius: '8px',
      fontSize: '16px',
      cursor: 'pointer',
      fontWeight: 'bold',
      width: '100%',
      maxWidth: '320px',
      marginBottom: '20px',
    },
    result: {
      backgroundColor: '#f5f5f5',
      padding: '20px',
      borderRadius: '10px',
      textAlign: 'left',
      marginTop: '30px',
      boxShadow: '0 4px 10px rgba(0,0,0,0.05)',
    },
    resultTitle: {
      marginBottom: '10px',
      fontWeight: 'bold',
      fontSize: '18px',
    },
    resultItem: {
      marginBottom: '6px',
    },
    swipeButton: {
      backgroundColor: '#2196F3',
      color: '#fff',
      border: 'none',
      padding: '12px',
      borderRadius: '8px',
      fontSize: '16px',
      cursor: 'pointer',
      fontWeight: 'bold',
      width: '100%',
      maxWidth: '320px',
      marginTop: '20px',
    }
  };


export default Upload;


