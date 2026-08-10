import { LOGO_SRC } from "../../config/constants";

export default function SplashScreen() {
  return (
    <div className="splash" role="status" aria-label="Chargement HERITIA">
      <div className="splash-inner">
        <img src={LOGO_SRC} alt="Logo HERITIA" />
        <h1>HERITIA</h1>
        <p>Votre héritage santé</p>
      </div>
    </div>
  );
}