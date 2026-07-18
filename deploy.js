#!/usr/bin/env node
/**
 * SUZUME DEPLOY — One-command deployment
 * Serves files locally + creates a public tunnel
 * No authentication needed!
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const PORT = 3456;
const ROOT = __dirname;

// MIME types
const MIME = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
};

// ─── Simple static file server ───
const server = http.createServer((req, res) => {
  let filePath = path.join(ROOT, req.url === '/' ? '/saas-website/index.html' : req.url);

  // If requesting a directory, try index.html
  if (req.url.endsWith('/')) {
    filePath = path.join(filePath, 'index.html');
  }

  const ext = path.extname(filePath);
  const contentType = MIME[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // Try alternate paths
        const altPaths = [
          path.join(ROOT, 'saas-website', req.url),
          path.join(ROOT, 'presentation', req.url),
          path.join(ROOT, req.url),
        ];
        tryNext(altPaths, 0, res, contentType);
      } else {
        res.writeHead(500);
        res.end('Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

function tryNext(paths, index, res, contentType) {
  if (index >= paths.length) {
    res.writeHead(404);
    res.end('Not Found');
    return;
  }
  fs.readFile(paths[index], (err, content) => {
    if (err) {
      tryNext(paths, index + 1, res, contentType);
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n  ✅ Local server running at:`);
  console.log(`      http://localhost:${PORT}/saas-website/`);
  console.log(`      http://localhost:${PORT}/presentation/`);
  console.log(`\n  ⏳ Creating public tunnel...`);

  // ─── Create localtunnel ───
  const localtunnel = require('localtunnel');

  (async () => {
    try {
      const tunnel = await localtunnel({
        port: PORT,
        subdomain: 'suzume-showcase-' + Date.now().toString(36),
        local_host: '127.0.0.1',
      });

      console.log(`\n  🎉  PUBLIC URL — SHARE THIS!`);
      console.log(`  ════════════════════════════`);
      console.log(`  🔗  ${tunnel.url}`);
      console.log(`  ════════════════════════════`);
      console.log(`\n  📱  SaaS Website:`);
      console.log(`      ${tunnel.url}/saas-website/`);
      console.log(`\n  📖  Presentation:`);
      console.log(`      ${tunnel.url}/presentation/`);
      console.log(`\n  ⚠️   Keep this terminal window OPEN!`);
      console.log(`  🔒  Press Ctrl+C to stop.\n`);

      tunnel.on('close', () => {
        console.log('\n  Tunnel closed.');
        process.exit(0);
      });
    } catch (err) {
      console.error('\n  ❌ Tunnel error:', err.message);
      console.log('\n  ⚠️  Local server still running at above URLs.');
      process.exit(1);
    }
  })();
});
