-- Schema untuk tabel crypto_airdrops di Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create table for storing crypto airdrop opportunities
CREATE TABLE IF NOT EXISTS crypto_airdrops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tweet_id TEXT NOT NULL,
    tweet_text TEXT NOT NULL,
    tweet_url TEXT,
    author TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    hashtag TEXT,
    score INTEGER,
    engagement JSONB,
    is_legitimate TEXT,  -- Yes/No/Maybe
    related_crypto TEXT,
    required_action TEXT,
    risk_level TEXT,     -- Low/Medium/High
    risk_explanation TEXT,
    estimated_value TEXT,
    claim_steps JSONB,
    additional_notes TEXT,
    raw_data JSONB,
    status TEXT DEFAULT 'new',  -- new, processed, verified, scam
    verified_by TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(tweet_id)
);

-- Create index on tweet_id
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_tweet_id ON crypto_airdrops(tweet_id);

-- Create index on is_legitimate
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_is_legitimate ON crypto_airdrops(is_legitimate);

-- Create index on risk_level
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_risk_level ON crypto_airdrops(risk_level);

-- Create index on related_crypto
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_related_crypto ON crypto_airdrops(related_crypto);

-- Create index on created_at
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_created_at ON crypto_airdrops(created_at);

-- Create index on status
CREATE INDEX IF NOT EXISTS idx_crypto_airdrops_status ON crypto_airdrops(status);

-- Enable Row Level Security
ALTER TABLE crypto_airdrops ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to select data
CREATE POLICY "Users can view all airdrops" 
ON crypto_airdrops FOR SELECT 
TO authenticated 
USING (true);

-- Create policy for authorized users to insert data
CREATE POLICY "Only authorized users can insert airdrops" 
ON crypto_airdrops FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() IN (
    SELECT user_id FROM authorized_airdrop_managers
));

-- Create policy for authorized users to update data
CREATE POLICY "Only authorized users can update airdrops" 
ON crypto_airdrops FOR UPDATE 
TO authenticated 
USING (auth.uid() IN (
    SELECT user_id FROM authorized_airdrop_managers
)) 
WITH CHECK (auth.uid() IN (
    SELECT user_id FROM authorized_airdrop_managers
));

-- Create authorized users table for management
CREATE TABLE IF NOT EXISTS authorized_airdrop_managers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users,
    UNIQUE(user_id)
);

-- Enable Row Level Security on the managers table
ALTER TABLE authorized_airdrop_managers ENABLE ROW LEVEL SECURITY;

-- Only admins can manage the authorized_airdrop_managers table
CREATE POLICY "Only admins can manage authorized users" 
ON authorized_airdrop_managers 
TO authenticated 
USING (auth.uid() IN (
    SELECT user_id FROM admin_users
));

-- Create admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable Row Level Security on the admin table
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Only admins can view the admin_users table
CREATE POLICY "Only admins can view admin_users" 
ON admin_users FOR SELECT
TO authenticated 
USING (auth.uid() IN (
    SELECT user_id FROM admin_users
));

-- Create a view to easily see the most promising opportunities
CREATE OR REPLACE VIEW v_promising_opportunities AS
SELECT 
    id, 
    tweet_id, 
    tweet_text, 
    tweet_url, 
    author, 
    created_at, 
    processed_at,
    related_crypto, 
    is_legitimate, 
    risk_level, 
    score,
    required_action
FROM 
    crypto_airdrops
WHERE 
    is_legitimate = 'Yes' 
    AND risk_level IN ('Low', 'Medium')
    AND status = 'new'
ORDER BY 
    score DESC, 
    created_at DESC; 