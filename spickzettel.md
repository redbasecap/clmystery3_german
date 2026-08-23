SPICKZETTEL — DIE KOMMANDOZEILEN-MORDE III
==========================================

NAVIGIEREN
----------
ls / cd / pwd             Verzeichnisse
less / cat / head / tail  Dateien lesen           tail -n 20 datei
wc -l                     Zeilen zählen
find                      suchen                  find fall -name '*brief*'

SUCHEN MIT GREP
---------------
grep MUSTER datei         Trefferzeilen
grep -i / -n / -c / -r    case-insensitive / Nummern / zählen / rekursiv
grep -A3 -B3              Kontext mitliefern
Beispiel:
  grep ABEND fall/protokolle/schichtplan.csv | grep KUECHE

JOINEN (zwei Dateien verbinden)
-------------------------------
Handarbeit mit grep, oder klassisch:
  join -t, -1 4 -2 1 datei1 datei2
Oder einfach: grep '<AUSWEIS>' fall/protokolle/ausweis-register.csv

SORTIEREN UND SCHNEIDEN
-----------------------
sort / sort -u / uniq     Sortieren / Dubletten
cut -d',' -f2             Spalten schneiden
tr 'a-z' 'A-Z'            Zeichen übersetzen
cut -c1 datei             ERSTEN Buchstaben jeder Zeile (Akrostichon!)

ARCHIVE (tar)
-------------
tar -tzf archiv.tar.gz          Inhalt AUFLISTEN
tar -xzf archiv.tar.gz -C ziel  Entpacken nach 'ziel'

KODIERUNG / VERSCHLÜSSELUNG
---------------------------
openssl base64 -d -in datei     Base64 dekodieren (portabel)
ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
AES (openssl, wird im Fall verwendet):
  openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \
    -in datei.aes -pass pass:PASSWORT
MD5-FINGERPRINTS (macOS/Linux):
  md5 datei ...                bzw.  md5sum datei ...

GIT-FORENSIK (im beschlagnahmten Repo)
--------------------------------------
sh fall/repos/hafenkasse-versand/ermittlung-starten.sh
cd fall/repos/hafenkasse-versand
git log --oneline / --stat / -p
git show SHA:pfad          Datei aus altem Stand holen!
git fsck --lost-found      Verlorene Commits finden
git reflog                 Wohin zeigte HEAD wann?

TIPPS
-----
* Logdateien erklären sich in ihren '#'-Kopfzeilen selbst.
* Zeitfenster filtern: grep '2026-05-09 2[01]:' ...
* Niemals raten: Jede Behauptung braucht Datei+Zeile als Beleg.
