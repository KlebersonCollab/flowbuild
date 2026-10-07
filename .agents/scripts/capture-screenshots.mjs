import puppeteer from '../../frontend/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';
import path from 'path';
import fs from 'fs';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOTS_DIR = path.resolve('docs/screenshots');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function run() {
  console.log('🚀 Iniciando Chrome via puppeteer-core...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    defaultViewport: {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1.25,
    },
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--window-size=1920,1080',
    ],
  });

  const page = await browser.newPage();
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 30000 });
  await page.waitForSelector('header', { timeout: 10000 });
  await new Promise(r => setTimeout(r, 1500));

  const clickTopNavButton = async (text) => {
    return page.evaluate((t) => {
      const header = document.querySelector('header');
      if (!header) return false;
      const buttons = Array.from(header.querySelectorAll('button'));
      const btn = buttons.find(b => b.textContent && b.textContent.includes(t));
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    }, text);
  };

  console.log('📸 1. Carregando template Decisão Condicional para o Canvas Hero...');
  await clickTopNavButton('Modelos');
  await new Promise(r => setTimeout(r, 600));

  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.textContent && b.textContent.includes('Decisão Condicional'));
    if (btn) btn.click();
  });
  await new Promise(r => setTimeout(r, 1500));

  // Deselect any node by clicking empty canvas area
  await page.mouse.click(600, 350);
  await new Promise(r => setTimeout(r, 800));

  const heroPath = path.join(SCREENSHOTS_DIR, 'canvas-hero.png');
  await page.screenshot({ path: heroPath, fullPage: false });
  console.log(`✅ Salvo: ${heroPath}`);

  console.log('📸 2. Abrindo Gerenciador de Fluxos (Worktree Hierarchy)...');
  await clickTopNavButton('Meus Fluxos');
  await new Promise(r => setTimeout(r, 1500));

  const flowsModalPath = path.join(SCREENSHOTS_DIR, 'flows-manager-worktree.png');
  await page.screenshot({ path: flowsModalPath, fullPage: false });
  console.log(`✅ Salvo: ${flowsModalPath}`);

  console.log('📸 3. Fechando Gerenciador de Fluxos e abrindo Modal de Variáveis...');
  // Press Escape to close flows modal
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 800));

  await clickTopNavButton('Variáveis');
  await new Promise(r => setTimeout(r, 1500));

  const varModalPath = path.join(SCREENSHOTS_DIR, 'variables-modal.png');
  await page.screenshot({ path: varModalPath, fullPage: false });
  console.log(`✅ Salvo: ${varModalPath}`);

  // Press Escape to close variables modal
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 800));

  console.log('📸 4. Executando fluxo e capturando Console Telemetria SSE...');
  await clickTopNavButton('Executar Fluxo');
  // Wait for execution to stream and complete
  await new Promise(r => setTimeout(r, 3500));

  const telemetryPath = path.join(SCREENSHOTS_DIR, 'execution-drawer-telemetry.png');
  await page.screenshot({ path: telemetryPath, fullPage: false });
  console.log(`✅ Salvo: ${telemetryPath}`);

  await browser.close();
  console.log('🎉 Todas as 4 capturas foram geradas com layout perfeito!');
}

run().catch((err) => {
  console.error('❌ Erro na captura:', err);
  process.exit(1);
});
