SCENES[18] = {
  caps: {
    0: ['薄暗い礼拝堂の隅で、ひっそり演奏している', '人の少ない館の広間で、静かに演奏している', '空いた舞踏の間で、小さく演奏している', '誰も踊らない舞踏室で、静かに演奏している', '王宮の大広間の片隅で、息をひそめて演奏している'],
    1: ['礼拝堂の隅で、蝋燭の灯りの下で演奏している','礼拝堂の石壁の前で、オルガンと演奏している','燭台の灯る館の広間で、演奏している','肖像画の並ぶ広間で、客に演奏している','宮廷の大広間で、堂々と演奏している'],
    2: ['礼拝堂で、集まった人々の前で演奏している','礼拝堂に蝋燭が増え、にぎやかに演奏している','舞踏の間で、シャンデリアの下で演奏している','金の広間で、踊る人々に演奏している','王宮の大広間で、拍手の中で演奏している']
  },
  cl: [['#7a2a4a', '#b0587a', '#4c1830'], ['#2a4a8a', '#5a82c4', '#182c58'], ['#c8a040', '#f0d078', '#8a6a1e'], ['#e8dcc8', '#ffffff', '#a89c88'], ['#2e6a58', '#58a088', '#1a4034'], ['#5a2a6a', '#8a58a0', '#361444']],
  fn(g, st, mood, fr) {
    const fl = (x, y, s) => { // candle flame
      const k = (fr + x) % 3; P_(g, x, y - 2 - (k === 0 ? 1 : 0), 1, 2, '#fff0a0'); P_(g, x, y - 1, 1, 1, '#ffb030');
    };
    const candle = (x, y, h) => { P_(g, x, y, 2, h, '#f4ecd8'); fl(x, y, 0); glow(g, x, y - 2, 9 + mood * 2, 'rgba(255,200,100,A)', 0.22 + mood * 0.06); };
    const arch = (x, y, w, h, c, c2) => { P_(g, x, y + w / 2, w, h - w / 2, c); for (let i = 0; i < w / 2; i++) { const d = Math.round(Math.sqrt((w / 2) * (w / 2) - (w / 2 - i) * (w / 2 - i))); P_(g, x + i, y + w / 2 - d, 1, d, c); P_(g, x + w - 1 - i, y + w / 2 - d, 1, d, c); } };
    const gold = '#e0b040', goldL = '#fbe488', goldD = '#8a6420';
    const drape = (x, w, flip) => { // curtain fold side
      vgrad(g, x, 0, w, 74, '#7a1828', '#4a0c1a', 4);
      for (let i = 1; i < w; i += 5) P_(g, x + i, 0, 2, 74, 'rgba(255,120,120,.22)');
      for (let i = 4; i < w; i += 5) P_(g, x + i, 0, 1, 74, 'rgba(0,0,0,.3)');
      P_(g, flip ? x : x + w - 2, 0, 2, 74, goldD);
    };
    // ---------- background by stage ----------
    if (st === 0) {
      vgrad(g, 0, 0, 256, 70, '#2a2630', '#4a4450', 5);
      // stone blocks
      for (let y = 0; y < 70; y += 10) for (let x = (y / 10 % 2) * 12; x < 256; x += 24) { P_(g, x, y, 24, 1, 'rgba(0,0,0,.22)'); P_(g, x, y, 1, 10, 'rgba(0,0,0,.18)'); }
      // arched window left, right
      [[18, 14], [214, 14]].forEach(([x, y], i) => { arch(x - 1, y - 1, 22, 40, '#171021', 0); arch(x, y, 20, 38, i ? '#4a5a8a' : '#5a6a9a', 0); P_(g, x + 9, y + 10, 2, 28, '#171021'); P_(g, x, y + 24, 20, 2, '#171021'); P_(g, x + 2, y + 14, 5, 6, '#7a8ab8'); });
      // pillar
      [[44], [204]].forEach(([x]) => { P_(g, x, 0, 8, 70, '#585260'); P_(g, x, 0, 2, 70, '#78727e'); P_(g, x + 6, 0, 2, 70, '#3a3640'); P_(g, x - 2, 64, 12, 6, '#4a4450'); });
      // organ pipes far right
      for (let i = 0; i < 5; i++) { const h = 22 + (i % 3) * 5; P_(g, 226 + i * 5, 62 - h, 4, h, i % 2 ? '#a08a50' : '#c0a860'); P_(g, 226 + i * 5, 62 - h, 1, h, '#e8d890'); }
      P_(g, 224, 62, 28, 8, '#4a3020');
      // pew left
      P_(g, 0, 56, 40, 4, '#4a2e1c'); P_(g, 0, 60, 40, 10, '#3a2214');
      // floor
      vgrad(g, 0, 70, 256, 42, '#403a44', '#1e1a24', 4);
      for (let x = 0; x < 256; x += 32) P_(g, x, 70, 1, 42, 'rgba(0,0,0,.25)');
      P_(g, 0, 70, 256, 1, '#5a5460');
      candle(32, 56, 6); P_(g, 30, 62, 6, 8, '#4a3a2a');
    } else if (st === 1) {
      // manor hall: wood panel wall
      vgrad(g, 0, 0, 256, 56, '#5a3a28', '#7a5438', 5);
      for (let x = 0; x < 256; x += 16) { P_(g, x, 0, 1, 56, 'rgba(0,0,0,.2)'); }
      P_(g, 0, 44, 256, 2, '#3a2216'); P_(g, 0, 46, 256, 24, '#6a4630'); for (let x = 4; x < 256; x += 32) { P_(g, x, 49, 24, 17, '#5a3a26'); P_(g, x, 49, 24, 1, '#7a5640'); }
      P_(g, 0, 68, 256, 2, '#3a2216');
      // framed portraits
      [[22, 10, 18, 24], [216, 10, 18, 24]].forEach(([x, y, w, h], i) => { PO(g, x, y, w, h, gold); P_(g, x + 2, y + 2, w - 4, h - 4, i ? '#3a4a5a' : '#5a3a3a'); P_(g, x + 6, y + 6, 6, 7, '#d8b090'); P_(g, x + 4, y + 13, 10, 7, i ? '#2a2a4a' : '#7a2a3a'); });
      // swag top & side drapes
      drape(0, 14, 0); drape(242, 14, 1);
      for (let x = 14; x < 242; x += 20) { P_(g, x, 0, 20, 6 + ((x / 20) % 2) * 2, '#7a1828'); P_(g, x, 0, 20, 1, goldD); }
      // fireplace-ish candelabra stands
      [[50], [206]].forEach(([x]) => { P_(g, x, 54, 3, 16, goldD); P_(g, x - 3, 68, 9, 2, gold); P_(g, x - 5, 52, 13, 2, gold); candle(x - 5, 46, 6); candle(x, 44, 8); candle(x + 6, 46, 6); });
      // floor wood
      vgrad(g, 0, 70, 256, 42, '#6a4a30', '#2e1e14', 4);
      for (let x = 0; x < 256; x += 14) P_(g, x, 70, 1, 42, 'rgba(0,0,0,.22)');
      P_(g, 0, 70, 256, 1, '#8a6a48');
      // small chandelier
      P_(g, 127, 0, 1, 6, goldD); P_(g, 118, 6, 20, 2, gold); [119, 126, 135].forEach(x => { P_(g, x, 3, 1, 3, gold); fl(x, 4, 0); });
    } else if (st === 2) {
      // ballroom: pale wall, marble pillars, mirrors, chandeliers
      vgrad(g, 0, 0, 256, 70, '#d8cdb4', '#a89c84', 5);
      P_(g, 0, 0, 256, 8, '#e8dcc0'); P_(g, 0, 8, 256, 2, gold); P_(g, 0, 10, 256, 1, goldD);
      // mirrors with gold frame
      [[16, 14], [208, 14]].forEach(([x, y]) => { PO(g, x, y, 30, 44, gold); vgrad(g, x + 2, y + 2, 26, 40, '#8aa0b8', '#587088', 4); P_(g, x + 5, y + 6, 2, 14, 'rgba(255,255,255,.4)'); P_(g, x + 9, y + 10, 2, 8, 'rgba(255,255,255,.3)'); });
      // marble pillars
      [[56], [192]].forEach(([x]) => { P_(g, x, 10, 8, 60, '#e8e4e0'); P_(g, x, 10, 2, 60, '#fffefc'); P_(g, x + 6, 10, 2, 60, '#a8a4a8'); for (let j = 0; j < 7; j++) P_(g, x + 2 + (j * 3) % 4, 16 + j * 8, 3, 1, '#b8b4bc'); P_(g, x - 2, 8, 12, 4, gold); P_(g, x - 2, 66, 12, 4, gold); });
      // side drapes
      drape(0, 12, 0); drape(244, 12, 1);
      // chandeliers
      [64, 192].forEach(cx => { P_(g, cx, 0, 1, 12, goldD); P_(g, cx - 10, 12, 21, 2, gold); P_(g, cx - 6, 14, 13, 3, goldD); [-10, -4, 3, 9].forEach(o => { P_(g, cx + o, 9, 2, 3, goldL); fl(cx + o, 8, 0); }); glow(g, cx, 12, 22 + mood * 4, 'rgba(255,220,140,A)', 0.3); });
      // floor marble checker
      for (let y = 70; y < 112; y += 7) for (let x = 0; x < 256; x += 14) { const c = (((x / 14) | 0) + ((y - 70) / 7 | 0)) % 2; P_(g, x, y, 14, 7, c ? '#9a9098' : '#6e6670'); }
      P_(g, 0, 70, 256, 1, '#c8c0c8'); P_(g, 0, 70, 256, 42, 'rgba(10,8,20,.2)');
    } else if (st === 3) {
      // palace ballroom (richer, between)
      vgrad(g, 0, 0, 256, 70, '#e8dcb8', '#c0aa78', 5);
      P_(g, 0, 0, 256, 12, goldD); P_(g, 0, 2, 256, 8, gold); for (let x = 2; x < 256; x += 8) P_(g, x, 4, 4, 4, goldL);
      [[14, 16], [212, 16]].forEach(([x, y]) => { PO(g, x, y, 30, 46, gold); vgrad(g, x + 3, y + 3, 24, 40, '#a8c0d8', '#6a88a8', 4); P_(g, x + 6, y + 6, 2, 16, 'rgba(255,255,255,.5)'); });
      [[52], [196]].forEach(([x]) => { P_(g, x, 12, 8, 58, '#f0ece8'); P_(g, x, 12, 2, 58, '#fff'); P_(g, x + 6, 12, 2, 58, '#aaa6ae'); P_(g, x - 2, 10, 12, 4, gold); P_(g, x - 2, 66, 12, 4, gold); P_(g, x + 3, 14, 2, 52, gold); });
      drape(0, 14, 0); drape(242, 14, 1);
      [48, 128, 208].forEach(cx => { P_(g, cx, 12, 1, 4, goldD); P_(g, cx - 12, 16, 25, 2, gold); P_(g, cx - 7, 18, 15, 3, goldD); [-12, -6, 0, 6, 12].forEach(o => { P_(g, cx + o, 13, 2, 3, goldL); fl(cx + o, 12, 0); }); glow(g, cx, 18, 24 + mood * 4, 'rgba(255,220,140,A)', 0.3); });
      for (let y = 70; y < 112; y += 7) for (let x = 0; x < 256; x += 14) { const c = (((x / 14) | 0) + ((y - 70) / 7 | 0)) % 2; P_(g, x, y, 14, 7, c ? '#a8a0a8' : '#6a6068'); }
      P_(g, 0, 70, 256, 1, gold); P_(g, 0, 70, 256, 42, 'rgba(10,8,20,.2)');
      // red carpet center
      P_(g, 70, 74, 116, 38, 'rgba(140,20,40,.55)'); P_(g, 70, 74, 116, 1, goldD);
    } else {
      // st 4: royal great hall: painted ceiling, gold everywhere, grand curtain
      vgrad(g, 0, 0, 256, 70, '#f0e4c0', '#c8a868', 5);
      // ceiling painting: sky with clouds
      vgrad(g, 20, 2, 216, 16, '#6a9ad0', '#f0c8a0', 5);
      P_(g, 18, 0, 220, 2, gold); P_(g, 18, 18, 220, 3, gold); P_(g, 18, 21, 220, 1, goldD);
      [[40, 8, 18], [90, 11, 14], [150, 7, 20], [200, 10, 16]].forEach(([x, y, w], i) => { P_(g, x, y, w, 4, '#fff4e8'); P_(g, x + 2, y - 2, w - 6, 3, '#fff'); P_(g, x + 4, y + 4, w - 6, 2, '#e8c8b0'); });
      P_(g, 120, 6, 3, 3, '#f8d0a8'); P_(g, 118, 9, 7, 4, '#e8e8f8'); P_(g, 160, 12, 3, 3, '#f8d0a8'); P_(g, 158, 15, 6, 2, '#c84860');
      // gilded wall top frieze
      P_(g, 0, 22, 256, 3, goldD); for (let x = 1; x < 256; x += 6) P_(g, x, 23, 3, 2, goldL);
      // pilasters + mirrors
      [[10], [40], [206], [236]].forEach(([x]) => { P_(g, x, 25, 10, 45, '#f4f0ea'); P_(g, x, 25, 2, 45, '#fff'); P_(g, x + 8, 25, 2, 45, '#aaa6ae'); P_(g, x + 4, 27, 2, 41, gold); P_(g, x - 1, 24, 12, 3, gold); });
      [[24, 30], [220, 30]].forEach(([x]) => { P_(g, x - 5, 30, 3, 38, 'rgba(0,0,0,0)'); });
      // grand red curtain with gold tassels, swept to the sides
      g.fillStyle = '#7a1020';
      [[0, 1], [1, 0]].forEach(([s]) => {
        const x0 = s ? 226 : 0, w0 = 30;
        vgrad(g, x0, 22, w0, 52, '#8a1426', '#4a0a18', 4);
        for (let i = 0; i < w0; i += 5) P_(g, x0 + i, 22, 2, 52, 'rgba(255,130,130,.2)');
        for (let i = 3; i < w0; i += 5) P_(g, x0 + i, 22, 1, 52, 'rgba(0,0,0,.3)');
      });
      // swept diagonal sides
      for (let j = 0; j < 20; j++) { P_(g, 30 + j, 22 + j, 1, 1, '#8a1426'); P_(g, 225 - j, 22 + j, 1, 1, '#8a1426'); }
      // valance
      P_(g, 0, 22, 256, 2, gold);
      for (let x = 0; x < 256; x += 16) { P_(g, x, 24, 16, 5 + (((x / 16) | 0) % 2) * 2, '#9a1a30'); P_(g, x, 24, 16, 1, goldL); P_(g, x + 6, 29, 3, 4, gold); }
      // chandeliers x3 hung from ceiling painting
      [70, 128, 186].forEach(cx => { P_(g, cx, 21, 1, 5, goldD); P_(g, cx - 12, 26, 25, 2, gold); P_(g, cx - 8, 28, 17, 3, goldD); for (let o = -12; o <= 12; o += 6) { P_(g, cx + o, 23, 2, 3, goldL); fl(cx + o, 22, 0); } for (let o = -10; o <= 10; o += 5) P_(g, cx + o, 31 + (Math.abs(o) % 2), 1, 2, (fr + o) % 4 ? '#e8f4ff' : '#ffffff'); glow(g, cx, 26, 22 + mood * 3, 'rgba(255,225,150,A)', 0.16); });
      // floor: marble checker + red carpet with gold border
      for (let y = 70; y < 112; y += 7) for (let x = 0; x < 256; x += 14) { const c = (((x / 14) | 0) + ((y - 70) / 7 | 0)) % 2; P_(g, x, y, 14, 7, c ? '#b8b0b8' : '#706870'); }
      P_(g, 0, 70, 256, 1, gold); P_(g, 0, 70, 256, 42, 'rgba(10,8,20,.2)');
      P_(g, 56, 72, 144, 40, '#7a1424'); P_(g, 56, 72, 144, 1, gold); P_(g, 56, 72, 1, 40, gold); P_(g, 199, 72, 1, 40, gold);
      // throne-like tall candelabra (outer)
      [24, 232].forEach(x => { P_(g, x, 52, 3, 18, gold); P_(g, x - 3, 68, 9, 2, goldD); P_(g, x - 5, 50, 13, 2, gold); candle(x - 5, 44, 6); candle(x, 42, 8); candle(x + 6, 44, 6); });
    }
    // calm center: dim any detail slightly behind performers (very light veil)
    if (st >= 2) { g.fillStyle = 'rgba(40,30,40,.10)'; g.fillRect(64, 26, 128, 46); }
    // extra candles and sparkles for lively mood
    if (mood === 2) {
      const xs = st === 0 ? [96, 150] : [76, 180];
      xs.forEach((x, i) => { if (st <= 1) { P_(g, x, 70, 2, 3, '#f4ecd8'); fl(x, 70, i); glow(g, x, 68, 7, 'rgba(255,200,100,A)', 0.2); } });
      if (st >= 3) for (let i = 0; i < 8; i++) { const x = (i * 37 + fr * 3) % 256, y = 30 + (i * 11) % 36; if (x < 56 || x > 200 || y < 28) P_(g, x, y, 1, 1, (fr + i) % 2 ? '#fff8c0' : '#ffe080'); }
    }
    if (mood === 0) { g.fillStyle = 'rgba(10,8,30,.38)'; g.fillRect(0, 0, 256, 112); }
  }
};
