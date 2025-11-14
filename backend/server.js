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

// Serve static frontend files
app.use(express.static(path.join(__dirname, "..", "frontend")));

// --- Base route ---
app.get("/", (req, res) => {
  // Serve the frontend if accessed from browser
  res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

// --- Health check route for Render ---
app.get("/health", async (req, res) => {
  const health = {
    status: "ok",
    timestamp: new Date().toISOString(),
    checks: {
      server: "ok",
      database: "unknown",
      openai: "unknown"
    }
  };

  try {
    // Check Supabase connection
    if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY) {
      const { createClient } = await import("@supabase/supabase-js");
      const supabase = createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_SERVICE_KEY
      );
      
      // Simple query to verify database connection
      const { error } = await supabase.from("artists").select("count", { count: "exact", head: true });
      health.checks.database = error ? `error: ${error.message}` : "ok";
    } else {
      health.checks.database = "not_configured";
    }

    // Check OpenAI API key presence
    if (process.env.OPENAI_API_KEY) {
      health.checks.openai = "configured";
    } else {
      health.checks.openai = "not_configured";
    }

    // Overall status
    const allOk = Object.values(health.checks).every(v => v === "ok" || v === "configured");
    health.status = allOk ? "ok" : "degraded";

    const statusCode = health.status === "ok" ? 200 : 503;
    res.status(statusCode).json(health);
  } catch (error) {
    health.status = "error";
    health.error = error.message;
    res.status(503).json(health);
  }
});

// --- Match route ---
app.use("/match", matchRoutes);

// --- Start server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
