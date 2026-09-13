import { useCallback, useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

function maturityTone(score) {
  if (score >= 80) return "text-emerald-300";
  if (score >= 60) return "text-amber-300";
  return "text-rose-300";
}

export default function NsiDashboard() {
  const [projects, setProjects] = useState([]);
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [fastTrack, setFastTrack] = useState(null);

  const heritia = useMemo(
    () => projects.find((p) => p.project_id === "heritia-core") || projects[0],
    [projects],
  );
  const steppingStone = heritia?.stepping_stone_projects?.[0];

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [projectsRes, signalsRes] = await Promise.all([
        fetch(`${API_BASE}/n2/nsi/projects`),
        fetch(`${API_BASE}/n2/nsi/signals?project_id=heritia-core`),
      ]);
      if (!projectsRes.ok || !signalsRes.ok) throw new Error("NSI API unavailable");
      setProjects(await projectsRes.json());
      setSignals(await signalsRes.json());
    } catch (err) {
      setError(err.message || "Erreur de chargement NSI");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const exportRadarFilters = () => {
    const filters = steppingStone?.target_radar_filter || {
      structure_classes: ["C2"],
      naf_codes: ["5610A", "5610B", "5621Z"],
    };
    const payload = {
      source: "nsi",
      project_id: heritia?.project_id,
      stepping_stone_id: steppingStone?.id,
      filters,
      export_label: "Exporter les filtres vers NeriaRadar",
    };
    window.dispatchEvent(new CustomEvent("n2:neriaradar-export", { detail: payload }));
    setFastTrack(payload);
  };

  if (loading) {
    return (
      <div className="nsi-dashboard glass-panel p-8 text-slate-200">Chargement NSI…</div>
    );
  }

  if (error) {
    return (
      <div className="nsi-dashboard glass-panel p-8 text-rose-200">{error}</div>
    );
  }

  return (
    <div className="nsi-dashboard space-y-6 p-6 text-slate-100">
      <header className="glass-panel rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Neria Scout Intelligent</p>
        <h1 className="mt-2 text-3xl font-semibold">Projets & Tremplins R&D</h1>
      </header>

      {heritia ? (
        <section className="glass-panel grid gap-6 rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl lg:grid-cols-2">
          <div>
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold">{heritia.name}</h2>
                <p className="text-sm text-slate-300">{heritia.category}</p>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${maturityTone(heritia.maturity_score)}`}>
                  {heritia.maturity_score}/100
                </div>
                <p className="text-xs uppercase tracking-widest text-slate-400">Maturité</p>
              </div>
            </div>

            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400"
                style={{ width: `${heritia.maturity_score}%` }}
              />
            </div>

            <h3 className="mt-6 text-sm font-semibold uppercase tracking-wider text-slate-300">
              Verrous techniques
            </h3>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              {(heritia.technical_barriers || []).map((item) => (
                <li key={item} className="rounded-lg bg-black/20 px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {steppingStone ? (
            <article className="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Projet Tremplin</p>
              <h3 className="mt-2 text-xl font-semibold">{steppingStone.name}</h3>
              <p className="mt-2 text-sm text-slate-300">{steppingStone.target_segment}</p>
              <p className="mt-4 text-sm text-slate-200">{steppingStone.mvp_scope}</p>
              <p className="mt-4 text-sm font-medium text-emerald-300">
                MRR estimé : {steppingStone.estimated_mrr_per_client} € / client
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={exportRadarFilters}
                  className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950"
                >
                  Exporter les filtres vers NeriaRadar
                </button>
                <a
                  href="/console/portail-b2b"
                  className="rounded-xl border border-white/20 px-4 py-2 text-sm"
                >
                  Portail B2B
                </a>
                <a
                  href="/console/selys-marketplace"
                  className="rounded-xl border border-white/20 px-4 py-2 text-sm"
                >
                  Selys Marketplace
                </a>
              </div>
            </article>
          ) : null}
        </section>
      ) : null}

      <section className="glass-panel rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h2 className="text-lg font-semibold">Signaux de convergence</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {signals.map((signal) => (
            <div key={signal.id} className="rounded-xl border border-white/10 bg-black/20 p-4">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-medium">{signal.title}</h3>
                <span className="rounded-full bg-white/10 px-2 py-1 text-xs uppercase">
                  {signal.opportunity_badge}
                </span>
              </div>
              <p className="mt-2 text-xs text-slate-400">{signal.source}</p>
              <p className="mt-2 text-sm text-cyan-200">Impact {signal.impact_score}/100</p>
            </div>
          ))}
        </div>
      </section>

      {fastTrack ? (
        <pre className="glass-panel overflow-x-auto rounded-2xl border border-white/10 bg-black/30 p-4 text-xs text-emerald-200">
          {JSON.stringify(fastTrack, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
