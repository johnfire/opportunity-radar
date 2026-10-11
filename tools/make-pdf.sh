#!/usr/bin/env bash
# Render open-challenges.md to a PDF with "Seite X von Y" on every page.
# Needs pandoc and chromium. Usage: tools/make-pdf.sh [input.md] [output.pdf]
set -euo pipefail
cd "$(dirname "$0")/.."
in="${1:-open-challenges.md}"
out="${2:-${in%.md}.pdf}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/style.css" <<'CSS'
@page {
  size: A4;
  margin: 18mm 15mm 20mm 15mm;
  @bottom-center { content: "Seite " counter(page) " von " counter(pages); font: 9pt sans-serif; color: #555; }
  @bottom-right  { content: "Erstellt __DATE__"; font: 8pt sans-serif; color: #888; }
}
body { font: 10pt/1.38 "DejaVu Sans", sans-serif; color: #111; }
h1 { font-size: 17pt; margin: 14pt 0 6pt; break-after: avoid; }
h2 { font-size: 13pt; margin: 12pt 0 4pt; break-after: avoid; }
h3 { font-size: 11pt; break-after: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 6pt 0; }
th, td { border: 1px solid #bbb; padding: 2pt 4pt; vertical-align: top; }
th { background: #eee; }
tr { break-inside: avoid; }
code { font-size: 9pt; }
hr { border: 0; border-top: 1px solid #ccc; margin: 10pt 0; }
li { margin: 2pt 0; }
a { color: #0645ad; text-decoration: none; word-break: break-all; }
CSS

sed "s/__DATE__/$(date +%d.%m.%Y)/" -i "$tmp/style.css"
pandoc "$in" -f gfm -t html5 -s --metadata pagetitle="Open Challenges" --metadata lang=de \
  -c "$tmp/style.css" --embed-resources -o "$tmp/doc.html" 2>/dev/null \
  || pandoc "$in" -f gfm -t html5 -s --metadata pagetitle="Open Challenges" --metadata lang=de \
  --css "$tmp/style.css" --self-contained -o "$tmp/doc.html"

chromium --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf="$out" "file://$tmp/doc.html" >/dev/null 2>&1
echo "wrote $out"
