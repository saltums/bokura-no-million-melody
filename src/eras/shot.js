// usage: node /home/claude/eras/shot.js <id>   -> /tmp/w_scene_<id>/sheet.png (stage 0,2,4 x mood 0,2; grey boxes = performers)
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const id = process.argv[2]; const dir = '/tmp/w_scene_' + id; fs.mkdirSync(dir, { recursive: true });
  const t = fs.readFileSync('/home/claude/proto_template.html', 'utf8').split('\n');
  const a0 = t.findIndex(l => l.startsWith('const OL')), a1 = t.findIndex(l => l.startsWith('function PO')); const helpers = t.slice(a0, a1 + 1).join('\n');
  const src = fs.readFileSync('/home/claude/eras/scene_' + id + '.js', 'utf8');
  const html = `<canvas id=c width=768 height=224></canvas><script>${helpers}
const SCENES = {};
${src}
const key = Object.keys(SCENES)[0]; const S0 = SCENES[key]; const c = document.getElementById('c'); const big = c.getContext('2d');
const cl = (S0.cl || []);
[0, 2, 4].forEach((st, i) => [0, 2].forEach((mood, j) => { const o = document.createElement('canvas'); o.width = 256; o.height = 112; const g = o.getContext('2d'); g.imageSmoothingEnabled = false; S0.fn(g, st, mood, 3);
  [[96, 76], [128, 76], [160, 76]].forEach(([x, y], k) => { const col = (cl[k % Math.max(1, cl.length)] || ['#888'])[0]; g.fillStyle = 'rgba(0,0,0,.55)'; g.fillRect(x - 8, y - 48, 18, 48); g.fillStyle = col; g.fillRect(x - 7, y - 30, 16, 30); g.fillStyle = '#e8c39e'; g.fillRect(x - 4, y - 44, 10, 12); });
  big.imageSmoothingEnabled = false; big.drawImage(o, i * 256, j * 112); }));
window.__ok = 1;<\/script>`;
  fs.writeFileSync(dir + '/h.html', html);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); const p = await b.newPage({ viewport: { width: 768, height: 224 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); await p.goto('file://' + dir + '/h.html'); await p.waitForTimeout(300);
  await p.locator('#c').screenshot({ path: dir + '/sheet.png' }); console.log('errs', errs, '->', dir + '/sheet.png'); await b.close();
})();
