export default function ScanScreen() {
  return (
    <div className="page">
      <h1>Scan</h1>
      <p className="lede">Scanner tickets et emballages pour alimenter le stock.</p>
      <div className="placeholder-visual">Caméra Scan</div>
      <button className="btn btn-primary" type="button">
        Lancer le scan
      </button>
    </div>
  );
}