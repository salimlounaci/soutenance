import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const API_URL = process.env.REACT_APP_API_URL;  

  const [isRegistering, setIsRegistering] = useState(false); 
  const [formData, setFormData] = useState({
    prenom: '',
    nom: '',
    email: '',
    password: '',
    role: 'user',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const { prenom, nom, email, password } = formData;

    if (isRegistering) {
      if (prenom && nom && email && password) {
        fetch(`${API_URL}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        })
          .then(res => res.json())
          .then(data => {
            if (data.message) {
              alert(data.message);
              navigate('/upload');
            } else {
              alert(data.error);
            }
          });
      } else {
        alert('Merci de remplir tous les champs pour créer un compte.');
      }
    } else {
      if (email && password) {
        fetch(`${API_URL}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        })
          .then(res => res.json())
          .then(data => {
            if (data.user) {
              localStorage.setItem('user', JSON.stringify(data.user));
              alert(data.message);
              navigate('/upload');
            } else {
              alert(data.error);
            }
          });
      } else {
        alert('Merci de remplir tous les champs pour vous connecter.');
      }
    }
  };

  // ... le reste inchangé
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <img src="/logo.png" alt="Logo JobAI" style={styles.logo} />
        <h1 style={styles.title}>Bienvenue sur JobAI</h1>
        <p style={styles.subtitle}>
          {isRegistering ? 'Créer un compte' : 'Connecte-toi pour continuer'}
        </p>

        <div style={{ marginBottom: '16px' }}>
          <button
            style={{ ...styles.toggleButton, backgroundColor: isRegistering ? '#ccc' : '#e63946' }}
            onClick={() => setIsRegistering(false)}
          >
            Se connecter
          </button>
          <button
            style={{ ...styles.toggleButton, backgroundColor: isRegistering ? '#e63946' : '#ccc' }}
            onClick={() => setIsRegistering(true)}
          >
            Créer un compte
          </button>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          {isRegistering && (
            <>
              <input
                type="text"
                name="prenom"
                placeholder="Prénom"
                value={formData.prenom}
                onChange={handleChange}
                style={styles.input}
              />
              <input
                type="text"
                name="nom"
                placeholder="Nom"
                value={formData.nom}
                onChange={handleChange}
                style={styles.input}
              />
            </>
          )}
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            style={styles.input}
          />
          <input
            type="password"
            name="password"
            placeholder="Mot de passe"
            value={formData.password}
            onChange={handleChange}
            style={styles.input}
          />
          <button type="submit" style={styles.button}>
            {isRegistering ? 'Créer le compte' : 'Se connecter'}
          </button>
        </form>
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
    maxWidth: '400px',
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
    fontSize: '24px',
    marginBottom: '8px',
    color: '#333',
    fontWeight: '600',
  },
  subtitle: {
    fontSize: '14px',
    color: '#777',
    marginBottom: '24px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  input: {
    padding: '12px 14px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    fontSize: '15px',
    outline: 'none',
    transition: 'border 0.3s',
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
    transition: 'background-color 0.3s',
  },
   toggleButton: {
    padding: '10px 12px',
    margin: '0 6px',
    border: 'none',
    borderRadius: '6px',
    color: '#fff',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
};

export default Login;
