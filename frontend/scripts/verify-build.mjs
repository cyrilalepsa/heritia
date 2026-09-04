import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const distDir = path.join(rootDir, "dist");
const indexPath = path.join(distDir, "index.html");

if (!fs.existsSync(indexPath)) {
  console.error("verify-build: dist/index.html is missing — run vite build first");
  process.exit(1);
}

const indexHtml = fs.readFileSync(indexPath, "utf8");
const assetsDir = path.join(distDir, "assets");
const jsFiles = fs.existsSync(assetsDir)
  ? fs.readdirSync(assetsDir).filter((name) => name.endsWith(".js"))
  : [];

if (!indexHtml.includes("<title>HERITIA</title>")) {
  console.error("verify-build: expected HERITIA index.html title");
  process.exit(1);
}

const forbiddenMarkers = ["NeriaCorp N2", "odelice-logo", "Les Délices en Famille"];
for (const marker of forbiddenMarkers) {
  if (indexHtml.includes(marker)) {
    console.error(`verify-build: forbidden N2 template marker found: ${marker}`);
    process.exit(1);
  }
}

if (jsFiles.length === 0) {
  console.error("verify-build: no JS bundle found in dist/assets");
  process.exit(1);
}

const bundle = fs.readFileSync(path.join(assetsDir, jsFiles[0]), "utf8");
const requiredRoutes = ["/profil", "/recettes", "/scan", "/gamification", "/stock"];
const missingRoutes = requiredRoutes.filter((route) => !bundle.includes(route));

if (missingRoutes.length > 0) {
  console.error(`verify-build: missing Heritia routes in bundle: ${missingRoutes.join(", ")}`);
  process.exit(1);
}

console.log("verify-build: HERITIA React bundle OK");
