// This script creates or updates the .env.local file with Supabase credentials
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Function to get input from command line
function promptForCredentials() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    console.log('\n=== Supabase Configuration Setup ===\n');
    console.log('This script will create a .env.local file in the frontend directory');
    console.log('You\'ll need your Supabase URL and anon key from your Supabase dashboard');
    console.log('(Settings > API)\n');

    rl.question('Enter your Supabase URL (e.g., https://xxxxxxx.supabase.co): ', (url) => {
      rl.question('Enter your Supabase anon key: ', (key) => {
        rl.close();
        resolve({ url, key });
      });
    });
  });
}

async function main() {
  // Get command line arguments for Supabase URL and anon key
  let args = process.argv.slice(2);
  let supabaseUrl = args[0];
  let supabaseKey = args[1];

  // If arguments are not provided, prompt for them
  if (!supabaseUrl || !supabaseKey) {
    const credentials = await promptForCredentials();
    supabaseUrl = credentials.url;
    supabaseKey = credentials.key;
  }

  // Validate inputs
  if (!supabaseUrl || !supabaseKey) {
    console.error('Error: Supabase URL and anon key are required');
    process.exit(1);
  }

  if (supabaseUrl === 'https://your-supabase-url.supabase.co' || supabaseKey === 'your-anon-key') {
    console.error('Error: Please provide your actual Supabase credentials, not the placeholder values');
    process.exit(1);
  }

  const envContent = `# Supabase credentials
NEXT_PUBLIC_SUPABASE_URL=${supabaseUrl}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${supabaseKey}
`;

  const envPath = path.join(__dirname, '..', 'frontend', '.env.local');

  // Write the .env.local file
  try {
    fs.writeFileSync(envPath, envContent);
    console.log(`\nSuccessfully created ${envPath}`);
    console.log('Supabase credentials configured!\n');
    console.log('You can now run:');
    console.log('1. node scripts/test-supabase-connection.js - to test the connection');
    console.log('2. node scripts/setup-db.js - to set up the database tables');
    console.log('3. cd frontend && npm run dev - to start the Next.js app\n');
  } catch (error) {
    console.error('Error creating .env.local file:', error);
  }
}

main(); 