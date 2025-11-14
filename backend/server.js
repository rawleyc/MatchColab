// --- Load environment variables ---
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from the root directory (one level up from backend)
dotenv.config({ path: path.join(__dirname, "..", ".env") });

// --- Import dependencies ---
import express from "express";
import cors from "cors";
import morgan from "morgan";

// --- Import routes ---
import matchRoutes from "./routes/match.js";

// --- Initialize app ---
const app = express();

// --- Middleware setup ---
// Configure CORS: allow all in dev; allowlist via CORS_ORIGIN (comma-separated) in prod
const allowedOrigins = (process.env.CORS_ORIGIN || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
const corsOptions = allowedOrigins.length ? { origin: allowedOrigins } : {};
app.use(cors(corsOptions));
app.use(express.json()); // parses JSON in request body
app.use(morgan("dev"));  // logs requests in the console

// --- Base route ---
app.get("/", (req, res) => {
  res.json({ message: "MatchColab API is running 🚀" });
});

// --- Health check route for Render ---
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// --- Match route ---
app.use("/match", matchRoutes);

// --- Start server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
