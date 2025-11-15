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
      only_successful = false,
      persist_artist = false,
      artist_name = null
    } = req.body;

    // Validate required fields
    if (!tags || !tags.trim()) {
      return res.status(400).json({ error: "Tags are required" });
    }

    // Fixed parameters (no longer client configurable)
    const topN = 10;
    const minSim = 0.5;

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
      const record = { artist_name: artist_name.trim(), artist_tags: tags.trim(), embedding };
      // Try upsert by artist_name (requires unique index on artist_name). Fallback to insert if upsert not supported.
      const { error: upsertError } = await supabase
        .from("artists")
        .upsert(record, { onConflict: "artist_name" });
      if (upsertError) {
        console.warn("Upsert warning, attempting insert:", upsertError.message);
        const { error: insertError } = await supabase
          .from("artists")
          .insert(record);
        if (insertError) {
          console.warn("Insert warning:", insertError.message);
        }
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

    // 4️⃣ Filter out low overall score (< 0.5)
    const filteredData = (data || []).filter(r => (r.final_score ?? 0) >= 0.5);

    // 5️⃣ Ensure artist_tags are present: if RPC didn't include them, fetch from artists table
    let tagsById = new Map();
    if (Array.isArray(filteredData) && filteredData.length > 0) {
      const ids = filteredData.map(r => r.artist_id).filter(Boolean);
      if (ids.length > 0) {
        const { data: tagRows, error: tagErr } = await supabase
          .from("artists")
          .select("id, artist_tags")
          .in("id", ids);
        if (tagErr) {
          console.warn("Warning: could not fetch artist tags:", tagErr.message);
        } else if (Array.isArray(tagRows)) {
          tagsById = new Map(tagRows.map(r => [r.id, r.artist_tags]));
        }
      }
    }

    // 6️⃣ Decorate & slim results (remove semantic/historical component fields)
    const matches = (filteredData || []).map(row => ({
      artist_id: row.artist_id,
      artist_name: row.artist_name,
      artist_tags: row.artist_tags ?? tagsById.get(row.artist_id) ?? null,
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
