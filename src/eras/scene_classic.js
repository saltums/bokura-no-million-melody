SCENES[23] = {
  caps: {
    0: ['薄暗い客間の隅で、ひっそり演奏している', '人の少ないサロンで、静かに演奏している', '空席の目立つ演奏会場で、演奏している', '客のまばらな音楽堂で、小さく演奏している', '静まりかえった大劇場で、息をひそめて演奏している'],
    1: ['小さなサロンで、蝋燭の灯りの下に演奏している','客間の壁画の前で、仲間と演奏している','燭台の灯る伯爵家のサロンで、演奏している','肖像画の並ぶ客間で、客人に演奏している','貴族のサロンで、堂々と演奏している'],
    2: ['サロンに集まった人々の前で演奏している','サロンに蝋燭が増え、にぎやかに演奏している','演奏会場で、シャンデリアの下に演奏している','満席の音楽堂で、拍手の中に演奏している','大きな劇場で、喝采を浴びて演奏している']
  },
  cl: [['#2a3a5a', '#5a7ab0', '#18243c'], ['#6a2a3a', '#a85868', '#401822'], ['#3a5a48', '#68a088', '#223a2c'], ['#e8dcc8', '#ffffff', '#a89c88'], ['#4a3a5a', '#8070a0', '#2a2038'], ['#1e1e2a', '#4a4a60', '#0e0e16']],
  fn(g, st, mood, fr) {
    const gold = '#e0b040', goldL = '#fbe488', goldD = '#8a6420';
    const fl = (x, y) => { const k = (fr + x) % 3; P_(g, x, y - 2 - (k === 0 ? 1 : 0), 1, 2, '#fff0a0'); P_(g, x, y - 1, 1, 1, '#ffb030'); };
    const candle = (x, y, h) => { P_(g, x, y, 2, h, '#f4ecd8'); fl(x, y); glow(g, x, y - 2, 9 + mood * 2, 'rgba(255,200,100,A)', 0.22 + mood * 0.06); };
    const candelabra = x => { P_(g, x, 54, 3, 16, goldD); P_(g, x - 3, 68, 9, 2, gold); P_(g, x - 5, 52, 13, 2, gold); candle(x - 5, 46, 6); candle(x, 44, 8); candle(x + 6, 46, 6); };
    const drape = (x, w, flip, c1, c2) => {
      vgrad(g, x, 0, w, 74, c1, c2, 4);
      for (let i = 1; i < w; i += 5) P_(g, x + i, 0, 2, 74, 'rgba(255,255,255,.14)');
      for (let i = 4; i < w; i += 5) P_(g, x + i, 0, 1, 74, 'rgba(0,0,0,.3)');
      P_(g, flip ? x : x + w - 2, 0, 2, 74, goldD);
    };
    const window_ = (x, y, w, h) => { PO(g, x - 1, y - 1, w + 2, h + 2, '#e8e0d0'); vgrad(g, x, y, w, h, '#1c2848', '#46609a', 4); P_(g, x + (w >> 1), y, 1, h, '#e8e0d0'); P_(g, x, y + (h >> 1), w, 1, '#e8e0d0'); P_(g, x + 3, y + 3, 1, 1, '#fff'); P_(g, x + w - 5, y + 6, 1, 1, '#fff'); };
    const grand = (x, y) => { // grand piano, side view
      P_(g, x, y, 56, 6, '#14101a'); P_(g, x + 2, y - 3, 40, 3, '#14101a'); P_(g, x + 4, y - 1, 36, 1, '#3a3446');
      P_(g, x + 44, y - 3, 10, 3, '#1e1824'); P_(g, x, y + 6, 56, 2, '#e8e4dc');
      for (let i = 0; i < 56; i += 3) P_(g, x + i, y + 6, 1, 2, '#14101a');
      P_(g, x + 3, y + 8, 3, 14, '#14101a'); P_(g, x + 50, y + 8, 3, 14, '#14101a'); P_(g, x + 26, y + 8, 3, 10, '#14101a');
    };
    const frame = (x, y, w, h, i) => { PO(g, x, y, w, h, gold); P_(g, x + 2, y + 2, w - 4, h - 4, i ? '#34485a' : '#523a3a'); P_(g, x + (w >> 1) - 3, y + 5, 6, 7, '#d8b090'); P_(g, x + (w >> 1) - 5, y + 12, 10, h - 16, i ? '#2a2a4a' : '#7a2a3a'); };
    // ---------- background by stage ----------
    if (st === 0) {
      // small parlour: plain plaster wall, window, single candle
      vgrad(g, 0, 0, 256, 70, '#4a4252', '#6a6070', 5);
      for (let x = 0; x < 256; x += 12) P_(g, x, 0, 1, 70, 'rgba(0,0,0,.14)');
      window_(26, 12, 28, 40); window_(204, 12, 28, 40);
      P_(g, 0, 56, 256, 3, '#3a3040'); P_(g, 0, 59, 256, 11, '#564c5e');
      // small spinet/upright shape left
      P_(g, 70, 38, 40, 28, '#3a2418'); P_(g, 72, 40, 36, 4, '#5a3a28'); P_(g, 70, 62, 40, 6, '#e8e4dc'); for (let i = 0; i < 40; i += 3) P_(g, 70 + i, 62, 1, 6, '#2a1c14');
      vgrad(g, 0, 70, 256, 42, '#4a3a30', '#1e1612', 4);
      for (let x = 0; x < 256; x += 18) P_(g, x, 70, 1, 42, 'rgba(0,0,0,.25)');
      P_(g, 0, 70, 256, 1, '#6a5848');
      candle(150, 62, 6); P_(g, 146, 68, 10, 2, goldD);
    } else if (st === 1) {
      // salon: striped wallpaper, portraits, candelabra, curtains
      vgrad(g, 0, 0, 256, 56, '#3a5a68', '#527a88', 5);
      for (let x = 0; x < 256; x += 10) P_(g, x, 0, 4, 56, 'rgba(255,255,255,.07)');
      P_(g, 0, 44, 256, 2, '#d8cdb4'); P_(g, 0, 46, 256, 24, '#e0d4bc'); for (let x = 4; x < 256; x += 32) { P_(g, x, 49, 24, 17, '#cabc9e'); P_(g, x, 49, 24, 1, '#f0e8d4'); }
      P_(g, 0, 68, 256, 2, '#8a7a5a');
      frame(22, 8, 18, 26, 0); frame(216, 8, 18, 26, 1); frame(110, 6, 34, 24, 0);
      drape(0, 14, 0, '#7a2a3a', '#4a1424'); drape(242, 14, 1, '#7a2a3a', '#4a1424');
      for (let x = 14; x < 242; x += 20) { P_(g, x, 0, 20, 5 + ((x / 20) % 2) * 2, '#7a2a3a'); P_(g, x, 0, 20, 1, goldD); }
      candelabra(50); candelabra(206);
      vgrad(g, 0, 70, 256, 42, '#7a5a3a', '#2e1e14', 4);
      for (let x = 0; x < 256; x += 14) P_(g, x, 70, 1, 42, 'rgba(0,0,0,.22)');
      P_(g, 0, 70, 256, 1, '#9a7a56');
      P_(g, 127, 0, 1, 6, goldD); P_(g, 118, 6, 20, 2, gold); [119, 126, 135].forEach(x => { P_(g, x, 3, 1, 3, gold); fl(x, 4); });
    } else if (st === 2) {
      // concert salon: arched windows, chandeliers, grand piano silhouette
      vgrad(g, 0, 0, 256, 70, '#e0d6c0', '#b0a488', 5);
      P_(g, 0, 0, 256, 8, '#f0e6cc'); P_(g, 0, 8, 256, 2, gold); P_(g, 0, 10, 256, 1, goldD);
      [[16, 14], [208, 14]].forEach(([x, y]) => { PO(g, x, y, 30, 46, gold); vgrad(g, x + 2, y + 2, 26, 42, '#1c2848', '#46609a', 4); P_(g, x + 14, y + 2, 2, 42, gold); P_(g, x + 7, y + 8, 1, 1, '#fff'); });
      [[56], [192]].forEach(([x]) => { P_(g, x, 10, 8, 60, '#eae6e0'); P_(g, x, 10, 2, 60, '#fffefc'); P_(g, x + 6, 10, 2, 60, '#a8a4a8'); P_(g, x - 2, 8, 12, 4, gold); P_(g, x - 2, 66, 12, 4, gold); });
      drape(0, 12, 0, '#2a4a7a', '#162a4a'); drape(244, 12, 1, '#2a4a7a', '#162a4a');
      [64, 192].forEach(cx => { P_(g, cx, 0, 1, 12, goldD); P_(g, cx - 10, 12, 21, 2, gold); P_(g, cx - 6, 14, 13, 3, goldD); [-10, -4, 3, 9].forEach(o => { P_(g, cx + o, 9, 2, 3, goldL); fl(cx + o, 8); }); glow(g, cx, 12, 22 + mood * 4, 'rgba(255,220,140,A)', 0.3); });
      for (let y = 70; y < 112; y += 7) for (let x = 0; x < 256; x += 14) { const c = (((x / 14) | 0) + ((y - 70) / 7 | 0)) % 2; P_(g, x, y, 14, 7, c ? '#a09890' : '#6e665e'); }
      P_(g, 0, 70, 256, 1, '#c8c0b0'); P_(g, 0, 70, 256, 42, 'rgba(10,8,20,.2)');
      grand(190, 48);
    } else if (st === 3) {
      // music hall: tiered boxes, gilded
      vgrad(g, 0, 0, 256, 70, '#5a2a34', '#7a3a46', 5);
      P_(g, 0, 0, 256, 6, goldD); P_(g, 0, 2, 256, 3, gold);
      for (let t = 0; t < 2; t++) { const y = 10 + t * 24; P_(g, 0, y, 256, 3, gold); P_(g, 0, y + 3, 256, 1, goldD); for (let x = 6; x < 256; x += 22) { P_(g, x, y + 5, 16, 14, '#2a0e16'); P_(g, x + 2, y + 7, 4, 4, '#d8b090'); P_(g, x + 9, y + 8, 4, 4, '#c89a80'); P_(g, x, y + 19, 16, 2, gold); } }
      P_(g, 0, 58, 256, 3, gold); P_(g, 0, 61, 256, 9, '#3a1018');
      [[48, 64], [128, 52], [208, 64]].forEach(([cx, cy]) => { });
      [50, 128, 206].forEach(cx => { P_(g, cx, 0, 1, 8, goldD); P_(g, cx - 11, 8, 23, 2, gold); P_(g, cx - 7, 10, 15, 3, goldD); [-11, -5, 1, 7, 11].forEach(o => { P_(g, cx + o, 5, 2, 3, goldL); fl(cx + o, 4); }); glow(g, cx, 10, 24 + mood * 4, 'rgba(255,220,140,A)', 0.28); });
      vgrad(g, 0, 70, 256, 42, '#5a3a24', '#2a180e', 4);
      for (let x = 0; x < 256; x += 12) P_(g, x, 70, 1, 42, 'rgba(0,0,0,.25)');
      P_(g, 0, 70, 256, 1, gold);
      P_(g, 70, 72, 116, 40, 'rgba(120,20,40,.5)'); P_(g, 70, 72, 116, 1, goldD);
    } else {
      // grand opera-style concert hall: proscenium, painted ceiling, organ pipes
      vgrad(g, 0, 0, 256, 70, '#f0e4c0', '#c8a868', 5);
      vgrad(g, 20, 2, 216, 16, '#4a6ab0', '#e8c8a0', 5);
      P_(g, 18, 0, 220, 2, gold); P_(g, 18, 18, 220, 3, gold); P_(g, 18, 21, 220, 1, goldD);
      [[40, 8, 18], [96, 11, 14], [150, 7, 20], [200, 10, 16]].forEach(([x, y, w]) => { P_(g, x, y, w, 4, '#fff4e8'); P_(g, x + 2, y - 2, w - 6, 3, '#fff'); P_(g, x + 4, y + 4, w - 6, 2, '#e8c8b0'); });
      P_(g, 0, 22, 256, 3, goldD); for (let x = 1; x < 256; x += 6) P_(g, x, 23, 3, 2, goldL);
      // organ pipes behind the stage
      for (let i = 0; i < 17; i++) { const h = 18 + Math.abs(8 - i) * -1 + 8 + (i % 3) * 2; P_(g, 84 + i * 5, 68 - h - 14, 4, h + 14, i % 2 ? '#b09850' : '#d0b868'); P_(g, 84 + i * 5, 68 - h - 14, 1, h + 14, '#f0e0a0'); P_(g, 85 + i * 5, 68 - h - 14, 2, 2, '#3a2a10'); }
      P_(g, 80, 62, 92, 8, '#4a3020');
      // pilasters
      [[10], [40], [206], [236]].forEach(([x]) => { P_(g, x, 25, 10, 45, '#f4f0ea'); P_(g, x, 25, 2, 45, '#fff'); P_(g, x + 8, 25, 2, 45, '#aaa6ae'); P_(g, x + 4, 27, 2, 41, gold); P_(g, x - 1, 24, 12, 3, gold); });
      // red curtains at sides
      [[0, 8], [248, 8]].forEach(([x, w]) => { vgrad(g, x, 22, w, 52, '#8a1426', '#4a0a18', 4); P_(g, x, 22, w, 1, gold); });
      for (let x = 0; x < 256; x += 16) { P_(g, x, 22, 16, 4 + (((x / 16) | 0) % 2) * 2, '#9a1a30'); P_(g, x, 22, 16, 1, goldL); }
      [70, 128, 186].forEach(cx => { P_(g, cx, 21, 1, 5, goldD); P_(g, cx - 12, 26, 25, 2, gold); P_(g, cx - 8, 28, 17, 3, goldD); for (let o = -12; o <= 12; o += 6) { P_(g, cx + o, 23, 2, 3, goldL); fl(cx + o, 22); } for (let o = -10; o <= 10; o += 5) P_(g, cx + o, 31 + (Math.abs(o) % 2), 1, 2, (fr + o) % 4 ? '#e8f4ff' : '#ffffff'); glow(g, cx, 26, 22 + mood * 3, 'rgba(255,225,150,A)', 0.16); });
      for (let y = 70; y < 112; y += 7) for (let x = 0; x < 256; x += 14) { const c = (((x / 14) | 0) + ((y - 70) / 7 | 0)) % 2; P_(g, x, y, 14, 7, c ? '#b8b0b8' : '#706870'); }
      P_(g, 0, 70, 256, 1, gold); P_(g, 0, 70, 256, 42, 'rgba(10,8,20,.2)');
      P_(g, 56, 72, 144, 40, '#7a1424'); P_(g, 56, 72, 144, 1, gold); P_(g, 56, 72, 1, 40, gold); P_(g, 199, 72, 1, 40, gold);
      candelabra(24); candelabra(232);
    }
    if (st >= 2) { g.fillStyle = 'rgba(40,30,40,.10)'; g.fillRect(64, 26, 128, 46); }
    if (mood === 2) {
      if (st <= 1) [96, 150].forEach((x, i) => { P_(g, x, 70, 2, 3, '#f4ecd8'); fl(x, 70); glow(g, x, 68, 7, 'rgba(255,200,100,A)', 0.2); });
      if (st >= 3) for (let i = 0; i < 8; i++) { const x = (i * 37 + fr * 3) % 256, y = 30 + (i * 11) % 36; if (x < 56 || x > 200 || y < 28) P_(g, x, y, 1, 1, (fr + i) % 2 ? '#fff8c0' : '#ffe080'); }
    }
    if (mood === 0) { g.fillStyle = 'rgba(10,8,30,.38)'; g.fillRect(0, 0, 256, 112); }
  }
};
