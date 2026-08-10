import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import SocialAuthButtons from "../../components/SocialAuthButtons";
import { LOGO_SRC } from "../../config/constants";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/api";

export default function LoginScreen() {
  const navigate = useNavigate();
  const { loginWithToken } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.login({ email, password });
      await loginWithToken(res.access_token);
      navigate("/profil");
    } catch (err) {
      setError(err.message || "Connexion impossible");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="page auth-card">
        <img className="auth-logo" src={LOGO_SRC} alt="HERITIA" />
        <h1 className="brand-title">HERITIA</h1>
        <p className="brand-sub">Connexion à votre espace</p>

        {error ? <div className="error-banner">{error}</div> : null}

        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <div className="link-row">
          <Link to="/forgot-password">Mot de passe oublié ?</Link>
        </div>

        <div className="divider">ou</div>
        <SocialAuthButtons />

        <div className="link-row">
          Pas encore de compte ? <Link to="/register">S&apos;inscrire</Link>
        </div>
      </div>
    </div>
  );
}