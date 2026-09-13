import { useCallback, useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

const PROJECT_ACCENTS = {
  "heritia-core": "from-emerald-400 to-cyan-400",
  "aevis-core": "from-violet-400 to-indigo-400",
  "selys-core": "from-amber-400 to-orange-400",
  "selys-marketplace-core": "from-rose-400 to-pink-400",
};

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
  const [selectedProjectId, setSelectedProjectId] = useState("heritia-core");
  const [fastTrack, setFastTrack] = useState(null);

  const selectedProject = useMemo(
    () => projects.find((p) => p.project_id === selectedProjectId) || projects[0],
    [projects, selectedProjectId],
  );

  const projectSignals = useMemo(
    () =>
      selectedProject
        ? signals.filter((s) => s.project_id === selectedProject.project_id)
        : signals,
    [signals, selectedProject],
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [projectsRes, signalsRes] = await Promise.all([
        fetch(`${API_BASE}/n2/nsi/projects`),
        fetch(`${API_BASE}/n2/nsi/signals`),
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

  const exportRadarFilters = (project) => {
    const profileFilters = {
      "heritia-core": { structure_classes: ["C1"], naf_codes: [] },
      "aevis-core": { structure_classes: ["C2"], naf_codes: ["4711D", "4719B", "4778C"] },
      "selys-core": { structure_classes: ["C2", "C3"], naf_codes: ["8121Z", "8122Z", "8130Z"] },
      "selys-marketplace-core": {
        structure_classes: ["C2"],
        naf_codes: ["4711D", "5610A", "5610B"],
      },
    };
    const filters = profileFilters[project.project_id] || { structure_classes: [], naf_codes: [] };
    const payload = {
      source: "nsi",
      project_id: project.project_id,
      target_audience: project.target_audience,
      perimeter: project.perimeter,
      filters,
      export_label: `Exporter filtres ${project.name} vers NeriaRadar`,
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
        <h1 className="mt-2 text-3xl font-semibold">Projets R&D autonomes</h1>
        <p className="mt-2 text-sm text-slate-300">
          Chaque application NeriaCorp est indépendante — aucun pontage automatique de stock ou de flux
          inter-apps.
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        {projects.map((project) => {
          const accent = PROJECT_ACCENTS[project.project_id] || "from-slate-400 to-slate-500";
          const isSelected = selectedProject?.project_id === project.project_id;
          return (
            <article
              key={project.project_id}
              className={`glass-panel rounded-2xl border p-5 backdrop-blur-xl transition ${
                isSelected ? "border-cyan-400/40 bg-cyan-400/5" : "border-white/10 bg-white/5"
              }`}
            >
              <button
                type="button"
                onClick={() => setSelectedProjectId(project.project_id)}
                className="w-full text-left"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">{project.name}</h2>
                    <p className="text-sm text-slate-300">{project.category}</p>
                    <p className="mt-1 text-xs uppercase tracking-wider text-cyan-200">
                      {project.target_audience}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${maturityTone(project.maturity_score)}`}>
                      {project.maturity_score}/100
                    </div>
                    <p className="text-xs uppercase tracking-widest text-slate-400">Maturité</p>
                  </div>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${accent}`}
                    style={{ width: `${project.maturity_score}%` }}
                  />
                </div>
              </button>

              <p className="mt-4 text-sm text-slate-200">{project.perimeter}</p>

              <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Fonctionnalités clés
              </h3>
              <ul className="mt-2 space-y-1 text-sm text-slate-200">
                {(project.core_features || []).slice(0, 3).map((item) => (
                  <li key={item} className="rounded-lg bg-black/20 px-3 py-1.5">
                    {item}
                  </li>
                ))}
              </ul>

              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => exportRadarFilters(project)}
                  className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950"
                >
                  Exporter vers NeriaRadar
                </button>
              </div>
            </article>
          );
        })}
      </section>

      {selectedProject ? (
        <section className="glass-panel rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <h2 className="text-lg font-semibold">
            Verrous techniques — {selectedProject.name}
          </h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-200">
            {(selectedProject.technical_barriers || []).map((item) => (
              <li key={item} className="rounded-lg bg-black/20 px-3 py-2">
                {item}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="glass-panel rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h2 className="text-lg font-semibold">
          Signaux de veille
          {selectedProject ? ` — ${selectedProject.name}` : ""}
        </h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {projectSignals.map((signal) => (
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
