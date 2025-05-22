// This script tests the connection to Supabase
require('dotenv').config({ path: './frontend/.env.local' });
const { createClient } = require('@supabase/supabase-js');

// Supabase credentials from .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Check if credentials are provided
if (!supabaseUrl || !supabaseKey) {
  console.error('Supabase credentials are missing in frontend/.env.local');
  console.error('Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
  process.exit(1);
}

console.log('Supabase URL:', supabaseUrl);
console.log('Supabase Key:', supabaseKey.substring(0, 3) + '...' + supabaseKey.substring(supabaseKey.length - 3));

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  try {
    console.log('Testing Supabase connection...');
    
    // Simple query to test connection
    const { data, error } = await supabase
      .from('projects')
      .select('count', { count: 'exact' });
    
    if (error) {
      console.error('Error connecting to Supabase:', error);
      return false;
    }
    
    console.log('Successfully connected to Supabase!');
    console.log('Database configuration is working properly.');
    return true;
  } catch (error) {
    console.error('Unexpected error:', error);
    return false;
  }
}

testConnection()
  .then(success => {
    if (!success) {
      console.log('Supabase connection test failed. Please check your credentials.');
      process.exit(1);
    }
  })
  .catch(err => {
    console.error('Test error:', err);
    process.exit(1);
  }); 