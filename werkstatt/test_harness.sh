#!/usr/bin/env bash
# Test harness for "Die Kommandozeilen-Morde III" (SPOILER-HEAVY — workshop only!)
set -u
cd "$(dirname "$0")/.."

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "  OK   $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

META="werkstatt/meta.json"
[ -f "$META" ] || { echo "meta.json missing"; exit 1; }
jget() { python3 -c "import json,sys;m=json.load(open('$META'));print(eval('m'+sys.argv[1]))" "$1"; }

HASHER="$(command -v md5 || command -v md5sum)"
SHA256() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 | awk '{print $1}'; else sha256sum | awk '{print $1}'; fi; }

echo "=== 1. Loesungskette ==="
CHEFIN="$(jget "['chefin']")"
H=$(printf '%s' "$CHEFIN" | "$HASHER" | awk '{print $NF}')
grep -qi "^$H$" kodiert && ok "md5('$CHEFIN') in kodiert" || bad "md5 nicht in kodiert"

N_ROSTER=$(grep -c "^2026-05-09,ABEND,KUECHE," fall/protokolle/schichtplan.csv)
[ "$N_ROSTER" = "6" ] && ok "Schichtplan ABEND/KUECHE == genau 6 Ausweise" || bad "Roster=$N_ROSTER"

PE="$(jget "['verify']['petrov_entry']")"
PX="$(jget "['verify']['petrov_exit']")"
grep -qF "$PE | EINGANG | KUECHE-LIEFERUNG | 2207" fall/protokolle/zutritts-log.log && ok "Petrov EINGANG 20:31" || bad "Petrov entry fehlt"
grep -qF "$PX | AUSGANG | KUECHE-LIEFERUNG | 2207" fall/protokolle/zutritts-log.log && ok "Petrov AUSGANG 21:33" || bad "Petrov exit fehlt"

EB_EXIT="$(jget "['verify']['elim_b_last_exit']")"
grep -qF "$EB_EXIT | AUSGANG | KUECHE-LIEFERUNG | $(jget "['elim_b']['ausweis']")" fall/protokolle/zutritts-log.log \
  && ! grep -E "^2026-05-09 (19:5[6-9]|2[01]:[0-5][0-9])" fall/protokolle/zutritts-log.log | grep -q "EINGANG.* $(jget "['elim_b']['ausweis']")$" \
  && ok "Elim B verliess die Tuer 19:55 und kam nicht zurueck" || bad "Elim-B-Logik kaputt"

HU="$(jget "['verify']['history_user_elim']")"
HL="$(jget "['verify']['history_logout']")"
grep -qF "# session 2026-05-09 21:02:55 user:$HU" fall/protokolle/apotheke-history.txt && grep -qF "# logout $HL" fall/protokolle/apotheke-history.txt \
  && ok "Apotheken-Session des Elim A im Fenster (Alibi)" || bad "History-Session fehlt"
MAP=$(grep "^$HU," fall/protokolle/terminal-nutzer.csv | cut -d, -f2)
[ "$MAP" = "$(jget "['elim_a']['ausweis']")" ] && ok "terminal-nutzer mapt Session auf Elim-A-Ausweis" || bad "Terminal-Mapping falsch ($MAP)"

WINDOW_IDS=$(grep -E "^2026-05-09 20:(3[0-9]|[45][0-9])" fall/protokolle/zutritts-log.log | grep "KUECHE-LIEFERUNG" | grep EINGANG | awk -F' \\| ' '{print $NF}' | sort -u)
N_WIN=$(echo "$WINDOW_IDS" | wc -l | tr -d ' ')
[ "$N_WIN" = "2" ] && ok "Zutritt-Fenster-EINGANG == genau 2 Kandidaten (2207+2189)" || bad "Window-IDs=$WINDOW_IDS ($N_WIN)"

active_in_window() {
python3 - "$1" <<'PY'
import sys,re
u=sys.argv[1]
txt=open('fall/protokolle/apotheke-history.txt').read()
for m in re.finditer(r'# session (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) user:(\S+)\n(.*?)\n# logout (\d{2}):(\d{2}):(\d{2})', txt, re.S):
    _,sh,sm,ss,user,_,eh,em,es=m.groups()
    if user!=u: continue
    start=int(sh)*3600+int(sm)*60+int(ss); end=int(eh)*3600+int(em)*60+int(es)
    if start<=21*3600+20*60 and end>=21*3600+5*60:
        print("YES"); break
PY
}
REMAIN=""
for id in $WINDOW_IDS; do
  u=$(awk -F, -v id="$id" '$2==id{print $1}' fall/protokolle/terminal-nutzer.csv | head -1)
  [ "$(active_in_window "$u")" = "YES" ] || REMAIN="$REMAIN $id"
done
[ "$(echo $REMAIN | tr -d ' ')" = "2207" ] && ok "Nach Alibi-Elimination bleibt GENAU 2207 (Petrov)" || bad "Remain=[$REMAIN]"

echo "=== 2. Beweisstuecke & Steganographie ==="
TARGET_MD5=$(jget "['verify']['fingerprint_target_md5']")
MATCHED=""
for b in fall/beweisstuecke/brief-*.txt; do
  bh=$("$HASHER" "$b" | awk '{print $NF}')
  if [ "$bh" = "$TARGET_MD5" ]; then MATCHED="$b"; fi
done
[ "$(basename "${MATCHED:-x}")" = "brief-c.txt" ] && ok "Genau brief-c matcht SENDUNG-88-Anhang" || bad "Match=${MATCHED:-keiner}"

ACRO=$(cut -c1 fall/beweisstuecke/brief-c.txt | tr -d '\n')
[ "$ACRO" = "$(jget "['verify']['acrostic']")" ] && ok "Akrostichon == $(jget "['verify']['acrostic']")" || bad "Acrostichon='$ACRO'"

TARLIST=$(tar -tzf fall/beweisstuecke/effekten-petrov.tar.gz)
echo "$TARLIST" | grep -q "inventar.txt" && echo "$TARLIST" | grep -q "beilage-muenznotiz.rot13" && ok "tar-Archiv Mitglieder vollstaendig" || bad "tar-Inhalt: $TARLIST"

TMPX=$(mktemp -d)
tar -xzf fall/beweisstuecke/effekten-petrov.tar.gz -C "$TMPX"
DEC=$(tr 'A-Za-z' 'N-ZA-Mn-za-m' < "$TMPX"/effekten-b14/beilage-muenznotiz.rot13 | SHA256)
WANT_M=$(jget "['verify']['muenz_rot13_sha256']")
[ "$DEC" = "$WANT_M" ] && ok "rot13-Muenznotiz roundtrip" || bad "Muenznotiz falsch ($DEC)"
rm -rf "$TMPX"

echo "=== 3. Verschluesselung ==="
MAIL=$(openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 -in fall/verschluesselt/auftraggeberin.eml.aes -pass pass:"$(jget "['codename_chefin']")" 2>/dev/null)
echo "$MAIL" | grep -q "$(jget "['verify']['mail_contains']")" && ok "AES-Mail entschluesselt mit Codename" || bad "AES-Mail kaputt"

EPI=$(openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 -in fall/verschluesselt/epilog.aes -pass pass:"$(jget "['codename_chefin']")" 2>/dev/null)
echo "$EPI" | grep -qi "Fall 48/III" && ok "Epilog entschluesselt" || bad "Epilog kaputt"

echo "=== 4. Git-Forensik ==="
REPO="fall/repos/hafenkasse-versand"
C_TEAM=$(jget "['git']['C_TEAM']"); C_SENDUNG=$(jget "['git']['C_SENDUNG']"); DANGLING=$(jget "['git']['DANGLING']")
git -C "$REPO" show "$C_TEAM:team/petrov.txt" | grep -q "$(jget "['verify']['taeter_txt_contains']")" && ok "team/petrov.txt wiederherstellbar" || bad "petrov.txt nicht holbar"
git -C "$REPO" show "$C_SENDUNG:kunden/sendung-88.csv" | grep -q "$(jget "['verify']['sendung88_contains']")" && ok "sendung-88.csv wiederherstellbar" || bad "sendung-88 nicht holbar"
FSCK_OUT=$(LC_ALL=C git -C "$REPO" fsck --dangling 2>/dev/null)
echo "$FSCK_OUT" | grep -q "$DANGLING" && ok "dangling commit auffindbar" || bad "dangling fehlt: $FSCK_OUT"
git -C "$REPO" show "$DANGLING:entwurf/weisung.md" | grep -q "$(jget "['verify']['dangling_contains']")" && ok "Weisung enthaelt KIEBITZ" || bad "Weisung-Inhalt falsch"

VOR=$(grep -F "$(jget "['verify']['vorstand_contains']")" fall/firmenregister/hafenbank-vorstand.csv)
[ -n "$VOR" ] && ok "Vorstandsregister enthaelt Anker" || bad "Vorstand-Anker fehlt"

echo "=== 5. Struktur & Mengen ==="
P_ROWS=$(tail -n +9 fall/personen | wc -l | tr -d ' ')
WANT_P=$(jget "['counts']['personen']")
[ "$P_ROWS" = "$WANT_P" ] && ok "personen rows == $WANT_P" || bad "personen rows=$P_ROWS erwartet $WANT_P"

I_CNT=$(ls fall/befragungen | wc -l | tr -d ' ')
WANT_I=$(jget "['counts']['interviews']")
[ "$I_CNT" = "$WANT_I" ] && ok "befragungen == $WANT_I" || bad "befragungen=$I_CNT"

for nr in $(jget "['zeugen']" | tr -d "[]" | tr "," "\n" | tr -d " "); do
  [ -f "fall/befragungen/befragung-$nr" ] && ok "Zeugen-Befragung $nr existiert" || bad "befragung-$nr fehlt"
done

STREET_BAD=0
for f in fall/strassen/*.txt; do
  lc=$(wc -l < "$f" | tr -d ' '); [ "$lc" = "300" ] || STREET_BAD=$((STREET_BAD+1))
done
[ "$STREET_BAD" = "0" ] && ok "alle Strassendateien haben 300 Zeilen" || bad "$STREET_BAD Strassen abweichend"

ADDR_BAD=0
while IFS=$'\t' read -r name gender age address; do
  street=$(echo "$address" | sed -E 's/, Zeile [0-9]+$//'); line=$(echo "$address" | grep -oE '[0-9]+$')
  fname="fall/strassen/${street// /_}.txt"
  if [ -f "$fname" ]; then
    lc=$(wc -l < "$fname" | tr -d ' ')
    [ "$line" -le "$lc" ] || ADDR_BAD=$((ADDR_BAD+1))
  else
    ADDR_BAD=$((ADDR_BAD+1))
  fi
done < <(tail -n +9 fall/personen)
[ "$ADDR_BAD" = "0" ] && ok "alle Adresszeilen innerhalb der Strassendatei" || bad "$ADDR_BAD Adressen out-of-range"

echo "=== 6. Pruefer-Konsistenz ==="
for stage in opfer taeter code chefin ort; do
  HASHES=$(jget "['hashes']['${stage}_sha256']" | tr -d "[]'" | tr ',' '\n' | sed 's/ //g' | grep -v '^$')
  FOUND=0
  for h in $HASHES; do grep -q "$h" pruefer.sh && FOUND=1; done
  [ "$FOUND" = "1" ] && ok "pruefer Stage '$stage' abgedeckt" || bad "pruefer Stage '$stage' fehlt"
done

echo "=== 7. Spoiler-Sweep ==="
SPOIL_OK=1
for pat in "Petrov" "Holthaus" "Regina" "SPHINX" "KIEBITZ" "Fischspeicher"; do
  HITS=$(grep -rl "$pat" anleitung spickzettel.md README.md LICENSE.md loesung hinweis* pruefer.sh kodiert fall/tatort 2>/dev/null | wc -l | tr -d ' ')
  [ "$HITS" != "0" ] && { SPOIL_OK=0; bad "Spoiler '$pat' in Narrativ-Dateien"; }
done
[ "$SPOIL_OK" = "1" ] && ok "keine Loesungen im Klartext-Narrativ"

echo ""
echo "=== SUMMARY: $PASS passed, $FAIL failed ==="
[ "$FAIL" = "0" ]
