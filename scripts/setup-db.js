/**
 * This script helps you to create the necessary tables in Supabase.
 * Run it using Node.js after setting up Supabase credentials in your .env file.
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: './frontend/.env.local' });

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
    message: 'Analysis complete for Celestia',
    level: 'info',
    source: 'AI',
    created_at: new Date(Date.now() - 560000).toISOString(), // 9.3 minutes ago
  },
  {
    message: 'Temporarily rate limited by Twitter API',
    level: 'warning',
    source: 'TWITTER',
    created_at: new Date(Date.now() - 550000).toISOString(), // 9.1 minutes ago
  },
  {
    message: 'Retrying request after cooldown',
    level: 'info',
    source: 'TWITTER',
    created_at: new Date(Date.now() - 540000).toISOString(), // 9 minutes ago
  },
  {
    message: 'Failed to connect to OpenRouter API',
    level: 'error',
    source: 'AI',
    created_at: new Date(Date.now() - 530000).toISOString(), // 8.8 minutes ago
  },
  {
    message: 'Fallback to backup AI model successful',
    level: 'info',
    source: 'AI',
    created_at: new Date(Date.now() - 520000).toISOString(), // 8.6 minutes ago
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

async function createTables() {
  try {
    console.log('Starting database setup...');

    // Create projects table
    console.log('Creating projects table...');
    const { error: projectsError } = await supabase.rpc('create_projects_table');
    
    if (projectsError) {
      // If RPC doesn't exist, create table directly
      const { error } = await supabase.schema.createTable('projects', {
        id: { type: 'serial', primaryKey: true },
        project_name: { type: 'text', notNull: true },
        token_symbol: { type: 'text', notNull: true },
        description: { type: 'text' },
        website_url: { type: 'text' },
        twitter_handle: { type: 'text' },
        discovery_date: { type: 'timestamptz', notNull: true, default: 'now()' },
        overall_rating: { type: 'float' },
        analysis_status: { type: 'text', default: 'pending' },
      });
      
      if (error) {
        console.error('Error creating projects table:', error);
      } else {
        console.log('Projects table created successfully!');
      }
    } else {
      console.log('Projects table created via RPC!');
    }

    // Create system_logs table
    console.log('Creating system_logs table...');
    const { error: logsError } = await supabase.rpc('create_system_logs_table');
    
    if (logsError) {
      // If RPC doesn't exist, create table directly
      const { error } = await supabase.schema.createTable('system_logs', {
        id: { type: 'serial', primaryKey: true },
        message: { type: 'text', notNull: true },
        level: { type: 'text', notNull: true },
        source: { type: 'text', notNull: true },
        created_at: { type: 'timestamptz', notNull: true, default: 'now()' },
      });
      
      if (error) {
        console.error('Error creating system_logs table:', error);
      } else {
        console.log('System logs table created successfully!');
      }
    } else {
      console.log('System logs table created via RPC!');
    }

    // Insert sample data into projects table
    console.log('Inserting sample projects...');
    const { error: insertProjectsError } = await supabase
      .from('projects')
      .insert(projects);
    
    if (insertProjectsError) {
      console.error('Error inserting sample projects:', insertProjectsError);
    } else {
      console.log('Sample projects inserted successfully!');
    }

    // Insert sample data into system_logs table
    console.log('Inserting sample system logs...');
    const { error: insertLogsError } = await supabase
      .from('system_logs')
      .insert(systemLogs);
    
    if (insertLogsError) {
      console.error('Error inserting sample logs:', insertLogsError);
    } else {
      console.log('Sample logs inserted successfully!');
    }

    console.log('Database setup completed!');
  } catch (error) {
    console.error('Unexpected error during setup:', error);
  }
}

// Run the setup
createTables().catch(console.error); 