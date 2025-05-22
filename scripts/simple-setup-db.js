// This script helps you to create the necessary tables in Supabase using direct SQL queries.
require('dotenv').config({ path: './frontend/.env.local' });
const { createClient } = require('@supabase/supabase-js');

// Supabase credentials from .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

// Mock data
const projects = [
  {
    project_name: 'LayerZero Protocol',
    token_symbol: 'ZRO',
    description: 'Cross-chain interoperability protocol enabling seamless messaging across blockchains',
    website_url: 'https://layerzero.network',
    twitter_handle: 'LayerZero_Labs',
    discovery_date: new Date().toISOString(),
    overall_rating: 8.7,
    analysis_status: 'completed',
  },
  {
    project_name: 'Celestia',
    token_symbol: 'TIA',
    description: 'Modular blockchain network with a focus on data availability',
    website_url: 'https://celestia.org',
    twitter_handle: 'CelestiaOrg',
    discovery_date: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    overall_rating: 9.2,
    analysis_status: 'completed',
  },
  {
    project_name: 'zkSync',
    token_symbol: 'ZKS',
    description: 'Layer 2 scaling solution for Ethereum using zero-knowledge proofs',
    website_url: 'https://zksync.io',
    twitter_handle: 'zksync',
    discovery_date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    overall_rating: 8.9,
    analysis_status: 'completed',
  },
  {
    project_name: 'Sei Network',
    token_symbol: 'SEI',
    description: 'Specialized Layer 1 blockchain for trading',
    website_url: 'https://sei.io',
    twitter_handle: 'SeiNetwork',
    discovery_date: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
    overall_rating: 7.5,
    analysis_status: 'completed',
  },
  {
    project_name: 'Starknet',
    token_symbol: 'STRK',
    description: 'Layer 2 scaling solution for Ethereum using STARKs',
    website_url: 'https://starknet.io',
    twitter_handle: 'StarkNetEco',
    discovery_date: new Date(Date.now() - 345600000).toISOString(), // 4 days ago
    overall_rating: 8.6,
    analysis_status: 'completed',
  },
];

const systemLogs = [
  {
    message: 'System started successfully',
    level: 'info',
    source: 'SYSTEM',
    created_at: new Date().toISOString(),
  },
  {
    message: 'Twitter API connection established',
    level: 'info',
    source: 'TWITTER',
    created_at: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
  },
  {
    message: 'Starting Twitter data collection',
    level: 'info',
    source: 'SCRAPER',
    created_at: new Date(Date.now() - 590000).toISOString(), // 9.8 minutes ago
  },
  {
    message: 'Found 5 new potential projects',
    level: 'info',
    source: 'ANALYZER',
    created_at: new Date(Date.now() - 580000).toISOString(), // 9.6 minutes ago
  },
  {
    message: 'Analysis complete for LayerZero Protocol',
    level: 'info',
    source: 'AI',
    created_at: new Date(Date.now() - 570000).toISOString(), // 9.5 minutes ago
  },
  {
    message: 'All projects have been successfully saved to the database',
    level: 'info',
    source: 'DATABASE',
    created_at: new Date(Date.now() - 510000).toISOString(), // 8.5 minutes ago
  },
  {
    message: 'System idle, waiting for next scheduled run',
    level: 'info',
    source: 'SYSTEM',
    created_at: new Date(Date.now() - 500000).toISOString(), // 8.3 minutes ago
  },
];

async function createTablesAndData() {
  try {
    console.log('Starting database setup...');

    // Create the projects table directly using SQL
    console.log('Creating projects table...');
    
    // Check if table exists first
    const { data: projectsTable, error: checkProjectsError } = await supabase
      .from('projects')
      .select('*', { count: 'exact', head: true });
      
    if (checkProjectsError && checkProjectsError.code === '42P01') {
      // Table doesn't exist, create it using REST API
      console.log('Projects table does not exist, creating it...');
      
      // Insert projects to let Supabase auto-create the table
      const { error: insertError } = await supabase
        .from('projects')
        .insert(projects);
        
      if (insertError) {
        console.error('Error creating projects table:', insertError);
      } else {
        console.log('Projects table created and data inserted successfully!');
      }
    } else {
      console.log('Projects table already exists');
      
      // Insert more data
      const { error: insertError } = await supabase
        .from('projects')
        .insert(projects);
        
      if (insertError) {
        console.error('Error inserting data to projects table:', insertError);
      } else {
        console.log('Additional project data inserted successfully!');
      }
    }
    
    // Check if system_logs table exists 
    const { data: logsTable, error: checkLogsError } = await supabase
      .from('system_logs')
      .select('*', { count: 'exact', head: true });
      
    if (checkLogsError && checkLogsError.code === '42P01') {
      // Table doesn't exist, create it
      console.log('System logs table does not exist, creating it...');
      
      // Insert logs to let Supabase auto-create the table
      const { error: insertLogsError } = await supabase
        .from('system_logs')
        .insert(systemLogs);
        
      if (insertLogsError) {
        console.error('Error creating system_logs table:', insertLogsError);
      } else {
        console.log('System logs table created and data inserted successfully!');
      }
    } else {
      console.log('System logs table already exists');
      
      // Insert more data
      const { error: insertLogsError } = await supabase
        .from('system_logs')
        .insert(systemLogs);
        
      if (insertLogsError) {
        console.error('Error inserting data to system_logs table:', insertLogsError);
      } else {
        console.log('Additional system logs data inserted successfully!');
      }
    }

    console.log('Database setup completed!');
  } catch (error) {
    console.error('Unexpected error during setup:', error);
  }
}

// Run the setup
createTablesAndData().catch(console.error); 