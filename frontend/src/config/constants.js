export const APP_URL =
  import.meta.env.VITE_APP_URL || "http://localhost:5174";

export const API_BASE =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_HERITIA_API ||
  "/api";

export const HEALTH_OPTION_SURCHARGE = 7;
/** A referral counts only when the invitee subscribes to Premium. */
export const REFERRALS_PER_FREE_YEAR = 6;
export const MAX_REFERRAL_FREE_YEARS = 3;
export const REFERRAL_REQUIRES_PREMIUM = true;

/** @typedef {'monthly' | 'annual'} BillingPeriod */
/** @typedef {'standard' | 'premium'} PlanTier */

export const PLAN_CATALOG = {
  standard: {
    tier: "standard",
    label: "Standard",
    includesHealth: false,
    monthly: {
      planType: "standard_monthly",
      price: 19,
      perMonthEquiv: 19,
      promoTag: null,
      argument: "Options santé à la carte (+7 €/mois).",
      cta: "Choisir le Standard mensuel",
      savings: 0,
    },
    annual: {
      planType: "standard_annual",
      price: 99,
      perMonthEquiv: 8.25,
      promoTag: "Économisez 129 € (-56 %)",
      argument: "Amorti dès le 1er mois grâce à l'anti-gaspillage.",
      cta: "JE FONCE ET J'ÉCONOMISE 129 €",
      savings: 129,
      highlight: "JE FONCE",
    },
  },
  premium: {
    tier: "premium",
    label: "Premium",
    includesHealth: true,
    monthly: {
      planType: "premium_monthly",
      price: 29,
      perMonthEquiv: 29,
      promoTag: null,
      argument: "Diabète, Cholestérol, Perte de poids inclus.",
      cta: "Choisir le Premium mensuel",
      savings: 0,
    },
    annual: {
      planType: "premium_annual",
      price: 149,
      perMonthEquiv: 12.4,
      promoTag: "Économisez 199 € (-57 %)",
      argument: "Toutes les options santé incluses + fonctionnalités avancées.",
      cta: "JE PASSE AU PREMIUM ET J'ÉCONOMISE 199 €",
      savings: 199,
      highlight: true,
    },
  },
};

export const HEALTH_OPTIONS = [
  { id: "diabete", label: "Diabète", surcharge: HEALTH_OPTION_SURCHARGE },
  { id: "cholesterol", label: "Cholestérol", surcharge: HEALTH_OPTION_SURCHARGE },
  { id: "perte_poids", label: "Perte de poids", surcharge: HEALTH_OPTION_SURCHARGE },
];

export function parsePlanType(planType) {
  const value = planType || "standard_monthly";
  if (value.includes("premium") || value === "standard_29") {
    return {
      tier: "premium",
      period: value.includes("annual") ? "annual" : "monthly",
    };
  }
  return {
    tier: "standard",
    period: value.includes("annual") ? "annual" : "monthly",
  };
}

export function buildPlanType(tier, period) {
  return PLAN_CATALOG[tier][period].planType;
}

export const NAV_TABS = [
  { path: "/profil", label: "Profil", icon: "user" },
  { path: "/stock", label: "Stock", icon: "box" },
  { path: "/scan", label: "Scan", icon: "scan" },
  { path: "/recettes", label: "Recettes", icon: "book" },
  { path: "/gamification", label: "Badges", icon: "trophy" },
];

export const LOGO_SRC = "/assets/logos/heritia.jpg";
export const GOLD_BADGES_UNLOCK = 3;