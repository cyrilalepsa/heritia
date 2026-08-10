import { useEffect, useState } from "react";
import { api } from "../../services/api";

const empty = { titre: "", ingredients: "", instructions: "" };

export default function RecettesScreen() {
  const [recipes, setRecipes] = useState([]);
  const [form, setForm] = useState(empty);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    try {
      const data = await api.listRecipes();
      setRecipes(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.createRecipe(form);
      setForm(empty);
      await load();
    } catch (err) {
      setError(err.message || "Création impossible");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Recettes</h1>
      <p className="lede">Proposez une recette — validation admin requise.</p>

      {error ? <div className="error-banner">{error}</div> : null}

      <form className="panel" onSubmit={onSubmit}>
        <h2>Nouvelle recette</h2>
        <div className="field">
          <label htmlFor="titre">Titre</label>
          <input
            id="titre"
            required
            value={form.titre}
            onChange={(e) => setForm((p) => ({ ...p, titre: e.target.value }))}
          />
        </div>
        <div className="field">
          <label htmlFor="ingredients">Ingrédients</label>
          <textarea
            id="ingredients"
            rows={3}
            required
            value={form.ingredients}
            onChange={(e) => setForm((p) => ({ ...p, ingredients: e.target.value }))}
          />
        </div>
        <div className="field">
          <label htmlFor="instructions">Instructions</label>
          <textarea
            id="instructions"
            rows={4}
            required
            value={form.instructions}
            onChange={(e) => setForm((p) => ({ ...p, instructions: e.target.value }))}
          />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Envoi…" : "Soumettre"}
        </button>
      </form>

      {recipes.map((recipe) => (
        <div className="panel" key={recipe.id}>
          <h2>{recipe.titre}</h2>
          <p className="meta">
            {recipe.admin_validated ? "Validée par l'admin" : "En attente de validation"}
          </p>
          <p style={{ whiteSpace: "pre-wrap" }}>{recipe.ingredients}</p>
        </div>
      ))}
    </div>
  );
}