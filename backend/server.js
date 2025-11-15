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

import { createClient } from "@supabase/supabase-js";
import OpenAI from "openai";
// Serve static frontend files
app.use(express.static(path.join(__dirname, "..", "frontend")));

// --- Base route ---
app.get("/", (req, res) => {
  // Serve the frontend if accessed from browser
  res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

// --- Health check route for Render ---
app.get("/health", async (req, res) => {

// --- Serve static frontend ---
const frontendPath = path.join(__dirname, "..", "frontend");
app.use(express.static(frontendPath));

// Fallback to index.html for root (simple SPA pattern)
app.get(["/", "/index.html"], (req, res, next) => {
  // If client explicitly requests JSON at root, pass through
  if (req.headers.accept && req.headers.accept.includes("application/json")) return next();
  res.sendFile(path.join(frontendPath, "index.html"));
});
  const health = {
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {
      server: "ok",
      database: "unknown",
      openai: "unknown"
    }
  };

  try {
    // Check Supabase connection
    if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY) {
      try {
        const { createClient } = await import("@supabase/supabase-js");
        const supabase = createClient(
          process.env.SUPABASE_URL,
          process.env.SUPABASE_SERVICE_KEY
        );
        
        // Simple query to verify database connection
        const { error, count } = await supabase
          .from("artists")
          .select("*", { count: "exact", head: true });
        
        if (error) {
          health.checks.database = `error: ${error.message}`;
        } else {
          health.checks.database = "ok";
          health.checks.database_info = { artist_count: count || 0 };
        }
      } catch (dbError) {
        health.checks.database = `error: ${dbError.message}`;
      }
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
    const allOk = Object.values(health.checks).every(v => 
      v === "ok" || v === "configured" || typeof v === "object"
    );
    health.status = allOk ? "ok" : "degraded";

    const statusCode = health.status === "ok" ? 200 : 503;
    res.status(statusCode).json(health);
  } catch (error) {
    health.status = "error";
    health.error = error.message;
    health.stack = process.env.NODE_ENV === "development" ? error.stack : undefined;
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
