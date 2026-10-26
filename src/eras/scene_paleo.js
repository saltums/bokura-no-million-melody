SCENES[21] = {
  cl: [['#8a5a3a', '#b88458', '#563622'], ['#6a7a8a', '#a0b4c4', '#404e5c'], ['#a8482a', '#d8784a', '#6e2a16'], ['#c8b890', '#eadcb8', '#8c7c58'], ['#4a6a8a', '#7aa0c4', '#2c445c'], ['#7a5a3a', '#a8845a', '#4a3420']],
  caps: {
    0: ['氷原で小さな火を囲み、低く唸っている', '吹きつける洞窟の入口で、声をそっと出している', '暗い洞窟の中で、火のそばに座っている', '壁画の前で、火を見つめて黙っている', '大洞窟の光の下で、息をひそめている'],
    1: ['氷原の焚き火のそばで、声を出している', '洞窟の入口で、骨を打ち鳴らしている', '洞窟の中で、火を囲み声を合わせている', '赤い獣の絵の下で、石を打ち唸っている', '大洞窟の光の柱の下で、声を響かせている'],
    2: ['氷原に歓声をあげて踊っている', '洞窟の入口で、皆と声をはり上げている', '洞窟の中で、皆が足を踏み鳴らしている', '壁画の洞窟で、皆が歌い踊っている', '大洞窟じゅうに、皆の声が轟いている'],
  },
  fn(g, st, mood, fr) {
    const mam = (x, y, s, col) => { // mammoth silhouette
      P_(g, x, y, 14 * s, 7 * s, col); P_(g, x + 2 * s, y - 2 * s, 8 * s, 3 * s, col); P_(g, x + 12 * s, y - 1 * s, 5 * s, 6 * s, col);
      P_(g, x + 16 * s, y + 3 * s, 2 * s, 6 * s, col); P_(g, x + 17 * s, y + 5 * s, 2 * s, 2 * s, '#e8d8b8');
      P_(g, x + 1 * s, y + 7 * s, 3 * s, 5 * s, col); P_(g, x + 10 * s, y + 7 * s, 3 * s, 5 * s, col);
    };
    const deer = (x, y, col) => { P_(g, x, y, 9, 4, col); P_(g, x + 8, y - 3, 3, 4, col); P_(g, x + 9, y - 6, 1, 3, col); P_(g, x + 11, y - 6, 1, 3, col); P_(g, x + 1, y + 4, 1, 4, col); P_(g, x + 7, y + 4, 1, 4, col); };
    const hand = (x, y, col) => { P_(g, x, y + 3, 5, 4, col); P_(g, x, y, 1, 4, col); P_(g, x + 1, y - 1, 1, 4, col); P_(g, x + 2, y - 2, 1, 5, col); P_(g, x + 3, y - 1, 1, 4, col); P_(g, x + 5, y + 2, 2, 2, col); };
    const fire = (cx, cy, s, ph) => {
      glow(g, cx, cy - 6, 24 + s * 10, 'rgba(255,150,50,A)', 0.3);
      for (let q = 0; q < 4; q++) P_(g, cx - 6 * s + q * 3 * s, cy + 1, 3 * s, 2, q % 2 ? '#4a2c18' : '#6a4026');
      [[0, 0, 4, 7, '#d84a1a'], [1, 2, 3, 10, '#f07a2a'], [2, 4, 1, 8, '#ffd04a']].forEach(([dx, dy, w, h, c]) => {
        const sw = ((fr + dx + ph) % 3) - 1; const ww = Math.max(1, Math.round(w * s / 1.3)), hh = Math.round(h * s / 1.3);
        P_(g, cx - (ww >> 1) + sw, cy - hh - dy + 1, ww, hh, c);
      });
      for (let i = 0; i < 4; i++) { const t = (fr * 2 + i * 6 + ph * 3) % 22; P_(g, cx - 3 + ((i * 5) % 7), cy - 10 - t, 1, 1, '#ffc060'); }
    };
    const stal = (x, w, h, col, col2) => { for (let j = 0; j < h; j++) { const ww = Math.max(1, Math.round(w * (1 - j / h))); P_(g, x + ((w - ww) >> 1), j, ww, 1, j % 5 ? col : col2); } };
    const stag = (x, w, h, base, col) => { for (let j = 0; j < h; j++) { const ww = Math.max(1, Math.round(w * (j / h))); P_(g, x + ((w - ww) >> 1), base - h + j, ww, 1, col); } };

    if (st <= 1) {
      // ---- 氷河期の氷原 ----
      vgrad(g, 0, 0, 256, 66, st ? '#16264e' : '#101c44', st ? '#8cb0cc' : '#7ea6c6', 8);
      for (let i = 0; i < 40; i++) { const x = (i * 53 + 7) % 256, y = (i * 17 + 3) % 40; if ((i + fr) % 4) P_(g, x, y, 1, 1, i % 5 ? '#dce8ff' : '#fff6c8'); }
      if (mood >= 1) { for (let b = 0; b < 3; b++) for (let x = 0; x < 256; x += 2) { const y = 10 + b * 7 + Math.round(5 * Math.sin((x + fr * 2 + b * 40) / 22)); P_(g, x, y, 2, 3, b % 2 ? 'rgba(90,230,170,.28)' : 'rgba(120,200,255,.26)'); } }
      P_(g, 214, 8, 8, 8, '#eef2d8'); P_(g, 216, 8, 4, 8, '#fffff0'); // 月
      // 遠い氷河
      for (let x = 0; x < 256; x++) { const h = 14 + Math.round(10 * Math.sin(x / 19) + 6 * Math.sin(x / 7 + 1) + 4 * Math.sin(x / 41)); P_(g, x, 60 - h, 1, h + 8, '#9ab4d0'); P_(g, x, 60 - h, 1, 2, '#e8f2ff'); P_(g, x, 66 - Math.floor(h / 3), 1, 3, '#6e8cb0'); }
      // 雪原(足元は落ち着いた色)
      vgrad(g, 0, 68, 256, 44, '#c0d4e6', '#4c5c80', 7);
      for (let i = 0; i < 60; i++) { const x = (i * 37 + 11) % 256, y = 72 + (i * 11) % 36; P_(g, x, y, 3, 1, i % 2 ? '#d8e6f4' : '#8ea4c0'); }
      P_(g, 0, 68, 256, 1, '#e8f2ff');
      // 氷のかけら
      [[10, 16], [26, 10], [232, 18], [244, 11]].forEach(([x, h], i) => { for (let j = 0; j < h; j++) P_(g, x + (j >> 3), 74 - j, 6 - (j >> 2), 1, j % 4 ? '#8cc4ee' : '#d8f0ff'); });
      if (st === 0) { fire(222, 80, 1, 0); P_(g, 36, 78, 4, 2, '#e8d8b8'); P_(g, 38, 76, 2, 2, '#e8d8b8'); }
      else {
        // 洞窟の入口: 左右の岩と庇
        for (let y = 0; y < 76; y++) { const w = y < 30 ? 56 - y : 28 + (y - 30) / 4; P_(g, 0, y, Math.round(w), 1, y % 7 ? '#3c3446' : '#2a2434'); const w2 = y < 24 ? 52 - y : 30; P_(g, 256 - Math.round(w2), y, Math.round(w2), 1, y % 6 ? '#3a3040' : '#282030'); }
        P_(g, 0, 0, 256, 6, '#2a2434'); for (let x = 0; x < 256; x += 5) P_(g, x, 6, 3, 2 + (x * 7) % 4, '#8cc4ee');
        P_(g, 0, 72, 256, 8, '#6a7a96'); P_(g, 0, 72, 256, 1, '#c8dcf0');
        // 焚き火(右)と骨(左)
        fire(224, 82, 1, 0); P_(g, 20, 78, 12, 2, '#e8d8b8'); P_(g, 18, 76, 3, 4, '#e8d8b8'); P_(g, 31, 76, 3, 4, '#e8d8b8');
        P_(g, 38, 60, 3, 14, '#efe6c8'); P_(g, 39, 56, 3, 6, '#efe6c8');
      }
    } else {
      // ---- 洞窟の内部 ----
      const big = st >= 4;
      vgrad(g, 0, 0, 256, 74, big ? '#120c20' : '#1c1220', big ? '#3a2a40' : '#4a3030', 8);
      for (let i = 0; i < 200; i++) { const x = (i * 47 + 13) % 256, y = (i * 29 + 5) % 74; P_(g, x, y, 2 + (i % 3), 1, i % 3 ? '#2c1c26' : '#4e3638'); }
      // 壁画(上のほう、うす暗い赤)
      const ink = '#a8402a', ink2 = '#d8602a';
      mam(14, 14, 1, ink); deer(86, 16, ink); mam(168, 10, 1, ink); hand(226, 20, ink2); hand(236, 14, ink2); deer(206, 34, ink);
      for (let q = 0; q < 6; q++) P_(g, 112 + q * 4, 8 + (q % 2) * 2, 2, 3, '#e8d8b8');
      if (st >= 3) { mam(40, 32, 1, ink2); deer(124, 6, ink2); hand(70, 6, ink2); hand(150, 30, ink); }
      // 洞窟の入口から氷の青い光(左上)
      if (!big) { for (let y = 2; y < 30; y++) { const w = 6 + Math.round(Math.sin(y / 4) * 2) + Math.min(10, y); P_(g, 0, y, w, 1, y < 4 ? '#e8f4ff' : '#9cd0f4'); } glow(g, 4, 14, 40, 'rgba(150,210,255,A)', 0.25); }
      // 天井のつらら・石筍
      if (st >= 2) for (let x = 6; x < 256; x += 17) stal(x, 7, 8 + (x * 3) % 9, '#3c2c3c', '#6a5a66');
      if (st >= 3) for (let x = 14; x < 256; x += 31) stal(x, 6, 14 + (x * 5) % 12, '#7ab4d8', '#d8f0ff');
      if (big) {
        for (let x = 4; x < 256; x += 13) stal(x, 8, 12 + (x * 7) % 18, '#2e2238', '#5a4a62');
        // 巨大な柱(石灰と氷)
        [[6, 34], [236, 34]].forEach(([x, w]) => { for (let y = 0; y < 82; y++) { const ww = w - Math.round(6 * Math.sin(y / 14)); P_(g, x - (w >> 1) + 12 - (ww >> 1) + (x < 100 ? 0 : -12), y, ww, 1, y % 6 ? '#4a3c52' : '#6a5a74'); } });
        for (let x = 0; x < 256; x += 2) P_(g, x, 0, 2, 3, '#1a1224');
        // 天井の穴からの光の柱
        for (let y = 0; y < 76; y++) { const half = 6 + (y >> 2); g.fillStyle = 'rgba(180,220,255,' + (0.12 - y * 0.0008).toFixed(3) + ')'; g.fillRect(128 - half, y, half * 2, 1); }
        for (let i = 0; i < 10; i++) { const y = (fr * 2 + i * 8) % 74; P_(g, 120 + ((i * 7) % 16) + ((fr + i) % 3), y, 1, 1, '#eaf6ff'); }
        // 光る氷の結晶
        [[28, 62], [44, 66], [212, 64], [228, 60]].forEach(([x, y], i) => { for (let j = 0; j < 12 + (i % 2) * 5; j++) P_(g, x + (j >> 2), y + 12 - j, 3, 1, j % 3 ? '#6cb4e8' : '#e0f6ff'); glow(g, x + 2, y + 4, 12, 'rgba(120,200,255,A)', 0.3); });
        // 牙のアーチ(左右の柱から天井へ)
        for (let j = 0; j < 30; j++) { const t = j / 30; P_(g, 34 + Math.round(t * 40), 50 - Math.round(Math.sin(t * 1.6) * 44), 3, 3, '#efe6c8'); P_(g, 219 - Math.round(t * 40), 50 - Math.round(Math.sin(t * 1.6) * 44), 3, 3, '#efe6c8'); }
        for (let y = 0; y < 76; y++) { const half = 8 + (y >> 2); g.fillStyle = 'rgba(190,225,255,0.10)'; g.fillRect(128 - half, y, half * 2, 1); }
      }
      // 床
      vgrad(g, 0, 76, 256, 36, big ? '#5a4a58' : '#4a3626', big ? '#201828' : '#241810', 6);
      for (let i = 0; i < 80; i++) { const x = (i * 31 + 7) % 256, y = 82 + (i * 13) % 28; P_(g, x, y, 3, 1, i % 2 ? '#5a4432' : '#2a1c14'); }
      P_(g, 0, 76, 256, 1, big ? '#8a7a96' : '#6a5238');
      if (big) { P_(g, 40, 76, 176, 3, '#7a6a84'); P_(g, 40, 76, 176, 1, '#a898b4'); }
      // 焚き火
      if (st === 2) fire(30, 84, 1, 0);
      if (st === 3) { fire(26, 84, 1, 0); fire(230, 84, 1, 1); }
      if (big) { fire(20, 86, 2, 0); fire(236, 86, 2, 1); fire(52, 80, 1, 2); fire(204, 80, 1, 0); }
      if (st >= 3) { P_(g, 46, 74, 10, 2, '#e8d8b8'); P_(g, 44, 72, 3, 4, '#e8d8b8'); P_(g, 55, 72, 3, 4, '#e8d8b8'); }
      if (st >= 3) { P_(g, 196, 62, 3, 14, '#efe6c8'); P_(g, 197, 58, 3, 6, '#efe6c8'); }
    }
    if (mood === 2) { for (let i = 0; i < 8; i++) { const x = (i * 33 + fr * 3) % 256, y = (i * 17 + fr * 2) % 70; P_(g, x, y, 1, 1, st >= 2 ? '#ffc060' : '#ffffff'); } }
    if (mood === 0) { g.fillStyle = 'rgba(10,8,30,.38)'; g.fillRect(0, 0, 256, 112); }
  }
};
