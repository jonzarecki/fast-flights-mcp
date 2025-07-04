#!/usr/bin/env node
const { spawn } = require('child_process');

// Run the Python entrypoint directly to avoid missing CLI errors
const child = spawn('python3', ['-m', 'fast_flights_mcp.server', ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: `${__dirname}/src`,
  },
});
child.on('close', code => process.exit(code));
