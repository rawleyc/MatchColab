import express from "express";
import OpenAI from "openai";
import { createClient } from "@supabase/supabase-js";

const router = express.Router();

// --- Helper function to get OpenAI client (lazy initialization) ---
const getOpenAIClient = () => {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY is not set in environment variables");
  }
  return new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
};

// --- Helper function to get Supabase client (lazy initialization) ---
const getSupabaseClient = () => {
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    throw new Error("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set in environment variables");
  }
  return createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );
};

// --- Main /match endpoint ---
router.post("/", async (req, res) => {
  try {
    const {
      tags,
      top_n = 10,
      only_successful = false,
      min_similarity = 0.3,
      persist_artist = false,
      artist_name = null
    } = req.body;

    // Validate required fields
    if (!tags || !tags.trim()) {
      return res.status(400).json({ error: "Tags are required" });
    }

    // Validate numeric parameters
    const topN = parseInt(top_n);
    if (isNaN(topN) || topN < 1 || topN > 100) {
      return res.status(400).json({ error: "top_n must be between 1 and 100" });
    }

    const minSim = parseFloat(min_similarity);
    if (isNaN(minSim) || minSim < 0 || minSim > 1) {
      return res.status(400).json({ error: "min_similarity must be between 0 and 1" });
    }

    const openai = getOpenAIClient();
    const supabase = getSupabaseClient();

    // 1️⃣ Generate embedding for input tags
    const embeddingResp = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: tags.trim()
    });
    const embedding = embeddingResp.data[0].embedding;

    // 2️⃣ (Optional) Persist querying artist so future matches can include them
    if (persist_artist && artist_name && artist_name.trim()) {
      const { error: upsertError } = await supabase
        .from("artists")
        .upsert({ artist_name: artist_name.trim(), artist_tags: tags.trim(), embedding }, { onConflict: "artist_name" });
      if (upsertError) {
        console.warn("Upsert warning:", upsertError.message);
      }
    }

    // 3️⃣ Call ranking function
    const { data, error } = await supabase.rpc("rank_artists_by_embedding", {
      query_embedding: embedding,
      only_successful_collabs: only_successful,
      match_count: topN,
      min_semantic_similarity: minSim
    });

    if (error) {
      console.error("Supabase RPC error:", error);
      return res.status(500).json({
        error: "Matching failed",
        details: error.message
      });
    }

    // 4️⃣ Decorate & slim results (remove semantic/historical component fields)
    const matches = (data || []).map(row => ({
      artist_id: row.artist_id,
      artist_name: row.artist_name,
      artist_tags: row.artist_tags,
      overall_score: row.final_score, // renamed for clarity in client
      recommendation: recommendationLabel(row.final_score)
    }));

    res.json({
      user_tags: tags.trim(),
      parameters: {
        top_n: topN,
        only_successful,
        min_similarity: minSim
      },
      matches,
      total_matches: matches.length
    });
  } catch (e) {
    console.error("Error in /match:", e);
    res.status(500).json({ error: "Server error", message: e.message });
  }
});

function recommendationLabel(score) {
  if (score >= 0.7) return "HIGHLY RECOMMENDED - Strong compatibility!";
  if (score >= 0.5) return "GOOD MATCH - Moderate compatibility";
  return "RISKY - Lower compatibility, but could be innovative";
}

export default router;
