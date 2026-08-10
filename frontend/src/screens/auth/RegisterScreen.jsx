import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import SocialAuthButtons from "../../components/SocialAuthButtons";
import { LOGO_SRC } from "../../config/constants";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/api";

const initial = {
  nom: "",
  prenom: "",
  ville: "",
  email: "",
  password: "",
};

export default function RegisterScreen() {
  const navigate = useNavigate();
  const { loginWithToken } = useAuth();
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.register(form);
      await loginWithToken(res.access_token);
      navigate("/profil");
    } catch (err) {
      setError(err.message || "Inscription impossible");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="page auth-card">
        <img className="auth-logo" src={LOGO_SRC} alt="HERITIA" />
        <h1 className="brand-title">HERITIA</h1>
        <p className="brand-sub">Créer votre compte</p>

        {error ? <div className="error-banner">{error}</div> : null}

        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="nom">Nom</label>
            <input
              id="nom"
              required
              value={form.nom}
              onChange={(e) => update("nom", e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="prenom">Prénom</label>
            <input
              id="prenom"
              required
              value={form.prenom}
              onChange={(e) => update("prenom", e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="ville">Ville</label>
            <input
              id="ville"
              required
              value={form.ville}
              onChange={(e) => update("ville", e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Création…" : "S'inscrire"}
          </button>
        </form>

        <div className="divider">ou</div>
        <SocialAuthButtons />

        <div className="link-row">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </div>
      </div>
    </div>
  );
}