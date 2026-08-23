#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"

FORT=".fortschritt-pruefer"
SHA256() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 | awk '{print $1}'; else sha256sum | awk '{print $1}'; fi; }

norm() {
  local s="${1^^}"
  s="${s//Ä/AE}"; s="${s//Ö/OE}"; s="${s//Ü/UE}"; s="${s//ß/SS}"
  s="${s//É/E}"; s="${s//È/E}"; s="${s//Ê/E}"
  local out="" ch i
  for (( i=0; i<${#s}; i++ )); do
    ch="${s:i:1}"
    [[ "$ch" =~ [A-Z0-9] ]] && out="$out$ch"
  done
  printf '%s' "$out"
}

ask() {
  local nr="$1" frage="$2" korrekt="$3" punkte="$4" antwort h ok ALT
  printf '\n== PRUEFPUNKT %s ==\n%s\n> ' "$nr" "$frage"
  read -r antwort
  h="$(printf '%s' "$(norm "$antwort")" | SHA256)"
  ok=0
  for ALT in ${korrekt//,/ }; do
    [ "$h" = "$ALT" ] && ok=1
  done
  if [ "$ok" = "1" ]; then
    echo "  >> RICHTIG. +$punkte Punkte"
    grep -q "^$nr " "$FORT" 2>/dev/null || printf '%s %s\n' "$nr" "$punkte" >> "$FORT"
  else
    echo "  >> Leider nicht. (Aktenzeichen bleibt offen.)"
  fi
}

ART='
 ____________________
|  T E R M I N A L   |
|  C I T Y   I I I   |
|____________________|
   \^~~^/  TCPD
'

case "${1:-}" in
  --status)
    echo "== Fortschritt =="; cat "$FORT" 2>/dev/null || echo "(noch keine Prüfpunkte)"
    exit 0 ;;
  --reset)
    rm -f "$FORT"; echo "Fortschritt zurückgesetzt."; exit 0 ;;
esac

echo "$ART"
echo "PRUEFER DES TCPD — AKTE 48/III"
echo "(Antworten: normale Schreibweise, Groß-/Kleinschreibung egal)"
echo

[ "${2:-}" = "--force" ] && rm -f "$FORT"

ask 1 "Wie lautete der vollständige Name des Opfers?" "7c3b9d584cf7a0f721419764f66151300f8a0be42959bf25fdbeeb61893c1618,7c3b9d584cf7a0f721419764f66151300f8a0be42959bf25fdbeeb61893c1618" 20
ask 2 "Wer hat den Tee gemischt? (vollständiger Name des Innendienst-Täters)" "8411c139ecb3e617b470c82a6281181ee834b7c2c0a0e8f1f94a2f6a102f9567" 20
ask 3 "Unter welchem Codename lief die Order der Drahtzieherin?" "f8c2c556e154d27fe5df5fd77599abfaad1a6ac572667ceb710351c3caf26982" 20
ask 4 "Wie lautet der vollständige Name der Auftraggeberin?" "613bfcfdcb27f5552db77177413db3deba8136c6c541ea7b586324c5028d4084,c30452fd2aa03fae0fed6d5af6b0c1be232119e7121cea72ca5a6907669ab63e" 20
ask 5 "Wo sollte die Übergabe stattfinden? (Ort)" "a2d7532a243f5452a4e1cf2e0654ee3e459fc7241debd99c1d0974cde498bbfe,198ffbf06f65ed26a4581e6f277f99a9e0dde714171d496580fec211a3833263,7ac1e365a82c22e352557ed9e8ac665dc38afe20121cf29d87651360c3beaaf1,de25e2bdf3c77d6e9cd5b3622d31c1920c97301e37289683058e5cfd4882f2b8" 20

GESAMT=$(awk '{s+=$2} END{print s+0}' "$FORT" 2>/dev/null)
GESAMT=${GESAMT:-0}
echo
echo "== ZWISCHENSTAND: $GESAMT / 100 Punkte =="

if [ "$GESAMT" = "100" ]; then
cat <<'EOF'

      _____
     |A .  |-----.
     | /.\ |c)   |   FALL 48/III GELÖST!
     |(_._)| /\/ |
     |  |  |-----'
     |___V_|
EOF
echo "Bravo, Detective. Reiche deinen Bericht bei loesung ein."
fi
exit 0
