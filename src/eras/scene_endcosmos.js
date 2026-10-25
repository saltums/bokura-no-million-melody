SCENES[22] = { cl: [['#6a4ab8', '#9a7ee0', '#3e2a7a'], ['#2e5aa8', '#5e8ee0', '#1a3670'], ['#a8487e', '#d878ac', '#6a2a50'], ['#3a8a9a', '#6ac0cc', '#1e5664'], ['#c8a85a', '#f0d890', '#84682a'], ['#c8c8e8', '#f4f4ff', '#8888b0']],
caps: {
0:['闇に浮かぶ小さな足場で歌っている','星屑の流れる足場で口ずさんでいる','遠い星ひとつの下で歌っている','かすかな星明かりの中で歌っている','静かな闇の端で歌っている'],
1:['小さな足場で星に向かって歌っている','星屑の舞台で静かに歌っている','消えかけの星座の下で歌っている','星々の灯りに囲まれて歌っている','最後の大星の下で歌っている'],
2:['足場の灯りを揺らして歌っている','舞い散る星屑の中で歌っている','星座の円舞台で声を響かせている','星の灯りが踊る中で歌っている','最後の星々に見守られて歌っている']
},
fn(g, st, mood, fr) {
  vgrad(g, 0, 0, 256, 112, '#07041a', '#1a1040', 8);
  // faint nebula bands (more with stage)
  if (st >= 1) glow(g, 50, 30, 50 + st * 6, 'rgba(110,60,170,A)', 0.14 + st * 0.03);
  if (st >= 3) glow(g, 215, 24, 56, 'rgba(50,90,180,A)', 0.2);
  // dying stars: sparse, twinkle with fr
  const n = 14 + st * 10 + mood * 6;
  for (let i = 0; i < n; i++) {
    const x = (i * 71 + 11) % 256, y = (i * 37 + 5) % 62;
    if (x > 56 && x < 204 && y > 26 && y < 70 && i % 3) continue;
    if ((i + fr) % 6 === 0) continue;
    const c = i % 5 === 0 ? '#ffd8a0' : (i % 3 ? '#b8b0e8' : '#8ab0f0');
    P_(g, x, y, 1, 1, c);
    if (i % 11 === 0 && st >= 1) { P_(g, x - 1, y, 3, 1, 'rgba(200,190,255,.4)'); P_(g, x, y - 1, 1, 3, 'rgba(200,190,255,.4)'); }
  }
  // a big fading red giant far away
  if (st >= 2) { glow(g, 28, 22, 22, 'rgba(200,80,60,A)', 0.35); P_(g, 26, 20, 4, 4, '#a85a58'); P_(g, 27, 21, 2, 2, '#e09070'); }
  // constellation lines and nodes (faded)
  if (st >= 2) {
    const pts = [[14, 56], [34, 44], [58, 52], [78, 36], [182, 34], [206, 48], [228, 38], [244, 54]];
    g.fillStyle = 'rgba(160,150,230,.35)';
    [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]].forEach(([a, b]) => { const A = pts[a], B = pts[b]; for (let k = 0; k <= 10; k++) if ((k + fr + a) % 4) g.fillRect(Math.round(A[0] + (B[0] - A[0]) * k / 10), Math.round(A[1] + (B[1] - A[1]) * k / 10), 1, 1); });
    pts.forEach((p, i) => { P_(g, p[0], p[1], 2, 2, (i + fr) % 4 ? '#d8d0ff' : '#7a70b0'); });
  }
  // the void below
  vgrad(g, 0, 84, 256, 28, '#0c0826', '#05030f', 4);
  // drifting stardust
  const dn = 6 + st * 5 + mood * 4;
  for (let i = 0; i < dn; i++) { const x = (i * 43 + fr * (1 + i % 2)) % 256, y = 82 + (i * 17) % 26; P_(g, x, y, 1, 1, i % 2 ? '#6a58b0' : '#4a6ab0'); }

  // platform
  const hw = [40, 62, 84, 100, 118][st];
  const L = 128 - hw, W = hw * 2;
  if (st <= 1) {
    // small floating rock slab
    g.fillStyle = '#2c2456'; g.beginPath(); g.moveTo(L, 74); g.lineTo(L + W, 74); g.lineTo(L + W - 12, 90); g.lineTo(L + W - 28, 98); g.lineTo(128, 102); g.lineTo(L + 24, 94); g.lineTo(L + 10, 86); g.closePath(); g.fill();
    PO(g, L, 72, W, 4, '#5a4a98'); P_(g, L, 72, W, 1, '#8a7ad0');
    for (let i = 0; i < 8; i++) P_(g, L + 6 + i * (W / 8), 80 + (i * 5) % 10, 3, 1, '#443a78');
    P_(g, L + W + 6, 90 + (fr % 3), 3, 3, '#3a3068'); P_(g, L - 10, 84 - (fr % 3), 2, 2, '#3a3068');
  } else {
    // round stage seen from side: ring of light
    const cy = 76;
    g.fillStyle = '#241c4c'; g.beginPath(); g.ellipse(128, cy + 6, hw, 11, 0, 0, 7); g.fill();
    g.fillStyle = '#3c3078'; g.beginPath(); g.ellipse(128, cy, hw, 8, 0, 0, 7); g.fill();
    g.fillStyle = '#4c3e90'; g.beginPath(); g.ellipse(128, cy - 1, hw - 6, 6, 0, 0, 7); g.fill();
    for (let k = 0; k < 28; k++) { const an = k / 28 * Math.PI * 2; const x = Math.round(128 + Math.cos(an) * (hw - 3)), y = Math.round(cy - 1 + Math.sin(an) * 7); P_(g, x, y, 2, 1, (k + fr) % 5 ? '#c8b8ff' : '#6a5aa8'); }
    P_(g, 128 - hw + 4, cy + 8, 2 * hw - 8, 1, '#2a2058');
  }

  // st1+: lamp posts of starlight on the platform edges
  if (st >= 1) {
    const lamp = (x, y, h) => { P_(g, x, y - h, 1, h, '#6a5aa8'); const f = (fr + x) % 3; glow(g, x, y - h - 2, 12 + st * 2, 'rgba(255,200,140,A)', 0.4); P_(g, x - 1, y - h - 3, 3, 3, f ? '#ffe2a8' : '#f0b878'); };
    lamp(L + 4, 72, 12); lamp(L + W - 5, 72, 12);
  }
  // st2+: floating star-lanterns
  if (st >= 2) for (let i = 0; i < 4 + (st - 2) * 3; i++) {
    const x = [30, 226, 46, 212, 18, 238, 70, 190, 10][i], y = 30 + (i * 13) % 26 + Math.round(Math.sin((fr + i * 2) / 2.5) * 2);
    glow(g, x, y, 9, 'rgba(255,190,130,A)', 0.4); P_(g, x - 1, y - 1, 3, 3, i % 2 ? '#ffe2a8' : '#ffc890'); P_(g, x, y - 2, 1, 1, '#fff4d8');
  }
  // st3+: pillars of dim light and ring of last stars above
  if (st >= 3) {
    for (let i = 0; i < 9; i++) { const an = Math.PI + i / 8 * Math.PI; const x = Math.round(128 + Math.cos(an) * 112), y = Math.round(52 + Math.sin(an) * 40); glow(g, x, y, 10, 'rgba(190,170,255,A)', 0.4); P_(g, x - 1, y - 1, 3, 3, (i + fr) % 3 ? '#e8e0ff' : '#a898e0'); P_(g, x, y - 3, 1, 7, 'rgba(220,210,255,.5)'); P_(g, x - 3, y, 7, 1, 'rgba(220,210,255,.5)'); }
  }
  // st4: last great star watching, soft warm beams down onto the stage
  if (st >= 4) {
    const pul = fr % 4;
    glow(g, 128, 10, 40 + pul, 'rgba(255,200,150,A)', 0.3);
    P_(g, 124, 6, 8, 8, '#ffe8c0'); P_(g, 122, 8, 12, 4, '#ffd8a0'); P_(g, 126, 4, 4, 12, '#ffd8a0'); P_(g, 126, 8, 4, 4, '#fffaf0');
    for (let y = 16; y < 70; y += 2) for (let x = 0; x < 2; x++) P_(g, 120 + x * 14 - (y - 16) / 6, y, 1, 1, 'rgba(255,220,170,.18)');
    for (let i = 0; i < 10; i++) { const t = (fr * 2 + i * 7) % 40; P_(g, 100 + (i * 13) % 56, 20 + t, 1, 1, '#ffe2b0'); }
  }
  // mood 2: more sparkling motes
  if (mood === 2) for (let i = 0; i < 14; i++) { const x = (i * 53 + 17) % 256, y = (i * 29 + fr * 2 + i * 7) % 70; if (x > 60 && x < 200 && y > 28) continue; P_(g, x, y, 1, 1, i % 2 ? '#ffe2b0' : '#c8b8ff'); }
  // ground fade at the bottom for the audience
  vgrad(g, 0, 90, 256, 22, '#0a0624', '#04020c', 3);
  if (mood === 0) { g.fillStyle = 'rgba(10,8,30,.38)'; g.fillRect(0, 0, 256, 112); }
} };
