import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.join(__dirname, "dist");
const port = Number(process.env.PORT || 3000);
const appId = "HERITIA";

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
};

function send(res, status, body, type, extraHeaders = {}) {
  res.writeHead(status, {
    "Content-Type": type || "text/plain; charset=utf-8",
    "X-Heritia-App": "1",
    "X-App-Name": appId,
    "Cache-Control": "no-cache, no-store, must-revalidate",
    ...extraHeaders,
  });
  res.end(body);
}

function readIndexTitle() {
  try {
    const html = fs.readFileSync(path.join(distDir, "index.html"), "utf8");
    const match = html.match(/<title>([^<]+)<\/title>/i);
    return match ? match[1] : "unknown";
  } catch {
    return "missing";
  }
}

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);

  if (urlPath === "/health") {
    return send(res, 200, JSON.stringify({ status: "ok", app: appId }), "application/json");
  }

  let filePath = path.join(distDir, urlPath === "/" ? "index.html" : urlPath);
  if (!filePath.startsWith(distDir)) {
    return send(res, 403, "Forbidden");
  }
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(distDir, "index.html");
  }
  const ext = path.extname(filePath).toLowerCase();
  fs.readFile(filePath, (err, data) => {
    if (err) return send(res, 500, "Error");
    send(res, 200, data, mime[ext] || "application/octet-stream");
  });
});

server.listen(port, "0.0.0.0", () => {
  const title = readIndexTitle();
  console.log(`${appId} web listening on 0.0.0.0:${port} (dist title: ${title})`);
  if (title !== appId) {
    console.warn(`WARNING: dist/index.html title is "${title}", expected "${appId}"`);
  }
  console.log("ready");
});
