SCENES[19] = {
  caps: {
    0: ['岩場の港で波音の中、竪琴を爪弾いている', '舟の影が揺れる岩場で、小声で詠んでいる', '潮風の岩場に座り、静かに竪琴を奏でている', '漁網の脇で、波の音に合わせ口ずさんでいる', '夕暮れの岩場で、竪琴を抱えて詠んでいる'],
    1: ['市場の広場で、露店の脇で竪琴を鳴らしている', '壺の並ぶ広場で、人々に詩を朗唱している', '日除け布の下で、竪琴に合わせ詠んでいる', '広場の石畳に立ち、道ゆく人に歌っている', '商人たちの前で、竪琴を奏でて詠んでいる'],
    2: ['神殿の前で、白い柱を背に竪琴を奏でている', '松明の灯る石段で、神々への賛歌を詠んでいる', '大理石の柱の間で、静かに詩を朗唱している', '神殿の石段に立ち、竪琴に合わせ歌っている', '柱の影で、供え物の前に賛歌を捧げている']
  },
  cl: [['#f2ede0', '#ffffff', '#b8b09c'], ['#2f6fb8', '#6aa4e6', '#1c4580'], ['#b8402e', '#e07858', '#7a2418'], ['#6a8a3a', '#9cc060', '#42601e'], ['#7a3a8a', '#b070c0', '#4c1e5a'], ['#e0b040', '#f8d878', '#a07818']],
  fn(g, st, mood, fr) {
    const sk = [['#78b4e6', '#d6ecf4'], ['#6aaae6', '#dcecf0'], ['#5a9ae0', '#f4e8c8'], ['#4a7ac8', '#f4d8a0'], ['#34509a', '#f6b878']][st];
    vgrad(g, 0, 0, 256, 50, sk[0], sk[1], 8);
    // sun / moon
    if (st < 3) { P_(g, 214, 10, 10, 10, '#fff4c0'); P_(g, 212, 12, 14, 6, '#fff4c0'); glow(g, 219, 15, 22, 'rgba(255,240,180,A)', 0.3); }
    else { glow(g, 200, 46, 50, 'rgba(255,190,110,A)', 0.4); P_(g, 196, 38, 12, 10, '#ffe8a0'); }
    // clouds
    [[30, 14], [120, 8], [170, 20]].forEach(([x, y], i) => { const o = (fr >> 2) % 40; const xx = (x + o + i * 3) % 280 - 14; P_(g, xx, y, 18, 3, 'rgba(255,255,255,.7)'); P_(g, xx + 4, y - 2, 10, 2, 'rgba(255,255,255,.7)'); });
    // sea
    vgrad(g, 0, 48, 256, 24, st >= 3 ? '#2a5a9a' : '#2c78c0', st >= 3 ? '#1c3c78' : '#1c4c9a', 5);
    P_(g, 0, 48, 256, 1, '#c8e4f4');
    for (let i = 0; i < 40; i++) { const x = (i * 37 + fr * (1 + i % 2)) % 256, y = 52 + (i * 11) % 18; P_(g, x, y, 3 + i % 3, 1, i % 2 ? 'rgba(255,255,255,.35)' : 'rgba(140,200,240,.4)'); }
    // far island + sail
    g.fillStyle = '#5a7a8a'; g.beginPath(); g.moveTo(0, 49); g.lineTo(30, 40); g.lineTo(70, 49); g.closePath(); g.fill();
    const bx = 150 + ((fr >> 1) % 4); P_(g, bx, 43, 1, 6, '#6a4a30'); g.fillStyle = '#f4eee0'; g.beginPath(); g.moveTo(bx + 1, 43); g.lineTo(bx + 7, 48); g.lineTo(bx + 1, 48); g.closePath(); g.fill(); P_(g, bx - 3, 49, 12, 2, '#6a4a30');

    const marble = '#e8e2d0', mL = '#fbf8ee', mD = '#b4ac94';
    function column(x, y, h, w) { // fluted column
      PO(g, x, y, w, h, marble); P_(g, x, y, 2, h, mL); P_(g, x + w - 2, y, 2, h, mD); P_(g, x + (w >> 1), y, 1, h, mD);
      PO(g, x - 2, y - 3, w + 4, 4, mL); PO(g, x - 2, y + h - 1, w + 4, 3, marble); }
    function torch(x, y) { P_(g, x, y, 2, 10, '#6a4a2a'); P_(g, x - 1, y - 1, 4, 2, '#3a2a1a'); const s = (fr + x) % 3 - 1;
      glow(g, x + 1, y - 4, 16 + (st >= 3 ? 6 : 0), 'rgba(255,170,60,A)', 0.45);
      P_(g, x - 1 + s, y - 6, 4, 5, '#e8501c'); P_(g, x + s, y - 8, 2, 5, '#ffb030'); P_(g, x + 1, y - 5, 1, 3, '#fff0a0'); }
    function olive(x, y) { P_(g, x, y - 12, 3, 14, '#5a4630'); P_(g, x - 1, y - 6, 1, 3, '#5a4630');
      [[-7, -20, 14, 8], [-9, -15, 10, 6], [1, -16, 11, 6]].forEach(([dx, dy, w, h], i) => { P_(g, x + dx, y + dy, w, h, i ? '#6a8a40' : '#82a458'); P_(g, x + dx + 2, y + dy, w - 5, 2, '#a4c474'); }); }
    function amph(x, y, c) { PO(g, x, y, 7, 9, c); P_(g, x + 2, y - 3, 3, 3, c); P_(g, x - 1, y + 1, 1, 3, c); P_(g, x + 7, y + 1, 1, 3, c); P_(g, x + 1, y + 3, 5, 1, '#3a2418'); P_(g, x + 1, y, 1, 7, 'rgba(255,255,255,.3)'); }
    function gull(x, y) { const f = (fr >> 1) & 1; P_(g, x, y + f, 2, 1, '#fff'); P_(g, x + 2, y, 2, 1, '#fff'); P_(g, x + 4, y + f, 2, 1, '#fff'); }

    if (st === 0) {
      // rocky harbour
      gull(70 + (fr % 30), 14); gull(180 - (fr % 20), 24);
      g.fillStyle = '#7a6e5c'; g.beginPath(); g.moveTo(0, 82); g.lineTo(0, 40); g.lineTo(18, 34); g.lineTo(34, 46); g.lineTo(46, 64); g.lineTo(54, 82); g.closePath(); g.fill();
      g.fillStyle = '#968a74'; g.beginPath(); g.moveTo(0, 60); g.lineTo(0, 40); g.lineTo(18, 34); g.lineTo(26, 44); g.lineTo(10, 58); g.closePath(); g.fill();
      g.fillStyle = '#6c6250'; g.beginPath(); g.moveTo(256, 82); g.lineTo(256, 46); g.lineTo(236, 40); g.lineTo(218, 56); g.lineTo(206, 82); g.closePath(); g.fill();
      olive(238, 62);
      // small fishing boat on water
      PO(g, 86, 56, 26, 5, '#8a5a34'); P_(g, 86, 56, 26, 1, '#c08a58'); P_(g, 98, 46, 1, 10, '#5a3a20');
      // ground rock
      P_(g, 0, 76, 256, 36, '#8a7e68'); for (let i = 0; i < 80; i++) { const x = (i * 31 + 7) % 256, y = 78 + (i * 13) % 32; P_(g, x, y, 4, 1, i % 2 ? '#9a8e76' : '#6c624e'); }
      P_(g, 0, 76, 256, 2, '#a89c84'); vgrad(g, 0, 90, 256, 22, '#7a6e5a', '#4a4234', 4);
      PO(g, 28, 72, 14, 8, '#a89c84'); PO(g, 214, 74, 12, 6, '#a89c84');
      // rope & net bits
      P_(g, 58, 70, 8, 6, '#b89858'); P_(g, 58, 72, 8, 1, '#8a6c38'); amph(222, 66, '#b86a3a');
    } else if (st === 1) {
      // agora: awnings + amphorae + low columns
      g.fillStyle = '#a89c84'; g.beginPath(); g.moveTo(0, 56); g.lineTo(0, 44); g.lineTo(30, 50); g.lineTo(40, 58); g.closePath(); g.fill();
      olive(14, 60); olive(244, 62);
      [[6, '#c8402e'], [206, '#2f6fb8']].forEach(([x, c], i) => {
        P_(g, x + 2, 40, 2, 38, '#6a4a2a'); P_(g, x + 40, 40, 2, 38, '#6a4a2a');
        for (let k = 0; k < 6; k++) P_(g, x + k * 7, 36 + (k & 1), 7, 8, (k & 1) ? '#f4efe0' : c); P_(g, x, 44, 44, 2, 'rgba(0,0,0,.25)');
        PO(g, x + 4, 66, 36, 8, '#8a5a34'); P_(g, x + 4, 66, 36, 2, '#c08a58');
        amph(x + 8, 57, '#b86a3a'); amph(x + 20, 57, '#8a4a2a'); P_(g, x + 30, 62, 8, 4, i ? '#d8c060' : '#c8402e');
      });
      column(52, 26, 44, 8); column(196, 26, 44, 8);
      P_(g, 48, 20, 16, 3, mL); P_(g, 192, 20, 16, 3, mL);
      // paving
      P_(g, 0, 76, 256, 36, '#b8ac94'); for (let y = 78; y < 112; y += 8) P_(g, 0, y, 256, 1, '#948a74'); for (let r = 0; r < 4; r++) for (let x = (r & 1) * 12; x < 256; x += 24) P_(g, x, 78 + r * 8, 1, 8, '#948a74');
      P_(g, 0, 76, 256, 2, '#d8ccb4'); vgrad(g, 0, 90, 256, 22, 'rgba(120,108,88,0)', '#5a5242', 4); P_(g, 0, 96, 256, 16, '#6a6252');
      gull(120 + (fr % 40), 12);
    } else if (st === 2) {
      // temple front
      const tx = 40, tw = 176;
      PO(g, tx, 14, tw, 8, mL); P_(g, tx, 14, tw, 2, '#fff'); // entablature
      for (let x = tx + 6; x < tx + tw - 6; x += 12) { P_(g, x, 17, 6, 3, '#d0c8b0'); }
      g.fillStyle = marble; g.beginPath(); g.moveTo(tx - 4, 14); g.lineTo(tx + tw / 2, 0); g.lineTo(tx + tw + 4, 14); g.closePath(); g.fill();
      g.fillStyle = '#cfc7b0'; g.beginPath(); g.moveTo(tx + 10, 13); g.lineTo(tx + tw / 2, 3); g.lineTo(tx + tw - 10, 13); g.closePath(); g.fill();
      P_(g, tx + tw / 2 - 2, 7, 4, 4, '#c8402e'); P_(g, tx + tw / 2 - 16, 10, 8, 2, '#2f6fb8'); P_(g, tx + tw / 2 + 8, 10, 8, 2, '#2f6fb8');
      P_(g, tx + 2, 22, tw - 4, 48, '#8c8470'); // dark cella wall behind
      vgrad(g, tx + 2, 22, tw - 4, 48, '#948c78', '#aca48e', 4);
      P_(g, 108, 36, 40, 34, '#4a4034'); P_(g, 110, 38, 36, 32, '#5a5040'); // doorway
      for (let k = 0; k < 8; k++) column(tx + 2 + k * 24, 22, 46, 8);
      P_(g, 84, 30, 88, 38, 'rgba(60,50,40,.35)');
      // steps
      for (let s = 0; s < 3; s++) { PO(g, tx - 12 - s * 8, 68 + s * 3, tw + 24 + s * 16, 4, s % 2 ? marble : mL); }
      olive(14, 66); olive(244, 66);
      torch(30, 54); torch(222, 54);
      P_(g, 0, 78, 256, 34, '#b8ac94'); for (let y = 80; y < 112; y += 8) P_(g, 0, y, 256, 1, '#948a74'); P_(g, 0, 78, 256, 2, '#d8ccb4'); P_(g, 0, 94, 256, 18, '#6a6252');
    } else {
      // outdoor theatre (3: rising seats, 4: grand full)
      const grand = st === 4;
      // skene wall back
      const wy = 22;
      PO(g, 36, wy, 184, 50, '#cfc4a8'); vgrad(g, 37, wy + 1, 182, 48, '#b8ac90', '#d4c8ac', 4);
      PO(g, 32, wy - 5, 192, 6, mL);
      if (grand) { for (let k = 0; k < 10; k++) if (k < 3 || k > 6) column(40 + k * 18, wy, 44, 7); for (let k = 0; k < 4; k++) { P_(g, 60 + k * 44, wy - 4 - 8, 3, 8, '#c8402e'); P_(g, 60 + k * 44, wy - 12, 12, 6, k % 2 ? '#c8402e' : '#2f6fb8'); P_(g, 60 + k * 44 + 9, wy - 12 + ((fr + k) & 1), 4, 6, k % 2 ? '#e87858' : '#6aa4e6'); } P_(g, 104, wy + 14, 48, 30, '#4a4034'); P_(g, 106, wy + 16, 44, 28, '#5a5040'); }
      else { for (let k = 0; k < 5; k++) column(52 + k * 36, wy, 44, 8); }
      // tiered seats both sides (curving)
      const rows = grand ? 8 : 5;
      for (let r = 0; r < rows; r++) {
        const y = 50 - r * 5 + (grand ? 0 : 8), inset = r * 6;
        PO(g, 0, y, 38 - inset + 10, 5, r % 2 ? '#d8cfb6' : '#c8bea4'); P_(g, 0, y, 48 - inset, 1, '#f4eedc');
        PO(g, 218 + inset - 10, y, 48 - inset, 5, r % 2 ? '#d8cfb6' : '#c8bea4'); P_(g, 218 + inset - 10, y, 48 - inset, 1, '#f4eedc');
        if (grand) for (let k = 0; k < 4; k++) { const c = [['#c8402e'], ['#2f6fb8'], ['#e0b040'], ['#7a3a8a']][(r + k) % 4][0]; P_(g, 3 + k * 9 - (r > 4 ? 0 : 0), y - 3, 3, 3, 'rgba(0,0,0,0)'); }
      }
      if (grand) { // distant spectators dots on seats
        for (let r = 0; r < 7; r++) for (let k = 0; k < 4; k++) { const c = ['#c8402e', '#2f6fb8', '#e0b040', '#7a3a8a', '#58a868'][(r * 3 + k) % 5]; const y = 47 - r * 5; P_(g, 2 + k * 9 + r * 2, y - 2 - ((fr + r + k) % 5 === 0 ? 1 : 0), 3, 4, c); P_(g, 223 + k * 9 - r * 2, y - 2 - ((fr + r + k + 2) % 5 === 0 ? 1 : 0), 3, 4, c); }
      }
      // orchestra (circular) floor
      P_(g, 0, 74, 256, 38, '#c8bca0'); P_(g, 0, 74, 256, 2, '#e8dcc0'); for (let y = 84; y < 112; y += 9) P_(g, 0, y, 256, 1, '#a89c84');
      g.fillStyle = '#d4c8ac'; g.beginPath(); g.ellipse(128, 76, 100, 7, 0, 0, 7); g.fill();
      if (grand) { g.strokeStyle = '#b8a888'; g.lineWidth = 1; g.beginPath(); g.ellipse(128, 76, 92, 5, 0, 0, 7); g.stroke(); }
      P_(g, 0, 96, 256, 16, '#6e6654');
      torch(34, 52); torch(220, 52); if (grand) { torch(14, 60); torch(240, 60); torch(78, 56); torch(176, 56); }
      if (grand) { glow(g, 128, 30, 90, 'rgba(255,210,140,A)', 0.1); }
      olive(6, 74); olive(250, 74);
    }
    if (mood === 2) {
      if (st <= 1) { for (let i = 0; i < 8; i++) { P_(g, 10 + i * 32, 2 + ((fr + i) & 1), 3, 4, ['#c8402e', '#f4efe0', '#2f6fb8', '#e0b040'][i & 3]); } }
      else { for (let i = 0; i < 10; i++) P_(g, 8 + i * 25, 6 + ((fr + i * 3) % 4), 2, 3, i % 2 ? '#e0b040' : '#c8402e'); }
      if (st >= 1) for (let i = 0; i < 5; i++) P_(g, (i * 53 + fr * 4) % 256, (fr * 3 + i * 21) % 60, 2, 2, ['#e0b040', '#c8402e', '#fff', '#58a868', '#2f6fb8'][i]);
    }
    if (mood === 0) { g.fillStyle = 'rgba(10,8,30,.38)'; g.fillRect(0, 0, 256, 112); }
  }
};
