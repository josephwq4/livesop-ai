import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Fail gracefully if env vars are missing
let supabaseClient = null;

if (supabaseUrl && supabaseAnonKey) {
    try {
        supabaseClient = createClient(supabaseUrl, supabaseAnonKey);
    } catch (error) {
        console.error("Supabase Init Error:", error);
    }
} else {
    console.error('CRITICAL: Missing Supabase Environment Variables! Check Vercel Settings.');
}

export const supabase = supabaseClient;
