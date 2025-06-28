#!/usr/bin/env node
const { spawn } = require('child_process');

const child = spawn('fast-flights-mcp', { stdio: 'inherit' });
child.on('close', code => process.exit(code));
