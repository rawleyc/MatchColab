// --- Load environment variables ---
import dotenv from "dotenv";
dotenv.config();

// --- Import dependencies ---
import express from "express";
import cors from "cors";
import morgan from "morgan";

// --- Import routes ---
import matchRoutes from "./routes/match.js";

// --- Initialize app ---
const app = express();

// --- Middleware setup ---
app.use(cors());
app.use(express.json()); // parses JSON in request body
app.use(morgan("dev"));  // logs requests in the console

// --- Base route ---
app.get("/", (req, res) => {
  res.json({ message: "MatchColab API is running 🚀" });
});

// --- Match route ---
app.use("/match", matchRoutes);

// --- Start server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
