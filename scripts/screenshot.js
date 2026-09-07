#!/usr/bin/env node
// scripts/screenshot.js — Playwright full-page screenshot
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const args = Object.fromEntries(
  process.argv.slice(2).map(a => {
    const [k, ...v] = a.replace(/^--/, '').split('=');
    return [k, v.join('=')];
  })
);

(async () => {
  const input = path.resolve(args.input || 'index.html');
  const output = path.resolve(args.output || 'screenshot.png');
  fs.mkdirSync(path.dirname(output), { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1366, height: 900 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.goto('file://' + input, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: output, fullPage: true });
  await browser.close();
  console.log(`ok: ${output}`);
})();
