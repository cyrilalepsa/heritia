import { useState } from "react";
import { Link } from "react-router-dom";
import { LOGO_SRC } from "../../config/constants";
import { api } from "../../services/api";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [step, setStep] = useState("request");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function requestReset(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);
    try {
      const res = await api.forgotPassword({ email });
      setMessage(res.message || "Email envoyé si le compte existe.");
      if (res.dev_reset_token) {
        setToken(res.dev_reset_token);
        setStep("reset");
      }
    } catch (err) {
      setError(err.message || "Impossible d'envoyer le lien");
    } finally {
      setLoading(false);
    }
  }

  async function confirmReset(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);
    try {
      await api.resetPassword({ token, new_password: newPassword });
      setMessage("Mot de passe mis à jour. Vous pouvez vous connecter.");
      setStep("done");
    } catch (err) {
      setError(err.message || "Réinitialisation impossible");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="page auth-card">
        <img className="auth-logo" src={LOGO_SRC} alt="HERITIA" />
        <h1 className="brand-title">HERITIA</h1>
        <p className="brand-sub">Mot de passe oublié</p>

        {error ? <div className="error-banner">{error}</div> : null}
        {message ? <div className="success-banner">{message}</div> : null}

        {step === "request" ? (
          <form onSubmit={requestReset}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Envoi…" : "Recevoir un lien"}
            </button>
          </form>
        ) : null}

        {step === "reset" ? (
          <form onSubmit={confirmReset}>
            <div className="field">
              <label htmlFor="token">Code de réinitialisation</label>
              <input
                id="token"
                required
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="newPassword">Nouveau mot de passe</label>
              <input
                id="newPassword"
                type="password"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Mise à jour…" : "Réinitialiser"}
            </button>
          </form>
        ) : null}

        {step === "done" ? (
          <Link className="btn btn-primary" to="/login" style={{ textDecoration: "none" }}>
            Retour à la connexion
          </Link>
        ) : null}

        <div className="link-row">
          <Link to="/login">Retour</Link>
        </div>
      </div>
    </div>
  );
}