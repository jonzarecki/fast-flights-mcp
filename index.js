#!/usr/bin/env node
const { spawn } = require('child_process');

// Check for fetch mode argument
const args = process.argv.slice(2);
let fetchMode = process.env.FAST_FLIGHTS_FETCH_MODE || 'common';
const fetchModeIndex = args.findIndex(arg => arg.startsWith('--fetch-mode='));
if (fetchModeIndex !== -1) {
  fetchMode = args[fetchModeIndex].split('=')[1];
  args.splice(fetchModeIndex, 1); // Remove the argument so it doesn't get passed to Python
}

// Run the Python entrypoint directly to avoid missing CLI errors
const child = spawn('python3', ['-m', 'fast_flights_mcp.server', ...args], {
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: `${__dirname}/src`,
    FAST_FLIGHTS_FETCH_MODE: fetchMode,
  },
});
child.on('close', code => process.exit(code));
