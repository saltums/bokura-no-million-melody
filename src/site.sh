#!/bin/bash
# build local test site with charset(index.html + data.json + bank.json。d/ は既存)
cd /home/claude && python3 assemble.py >/dev/null && node /tmp/chk.js >/dev/null
python3 - <<'PY'
s=open('/home/claude/proto_music5.html',encoding='utf-8').read()
open('/tmp/site/index.html','w',encoding='utf-8').write('<!doctype html>\n<html lang="ja"><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'+s)
PY
cp /home/claude/data.json /home/claude/bank.json /tmp/site/
