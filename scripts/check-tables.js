// Script to check table structure
require('dotenv').config({ path: './frontend/.env.local' });
const { createClient } = require('@supabase/supabase-js');

// Supabase credentials from .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

async function checkTables() {
  try {
    console.log('Checking projects table...');
    const { data: projectsData, error: projectsError } = await supabase
      .from('projects')
      .select('*')
      .limit(1);
    
    if (projectsError) {
      console.error('Error querying projects table:', projectsError);
    } else {
      if (projectsData && projectsData.length > 0) {
        console.log('Projects table exists with columns:', Object.keys(projectsData[0]));
      } else {
        console.log('Projects table exists but is empty');
      }
    }
    
    console.log('\nChecking system_logs table...');
    const { data: logsData, error: logsError } = await supabase
      .from('system_logs')
      .select('*')
      .limit(1);
    
    if (logsError) {
      console.error('Error querying system_logs table:', logsError);
    } else {
      if (logsData && logsData.length > 0) {
        console.log('System_logs table exists with columns:', Object.keys(logsData[0]));
      } else {
        console.log('System_logs table exists but is empty');
      }
    }
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

checkTables(); 