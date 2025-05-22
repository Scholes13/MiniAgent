// Script to update tables and insert compatible data
require('dotenv').config({ path: './frontend/.env.local' });
const { createClient } = require('@supabase/supabase-js');

// Supabase credentials from .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

// Data compatible with your schema
const projects = [
  {
    project_name: 'LayerZero Protocol',
    token_symbol: 'ZRO',
    description: 'Cross-chain interoperability protocol enabling seamless messaging across blockchains',
    website_url: 'https://layerzero.network',
    twitter_handle: 'LayerZero_Labs',
    discovery_date: new Date().toISOString(),
    last_updated: new Date().toISOString()
  },
  {
    project_name: 'Celestia',
    token_symbol: 'TIA',
    description: 'Modular blockchain network with a focus on data availability',
    website_url: 'https://celestia.org',
    twitter_handle: 'CelestiaOrg',
    discovery_date: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    last_updated: new Date(Date.now() - 86400000).toISOString()
  },
  {
    project_name: 'zkSync',
    token_symbol: 'ZKS',
    description: 'Layer 2 scaling solution for Ethereum using zero-knowledge proofs',
    website_url: 'https://zksync.io',
    twitter_handle: 'zksync',
    discovery_date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    last_updated: new Date(Date.now() - 172800000).toISOString()
  }
];

const systemLogs = [
  {
    message: 'System started successfully',
    level: 'info',
    source: 'SYSTEM',
    created_at: new Date().toISOString()
  },
  {
    message: 'Twitter API connection established',
    level: 'info',
    source: 'TWITTER',
    created_at: new Date(Date.now() - 600000).toISOString() // 10 minutes ago
  },
  {
    message: 'Starting Twitter data collection',
    level: 'info',
    source: 'SCRAPER',
    created_at: new Date(Date.now() - 590000).toISOString() // 9.8 minutes ago
  },
  {
    message: 'Found 5 new potential projects',
    level: 'info',
    source: 'ANALYZER',
    created_at: new Date(Date.now() - 580000).toISOString() // 9.6 minutes ago
  },
  {
    message: 'Analysis complete for LayerZero Protocol',
    level: 'info',
    source: 'AI',
    created_at: new Date(Date.now() - 570000).toISOString() // 9.5 minutes ago
  }
];

async function updateTables() {
  try {
    // Insert compatible projects data
    console.log('Inserting project data...');
    const { error: projectsError } = await supabase
      .from('projects')
      .insert(projects);
    
    if (projectsError) {
      console.error('Error inserting projects:', projectsError);
    } else {
      console.log('Successfully inserted project data');
    }
    
    // Create system_logs table with SQL query
    console.log('\nCreating system_logs table...');
    
    // Use RPC to execute SQL (since we can't directly execute SQL with the JS client)
    const { error: createTableError } = await supabase.rpc('create_system_logs_table');
    
    if (createTableError) {
      console.error('Error creating system_logs table via RPC:', createTableError);
      console.log('Attempting to create table via direct insertion...');
      
      // Try to insert data to auto-create the table
      const { error: insertLogsError } = await supabase
        .from('system_logs')
        .insert(systemLogs);
      
      if (insertLogsError) {
        console.error('Error creating system_logs table via insertion:', insertLogsError);
        
        // If this also fails, we need SQL privileges
        console.log('\nTo manually create the system_logs table, run this SQL in the Supabase SQL Editor:');
        console.log(`
CREATE TABLE IF NOT EXISTS system_logs (
  id SERIAL PRIMARY KEY,
  message TEXT NOT NULL,
  level TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
        `);
      } else {
        console.log('Successfully created system_logs table and inserted data');
      }
    } else {
      console.log('Successfully created system_logs table via RPC');
      
      // Now insert the logs
      const { error: insertLogsError } = await supabase
        .from('system_logs')
        .insert(systemLogs);
      
      if (insertLogsError) {
        console.error('Error inserting logs:', insertLogsError);
      } else {
        console.log('Successfully inserted system logs data');
      }
    }
    
    console.log('\nTable update process completed');
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

updateTables(); 