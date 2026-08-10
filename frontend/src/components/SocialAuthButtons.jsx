import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

export default function SocialAuthButtons() {
  const { loginWithToken } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(null);

  async function handleSocial(provider) {
    setError("");
    setLoading(provider);
    try {
      // Stub: real Google/Apple SDK tokens plug in here
      const email = `demo.${provider}@heritia.app`;
      const res = await api.socialLogin({
        provider,
        id_token: `stub-${provider}-token`,
        email,
        nom: "Demo",
        prenom: provider === "google" ? "Google" : "Apple",
        ville: "Paris",
      });
      await loginWithToken(res.access_token);
      navigate("/profil");
    } catch (err) {
      setError(err.message || "Connexion sociale indisponible");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      {error ? <div className="error-banner">{error}</div> : null}
      <button
        type="button"
        className="btn btn-social"
        style={{ marginBottom: 10 }}
        disabled={Boolean(loading)}
        onClick={() => handleSocial("google")}
      >
        {loading === "google" ? "Connexion…" : "Continuer avec Google"}
      </button>
      <button
        type="button"
        className="btn btn-social"
        disabled={Boolean(loading)}
        onClick={() => handleSocial("apple")}
      >
        {loading === "apple" ? "Connexion…" : "Continuer avec Apple"}
      </button>
    </div>
  );
}