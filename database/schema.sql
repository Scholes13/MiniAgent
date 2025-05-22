-- Skema database untuk aplikasi Crypto Airdrop Analyzer
-- Gunakan di Supabase SQL Editor

-- Tabel untuk menyimpan data proyek cryptocurrency
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  project_name TEXT NOT NULL,
  token_symbol TEXT,
  description TEXT,
  website_url TEXT,
  twitter_handle TEXT,
  discovery_date TIMESTAMPTZ DEFAULT NOW(),
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian project_name
CREATE INDEX idx_projects_name ON projects (project_name);

-- Tabel untuk menyimpan data dari Twitter
CREATE TABLE twitter_data (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  tweet_id TEXT NOT NULL,
  tweet_text TEXT NOT NULL,
  tweet_url TEXT,
  author_name TEXT,
  author_username TEXT,
  followers_count INTEGER,
  verified BOOLEAN,
  engagement_score FLOAT,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian berdasarkan project_id
CREATE INDEX idx_twitter_project_id ON twitter_data (project_id);

-- Tabel untuk menyimpan hasil analisis dari AI
CREATE TABLE ai_analysis (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  legitimacy_score INTEGER CHECK (legitimacy_score BETWEEN 1 AND 10),
  potential_score INTEGER CHECK (potential_score BETWEEN 1 AND 10),
  revenue_estimate TEXT,
  risk_level TEXT,
  overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 10),
  supporting_entities JSONB, -- Format: [{"name": "Entity Name", "type": "VC/Exchange/Influencer"}]
  analysis_text TEXT,
  ai_model_used TEXT,
  analysis_date TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian berdasarkan project_id dan overall_rating
CREATE INDEX idx_ai_project_id ON ai_analysis (project_id);
CREATE INDEX idx_ai_rating ON ai_analysis (overall_rating DESC);

-- Tabel untuk menyimpan data tokenomics dari proyek
CREATE TABLE tokenomics (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  total_supply NUMERIC,
  circulating_supply NUMERIC,
  airdrop_percentage NUMERIC,
  team_allocation_percentage NUMERIC,
  vesting_details JSONB,
  token_type TEXT, -- ERC20, BEP20, SPL, dll
  blockchain TEXT, -- Ethereum, BSC, Solana, dll
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian berdasarkan project_id
CREATE INDEX idx_tokenomics_project_id ON tokenomics (project_id);

-- Tabel untuk menyimpan data market yang dapat diupdate secara berkala
CREATE TABLE market_data (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  price_usd NUMERIC,
  market_cap NUMERIC,
  volume_24h NUMERIC,
  price_change_24h NUMERIC,
  exchanges JSONB, -- Format: [{"name": "Exchange Name", "pair": "Token/USDT"}]
  data_source TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian berdasarkan project_id
CREATE INDEX idx_market_project_id ON market_data (project_id);
CREATE INDEX idx_market_timestamp ON market_data (timestamp DESC);

-- Tabel untuk menyimpan watchlist pengguna
CREATE TABLE user_watchlist (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id), -- Menggunakan autentikasi Supabase
  project_id INTEGER REFERENCES projects(id),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indeks untuk pencarian berdasarkan user_id
CREATE INDEX idx_watchlist_user_id ON user_watchlist (user_id);
CREATE INDEX idx_watchlist_project_id ON user_watchlist (project_id);

-- Constraints tambahan untuk memastikan uniqueness
ALTER TABLE twitter_data ADD CONSTRAINT unique_tweet_per_project UNIQUE (project_id, tweet_id);
ALTER TABLE ai_analysis ADD CONSTRAINT unique_analysis_per_project UNIQUE (project_id, analysis_date);
ALTER TABLE tokenomics ADD CONSTRAINT unique_tokenomics_per_project UNIQUE (project_id);
ALTER TABLE user_watchlist ADD CONSTRAINT unique_user_project_watchlist UNIQUE (user_id, project_id);

-- Menambahkan RLS (Row Level Security) pada tabel user_watchlist
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;

-- Policy agar pengguna hanya dapat melihat dan mengedit watchlist mereka sendiri
CREATE POLICY "Users can view their own watchlist" 
ON user_watchlist FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to their own watchlist" 
ON user_watchlist FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own watchlist" 
ON user_watchlist FOR UPDATE 
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete from their own watchlist" 
ON user_watchlist FOR DELETE 
USING (auth.uid() = user_id);

-- Fungsi untuk mengupdate last_updated pada project saat ada perubahan data terkait
CREATE OR REPLACE FUNCTION update_project_last_updated()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE projects SET last_updated = NOW() WHERE id = NEW.project_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger untuk mengupdate project.last_updated
CREATE TRIGGER update_project_last_updated_on_twitter_data
AFTER INSERT OR UPDATE ON twitter_data
FOR EACH ROW EXECUTE FUNCTION update_project_last_updated();

CREATE TRIGGER update_project_last_updated_on_ai_analysis
AFTER INSERT OR UPDATE ON ai_analysis
FOR EACH ROW EXECUTE FUNCTION update_project_last_updated();

CREATE TRIGGER update_project_last_updated_on_tokenomics
AFTER INSERT OR UPDATE ON tokenomics
FOR EACH ROW EXECUTE FUNCTION update_project_last_updated();

CREATE TRIGGER update_project_last_updated_on_market_data
AFTER INSERT OR UPDATE ON market_data
FOR EACH ROW EXECUTE FUNCTION update_project_last_updated(); 