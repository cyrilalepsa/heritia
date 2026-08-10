import { useMemo, useState } from "react";
import {
  HEALTH_OPTION_SURCHARGE,
  HEALTH_OPTIONS,
  MAX_REFERRAL_FREE_YEARS,
  PLAN_CATALOG,
  REFERRALS_PER_FREE_YEAR,
  buildPlanType,
  parsePlanType,
} from "../../config/constants";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/api";

export default function ProfilScreen() {
  const { user, refreshUser, logout } = useAuth();
  const initial = parsePlanType(user?.plan_type);
  const [tier, setTier] = useState(initial.tier);
  const [period, setPeriod] = useState(initial.period);
  const [healthOptions, setHealthOptions] = useState(user?.health_options || []);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const catalog = PLAN_CATALOG[tier];
  const offer = catalog[period];
  const isPremium = catalog.includesHealth;
  const isAnnual = period === "annual";

  const surcharge = useMemo(() => {
    if (isPremium || isAnnual) return 0;
    return healthOptions.length * HEALTH_OPTION_SURCHARGE;
  }, [healthOptions, isPremium, isAnnual]);

  const totalLabel = useMemo(() => {
    if (isAnnual) {
      return `${offer.price} €/an · soit ${offer.perMonthEquiv.toFixed(2).replace(".", ",")} €/mois`;
    }
    const monthly = offer.price + surcharge;
    return `${monthly} €/mois`;
  }, [isAnnual, offer, surcharge]);

  const referrals =
    user?.referral_progress?.referrals_this_year ?? user?.referrals_this_year ?? 0;
  const referralTarget = user?.referral_progress?.target ?? REFERRALS_PER_FREE_YEAR;
  const freeYears =
    user?.referral_progress?.free_years_claimed ??
    user?.referral_free_years_claimed ??
    0;
  const referralPct = Math.min(100, Math.round((referrals / referralTarget) * 100));

  function selectTier(nextTier) {
    setTier(nextTier);
    if (nextTier === "premium") {
      setHealthOptions(HEALTH_OPTIONS.map((o) => o.id));
    }
  }

  function toggleOption(id) {
    if (isPremium) return;
    setHealthOptions((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function save(selectedTier = tier, selectedPeriod = period) {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const plan_type = buildPlanType(selectedTier, selectedPeriod);
      const payload = {
        plan_type,
        health_options:
          selectedTier === "premium"
            ? HEALTH_OPTIONS.map((o) => o.id)
            : healthOptions,
      };
      await api.updateMe(payload);
      await refreshUser();
      setTier(selectedTier);
      setPeriod(selectedPeriod);
      setMessage("Abonnement mis à jour.");
    } catch (err) {
      setError(err.message || "Enregistrement impossible");
    } finally {
      setSaving(false);
    }
  }

  if (!user) return null;

  return (
    <div className="page">
      <h1>Profil / Santé</h1>
      <p className="lede">
        {user.prenom} {user.nom} · {user.ville}
      </p>

      {error ? <div className="error-banner">{error}</div> : null}
      {message ? <div className="success-banner">{message}</div> : null}

      <div className="panel">
        <h2>Abonnement</h2>

        <div className="billing-toggle" role="tablist" aria-label="Périodicité">
          <button
            type="button"
            role="tab"
            aria-selected={period === "monthly"}
            className={`billing-toggle-btn${period === "monthly" ? " active" : ""}`}
            onClick={() => setPeriod("monthly")}
          >
            Mensuel
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={period === "annual"}
            className={`billing-toggle-btn${period === "annual" ? " active" : ""}`}
            onClick={() => setPeriod("annual")}
          >
            Annuel (-56%)
          </button>
        </div>

        <div className="plan-grid">
          {Object.values(PLAN_CATALOG).map((plan) => {
            const slot = plan[period];
            const active = tier === plan.tier;
            return (
              <button
                key={plan.tier}
                type="button"
                className={`plan-card${active ? " active" : ""}${
                  period === "annual" && plan.tier === "standard" ? " featured" : ""
                }`}
                onClick={() => selectTier(plan.tier)}
              >
                {slot.promoTag ? <span className="promo-tag">{slot.promoTag}</span> : null}
                {slot.highlight === "JE FONCE" ? (
                  <span className="highlight-pill">JE FONCE</span>
                ) : null}
                <span className="plan-name">{plan.label}</span>
                <span className="plan-price">
                  {period === "annual"
                    ? `${slot.price} €/an`
                    : `${slot.price} €/mois`}
                </span>
                {period === "annual" ? (
                  <span className="plan-equiv">
                    soit {slot.perMonthEquiv.toFixed(2).replace(".", ",")} €/mois
                  </span>
                ) : null}
                <span className="plan-note">{slot.argument}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="panel">
        <h2>
          {isPremium
            ? "Options santé incluses"
            : `Options santé (+${HEALTH_OPTION_SURCHARGE} €/mois)`}
        </h2>
        <div className="chip-row">
          {HEALTH_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`chip${
                isPremium || healthOptions.includes(opt.id) ? " active" : ""
              }`}
              onClick={() => toggleOption(opt.id)}
              disabled={isPremium}
              aria-disabled={isPremium}
            >
              {opt.label}
              {!isPremium && !isAnnual ? ` · +${HEALTH_OPTION_SURCHARGE}€` : ""}
            </button>
          ))}
        </div>
        <p className="meta total-estimate" style={{ marginTop: 12 }}>
          Total estimé : {totalLabel}
        </p>
      </div>

      <div className="panel referral-panel">
        <h2>Parrainage</h2>
        <p className="referral-gauge-label">
          {Math.min(referrals, referralTarget)}/{referralTarget} filleuls Premium
          convertis cette année
        </p>
        <div
          className="referral-bar"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={referralTarget}
          aria-valuenow={Math.min(referrals, referralTarget)}
        >
          <div className="referral-bar-fill" style={{ width: `${referralPct}%` }} />
        </div>
        <span className="referral-tag">
          6 parrainages Premium souscrits = 1 An Offert (Renouvelable{" "}
          {MAX_REFERRAL_FREE_YEARS} fois)
        </span>
        <p className="meta" style={{ marginTop: 10 }}>
          Crédits : {user.referral_credits} · Années offertes déjà obtenues :{" "}
          {freeYears}/{MAX_REFERRAL_FREE_YEARS}
        </p>
      </div>

      <button
        className="btn btn-primary"
        type="button"
        onClick={() => save(tier, period)}
        disabled={saving}
      >
        {saving ? "Enregistrement…" : offer.cta}
      </button>
      <button
        className="btn btn-secondary"
        type="button"
        style={{ marginTop: 10 }}
        onClick={logout}
      >
        Se déconnecter
      </button>
    </div>
  );
}