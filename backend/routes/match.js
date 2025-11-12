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
    const { tags } = req.body;
    if (!tags || tags.trim() === "") {
      return res.status(400).json({ error: "Tags are required" });
    }

    // Get clients (initialized with env vars)
    const openai = getOpenAIClient();
    const supabase = getSupabaseClient();

    // 1️⃣ Generate embedding for the input tags
    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: tags,
    });

    const [{ embedding }] = embeddingResponse.data;

    // 2️⃣ Query Supabase for the most similar artists
    const { data, error } = await supabase.rpc("match_artists", {
      query_embedding: embedding,
      match_threshold: 0.75, // similarity threshold (0–1)
      match_count: 5,        // return top 5 matches
    });

    if (error) {
      console.error("Supabase RPC error:", error);
      return res.status(500).json({ error: "Supabase query failed" });
    }

    // 3️⃣ Return clean response
    res.json({
      matches: data || [],
      count: data?.length || 0,
    });

  } catch (err) {
    console.error("Error in /match:", err);
    res.status(500).json({ error: "Server error" });
  }
});

export default router;
