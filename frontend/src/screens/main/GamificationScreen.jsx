import { useState } from "react";
import { GOLD_BADGES_UNLOCK } from "../../config/constants";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/api";

export default function GamificationScreen() {
  const { user, refreshUser } = useAuth();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [price, setPrice] = useState("9.90");

  if (!user) return null;

  const count = user.gold_badges_count || 0;
  const unlocked = user.ebook_unlocked || count >= GOLD_BADGES_UNLOCK;

  async function earnBadge() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await api.updateGoldBadges(count + 1);
      const me = await refreshUser();
      if (me.ebook_unlocked) {
        setMessage("3 badges or atteints — marketplace e-book débloquée !");
      } else {
        setMessage("Badge or ajouté.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function startStripeOnboarding() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const res = await api.stripeOnboarding();
      setMessage(`Compte Stripe Express : ${res.account_id}`);
      if (res.onboarding_url) window.open(res.onboarding_url, "_blank", "noopener,noreferrer");
      await refreshUser();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function publishEbook() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const cents = Math.round(parseFloat(price.replace(",", ".")) * 100);
      await api.createEbook({
        title: `E-book de ${user.prenom}`,
        price: cents,
        active: true,
      });
      setMessage("Listing e-book publié (commission plateforme 0%).");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <h1>Gamification</h1>
      <p className="lede">Badges or & marketplace e-book (Stripe Connect, 0% commission).</p>

      {error ? <div className="error-banner">{error}</div> : null}
      {message ? <div className="success-banner">{message}</div> : null}

      <div className="panel">
        <h2>Badges or</h2>
        <div className="badge-meter" aria-label={`${count} badges or`}>
          {[0, 1, 2].map((i) => (
            <div key={i} className={`badge-dot${count > i ? " filled" : ""}`}>
              ★
            </div>
          ))}
        </div>
        <p className="meta">
          {count} / {GOLD_BADGES_UNLOCK} —{" "}
          {unlocked ? "E-book débloqué" : "Encore des badges pour débloquer l'e-book"}
        </p>
        <button className="btn btn-primary" type="button" onClick={earnBadge} disabled={busy}>
          Gagner un badge or
        </button>
      </div>

      <div className="panel">
        <h2>Marketplace e-book</h2>
        {!unlocked ? (
          <p className="meta">Atteignez 3 badges or pour activer la vente de votre e-book.</p>
        ) : (
          <>
            <p className="meta" style={{ marginBottom: 12 }}>
              Stripe Connect Express · application_fee_amount = 0
            </p>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={startStripeOnboarding}
              disabled={busy}
              style={{ marginBottom: 12 }}
            >
              Onboarding Stripe Express
            </button>
            <div className="field">
              <label htmlFor="price">Prix (€)</label>
              <input
                id="price"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                inputMode="decimal"
              />
            </div>
            <button className="btn btn-primary" type="button" onClick={publishEbook} disabled={busy}>
              Publier mon e-book
            </button>
          </>
        )}
      </div>
    </div>
  );
}