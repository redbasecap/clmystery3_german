#!/usr/bin/env python3
import base64
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME = REPO
FALL_DIR = GAME / "fall"
ASSETS = Path(__file__).resolve().parent / "assets"

rng = random.Random(20260509)

OPFER_NAME = "René Falkenberg"
OPFER_ALT = 49
TAETER_NAME = "Milan Petrov"
TAETER_ALT = 26
AUFTRAGGEBERIN = "Regina Holthaus"
CODENAME_BOSS = "SPHINX"
CODENAME_TAETER = "KIEBITZ"
AUSWEIS_TAETER = "TC-KUECHE-2207"
TERMINAL_USER_TAETER = "kk-kueche-01"
ELIM_A = ("Tom", "Krüger", "2189", "kk-kueche-03")
ELIM_B = ("Georg", "Jost", "2311")
DROP = "alter Fischspeicher Rampe 3"

VORNAME_W = [
    "Anna","Bertha","Clara","Dora","Elisabeth","Franziska","Greta","Hanna","Ines","Johanna",
    "Katharina","Leonie","Martina","Nadja","Ottilie","Petra","Rosa","Sabine","Tanja","Ulrike",
    "Verena","Wanda","Yvonne","Zoe","Amelie","Britta","Cecilia","Dagmar","Emilia","Frieda",
    "Gesine","Henriette","Ida","Josephine","Karoline","Luise","Mathilde","Nicole","Odalys","Pauline",
    "Ronja","Stefanie","Theresa","Uta","Valentina","Wilhelmine","Xenia","Yasmin","Zaida","Almut",
    "Regina","Serpil","Aylin","Fatima","Giulia","Noor","Selma","Leyla","Aisha","Marlene",
]
VORNAME_M = [
    "Aaron","Bruno","Christian","Dieter","Emil","Falk","Gustav","Heinrich","Ignatz","Jonas",
    "Klaus","Ludwig","Martin","Norbert","Otto","Paul","Reinhold","Stefan","Theodor","Uwe",
    "Vincent","Wolfgang","Xaver","Yusuf","Zacharias","Anton","Boris","Cornelius","Detlef","Emanuel",
    "Florian","Georg","Hendrik","Ivo","Jakob","Konrad","Lorenz","Matthias","Nikolaus","Oskar",
    "Pascal","Quirin","Rasmus","Sebastian","Tobias","Ulf","Veit","Werner","Zeno","Anselm",
    "René","Milan","Darius","Tarik","Joost","Kenan","Ruben","Ilja","Neo","Tom",
]
NACHNAMEN = [
    "Ackermann","Baumann","Brandt","Czerwinski","Dahlmann","Ehlers","Falkenberg","Gerber","Grünwald","Hartmann",
    "Ivanov","Jensen","Kowalczyk","Lindqvist","Meixner","Neumann","Ostermann","Petrov","Quandt","Richter",
    "Salomon","Schneider","Sommerfeld","Trapp","Uhlmann","Vogler","Weidner","Zabel","Adler","Bergmann",
    "Conradi","Dietrich","Engel","Fricke","Glockner","Hansen","Ibsen","Junker","Kalckreuth","Lorenzen",
    "Mohr","Nissen","Ohlsen","Pietsch","Renner","Sander","Thiel","Ufer","Visser","Wendland",
    "Yildirim","Ziervogel","Baranowski","Aydin","Duarte","Novak","Horvath","Kovacs","Larsen","Meier",
    "Berger","Hofer","Steiner","Wagner","Zimmerer","Reiter","Fuchs","Jäger","Wolf","Hirsch",
    "Krämer","Bäcker","Lehmann","Schulz","Fischer","Weber","Becker","Hoffmann","Schäfer","Koch",
    "Bauer","Kriger","Klein","Wolf","Schröder","Neubauer","Brandner","Eichhorn","Feldmann","Grunert",
    "Halm","Isele","Jost","Kirchner","Laux","Moser","Nagel","Ott","Preuß","Roth",
    "Simon","Turk","Usinger","Vollmer","Wallner","Zorn","Amthor","Bock","Creutz","Deckert",
    "Ebert","Fendt","Glatz","Huber","Irmer","Jahn","Karg","Lutz","Michel","Noll",
]
STRASSEN = [
    "Finsterstraße","Gießergasse","Rabensteinplatz","Lindenpromenade","Grünplatz","Hafenkante",
    "Nordhaufenweg","Alter_Steg","Kupferdreh","Schmiedegasse","Wachtelweg","Donnerberg",
    "Silberblick","Nebelstieg","Rabenhorst","Eichenwall","Mühlendamm","Fischmarkt",
    "Laterntwete","Sternwarte","Kesselbrink","Dunkelmünde","Windhorst","Habichtsfeld",
    "Bruchsalier Weg","Karpfensteig","Amselgrund","Zinnwalder Promenade","Feuerrad","Grauhof",
    "Spinnwebgasse","Turmschneise","Moosbruch","Kaltental","Bibernellweg","Steinhuder Ring",
]
CLUBS = {
    "Freunde_der_Gefaengnisbuecherei": 46,
    "Eisen_Tempel_Fitness": 380,
    "Sammlerverein_Muenzen_und_More": 120,
    "Terminal_City_Library": 410,
    "Museum_fuer_Bash_Geschichte": 95,
    "Segelklub_Blauer_Pier": 150,
    "Schachclub_Zugzwang": 88,
    "Angelverein_Der_Karpfen": 130,
}
MARKEN = ["Opel","Ford","Volkswagen","Toyota","Skoda","Fiat","Volvo","Renault","Peugeot","Seat"]
FARBEN = ["Blau","Rot","Gruen","Schwarz","Weiss","Silber","Grau","Gelb","Mintgruen","Braun"]

ZEUGEN = [
    {"nr": 21045, "vorname": "Dietmar", "nachname": "Kluge", "rolle": "Zellennachbar", "alter": 58},
    {"nr": 33712, "vorname": "Burghard", "nachname": "Fink", "rolle": "Küchenchef", "alter": 61},
    {"nr": 29864, "vorname": "Josefine", "nachname": "Peters", "rolle": "Gefängnisbibliothekarin", "alter": 44},
]

RESERVED_NACHNAMEN = {"Petrov", "Holthaus", "Falkenberg", "Krüger", "Jost", "Kluge", "Fink", "Peters"}
NAMES_TAKEN = set()
PEOPLE = []
MITGLIEDER_BUECHEREI = []

def unique_name(g):
    while True:
        vn = rng.choice(VORNAME_M if g == "M" else VORNAME_W)
        nn = rng.choice(NACHNAMEN)
        if nn in RESERVED_NACHNAMEN:
            continue
        if (vn, nn) in NAMES_TAKEN:
            continue
        NAMES_TAKEN.add((vn, nn))
        return vn, nn

def make_person(vorname=None, nachname=None, geschlecht=None, alter=None, street=None):
    g = geschlecht or rng.choice(["M", "W", "W", "M", "D"])
    if vorname is None or nachname is None:
        vorname, nachname = unique_name(g)
    else:
        assert (vorname, nachname) not in NAMES_TAKEN, f"Duplikat: {vorname} {nachname}"
        NAMES_TAKEN.add((vorname, nachname))
    st = street or rng.choice(STRASSEN)
    p = {"vorname": vorname, "nachname": nachname, "geschlecht": g, "alter": alter or rng.randint(16, 90),
         "strasse": st, "zeile": rng.randint(1, 300)}
    PEOPLE.append(p)
    return p

def find_person(nn, vn=None):
    for p in PEOPLE:
        if p["nachname"] == nn and (vn is None or p["vorname"] == vn):
            return p
    return None

def fmt_addr(street, zeile):
    return f"{street.replace('_', ' ')}, Zeile {zeile}"

def load_alice():
    txt = (ASSETS / "alice_de.txt").read_text(encoding="utf-8")
    txt = re.sub(r"\s+", " ", txt)
    words = [w.strip(",.;:!?()[]\"'*_") for w in txt.split()]
    return [w for w in words if len(w) > 2 and not any(ch.isdigit() for ch in w)]

ALICE_WORDS = load_alice()

def noise_sentence(lo=8, hi=16):
    return " ".join(rng.choice(ALICE_WORDS) for _ in range(rng.randint(lo, hi))).capitalize() + "."

def noise_paragraph(lines=4):
    return "\n".join(noise_sentence() for _ in range(lines))

def ts(y=2026, mo=5, d=9, h=0, mi=0, se=0):
    return f"{y:04d}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}:{se:02d}"

def norm(s):
    s = s.upper()
    s = (s.replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE")
           .replace("ß", "SS").replace("É", "E").replace("È", "E").replace("Ê", "E"))
    return "".join(c for c in s if c.isalnum())

def sha(*variants):
    return ",".join(hashlib.sha256(norm(v).encode()).hexdigest() for v in variants)

def md5hex(s):
    return hashlib.md5(s.encode()).hexdigest()

def build_streets():
    d = FALL_DIR / "strassen"
    d.mkdir(parents=True, exist_ok=True)
    for s in STRASSEN:
        with open(d / (s.replace(" ", "_") + ".txt"), "w", encoding="utf-8") as f:
            for _ in range(300):
                f.write(noise_sentence(9, 18) + "\n")

def build_people():
    for _ in range(6590):
        make_person()
    taeter = make_person(TAETER_NAME.split()[0], TAETER_NAME.split()[1], "M", TAETER_ALT, "Fischmarkt")
    taeter["zeile"] = 87
    opfer = make_person(OPFER_NAME.split()[0], OPFER_NAME.split()[1], "M", OPFER_ALT, "Hafenkante")
    opfer["zeile"] = 205
    chefin = make_person(AUFTRAGGEBERIN.split()[0], AUFTRAGGEBERIN.split()[1], "W", 57, "Silberblick")
    chefin["zeile"] = 11
    ea = make_person(ELIM_A[0], ELIM_A[1], "M", 34, "Kaltental"); ea["zeile"] = 66
    eb = make_person(ELIM_B[0], ELIM_B[1], "M", 41, "Moosbruch"); eb["zeile"] = 178
    make_person(ZEUGEN[0]["vorname"], ZEUGEN[0]["nachname"], "M", 58, "Kaltental")["zeile"] = 39
    make_person(ZEUGEN[1]["vorname"], ZEUGEN[1]["nachname"], "M", 61, "Fischmarkt")["zeile"] = 4
    make_person(ZEUGEN[2]["vorname"], ZEUGEN[2]["nachname"], "W", 44, "Sternwarte")["zeile"] = 92
    pre = """***************
Um zur Straße zu gelangen, in der jemand wohnt, benutze die Datei
für diesen Straßennamen im Unterverzeichnis 'strassen'.
Um an der Tür zu klopfen und zu ermitteln, lies die Zeilennummer,
in der die Person wohnt, aus dieser Datei.  Sieht eine Zeile wie Kauderwelsch aus, bist du am falschen Haus.
***************

NAME\tGESCHLECHT\tALTER\tADRESSE"""
    lines = [pre]
    for p in PEOPLE:
        lines.append(f"{p['vorname']} {p['nachname']}\t{p['geschlecht']}\t{p['alter']}\t{fmt_addr(p['strasse'], p['zeile'])}")
    (FALL_DIR / "personen").write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_vehicles():
    lines = ["KENNZEICHEN\tMARKE\tFARBE\tJAHR\tBESITZER"]
    used = set()
    def plate():
        while True:
            pl = f"TC-{rng.randint(100,999)}-{chr(rng.randint(65,90))}{chr(rng.randint(65,90))}"
            if pl not in used:
                used.add(pl)
                return pl
    for _ in range(2500):
        o = rng.choice(PEOPLE)
        lines.append(f"{plate()}\t{rng.choice(MARKEN)}\t{rng.choice(FARBEN)}\t{rng.randint(1998, 2026)}\t{o['vorname']} {o['nachname']}")
    t = find_person(TAETER_NAME.split()[1], TAETER_NAME.split()[0])
    lines.append(f"TC-{rng.randint(100,999)}-WK\tSimson\tSchwarz\t1992\t{TAETER_NAME}")
    (FALL_DIR / "fahrzeuge").write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_memberships():
    d = FALL_DIR / "mitgliedschaften"
    d.mkdir(parents=True, exist_ok=True)
    pool = PEOPLE[:]
    rng.shuffle(pool)
    idx = 0
    for club, size in CLUBS.items():
        members = []
        while len(members) < size and idx < len(pool):
            members.append(pool[idx]); idx += 1
        if club == "Freunde_der_Gefaengnisbuecherei":
            for name in [(TAETER_NAME.split()[0], TAETER_NAME.split()[1]),
                         (AUFTRAGGEBERIN.split()[0], AUFTRAGGEBERIN.split()[1]),
                         (ELIM_A[0], ELIM_A[1]), (ELIM_B[0], ELIM_B[1])]:
                p = find_person(name[1], name[0])
                if p not in members:
                    members.append(p)
            CLUBS[club] = len(members)
            MITGLIEDER_BUECHEREI.clear()
            MITGLIEDER_BUECHEREI.extend(members)
        with open(d / club, "w", encoding="utf-8") as f:
            f.write(f"Mitgliederliste {club.replace('_', ' ')}\nStand: 01.05.2026\n\n")
            for m in sorted(members, key=lambda x: x["nachname"]):
                f.write(f"{m['nachname']}, {m['vorname']}\n")

def build_interviews():
    d = FALL_DIR / "befragungen"
    d.mkdir(parents=True, exist_ok=True)
    stmts = [
        "Ich habe nichts gesehen. Ich war die ganze Nacht über meinem Buch.",
        "Wer? Ich? Um diese Zeit schlafe ich. Fragen Sie meinen Anwalt.",
        "Ich habe nur eine Katze gehört. Oder war es ein Moped?",
        "Der Tee hier ist furchtbar. Da trinkt doch niemand freiwillig.",
        "Bücher bekommt man hier selten. Erst recht gespendete.",
        "Mein Nachbar hatte Besuch. Mehr sage ich nicht ohne Anwalt.",
        "Ich arbeite erst seit Montag hier. Keine Ahnung von irgendwas.",
        "Bittermandel? Das riecht man doch sofort. Hab ich nicht gerochen.",
    ]
    for _ in range(500):
        nr = rng.randint(10000, 99999)
        while (d / f"befragung-{nr}").exists():
            nr = rng.randint(10000, 99999)
        body = noise_paragraph(3) + "\n\n" + rng.choice(stmts) + "\n\n" + noise_paragraph(2) + "\n"
        (d / f"befragung-{nr}").write_text(body, encoding="utf-8")

    z = ZEUGEN
    (d / f"befragung-{z[0]['nr']}").write_text(
        f"AUSSAGE {z[0]['vorname']} {z[0]['nachname']}, {z[0]['rolle']}, {z[0]['alter']} (Zelle B-15):\n\n"
        "  |=|  |=|  |=|  |=|\n"
        "  |=|  |=|  |=|  |=|   <- Gitter zwischen B-14 und B-15\n\n"
        "René war gut drauf, weil seine Aussage bevorstand. Abends brachte die Küche\n"
        "wie immer Tee gegen 21:00. Ich hab meinen nicht angerührt. Seinen hat er\n"
        "getrunken, kurz nach halb neun... äh, nach elf VORMITTAGS rede ich Quatsch:\n"
        "kurz nach 21:12 Uhr wurde er seltsam ruhig. Ich rief sofort. Er roch...\n"
        "komisch. Wie BITTERMANDEL. Und seit Wochen las er NUR an einem Buch:\n"
        "einem gespendeten, mit einem Aufkleber vom MUSEUM FÜR BASH GESCHICHTE.\n", encoding="utf-8")

    (d / f"befragung-{z[1]['nr']}").write_text(
        f"AUSSAGE {z[1]['vorname']} {z[1]['nachname']}, {z[1]['rolle']}, {z[1]['alter']}:\n\n"
        "Meine Leute bringen den Tee um 21:00 auf die Blöcke. Wer genau fuhr, steht im\n"
        "SCHICHTPLAN. Ich selbst war bis 20:30 bei der Warenannahme, dann Büro.\n"
        "Auffällig: Seit ein paar Monaten spendet jemand ständig Bücher für die\n"
        "Gefängnisbücherei. Immer über die Firma GRÜNBLITZ CATERING als Transporteur.\n"
        "Spendenscheine laufen auf verschiedene Namen, aber immer dieselbe Adresse.\n", encoding="utf-8")

    (d / f"befragung-{z[2]['nr']}").write_text(
        f"AUSSAGE {z[1]['vorname']} {z[2]['vorname']} {z[2]['nachname']}, {z[2]['rolle']}, {z[2]['alter']}:\n\n"
        "Das Buch aus B-14 kam mit der letzten Bücherspende. Der Spendenkreis nennt\n"
        "sich 'Freunde der Gefängnisbücherei'. Wer Mitglied ist? Steht in unserer\n"
        "Mitgliederliste. Und in dem Buch war ein unsignierter BRIEF eingelegt,\n"
        "den haben wir zu den Effekten gelegt. Der Tote hat davor immer nur\n"
        "gegrinst und die ANFANGSBUCHSTABEN der Zeilen vorgesagt wie ein Gedicht.\n", encoding="utf-8")

GIT_ENV_BASE = {
    "GIT_AUTHOR_NAME": "dispatch-hafenkasse",
    "GIT_AUTHOR_EMAIL": "dispatch@hafenkasse.example",
    "GIT_COMMITTER_NAME": "dispatch-hafenkasse",
    "GIT_COMMITTER_EMAIL": "dispatch@hafenkasse.example",
}

def git_run(repo, *args, date=None):
    env = dict(os.environ)
    env.update(GIT_ENV_BASE)
    if date:
        iso = date.strftime("%Y-%m-%dT%H:%M:%S +0100")
        env["GIT_AUTHOR_DATE"] = iso
        env["GIT_COMMITTER_DATE"] = iso
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)

def git_out(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True, env=dict(os.environ, **GIT_ENV_BASE)).stdout

SENDUNG88_CSV = """# SENDUNG 88 — INTERN
# Format: SCHLUESSEL: WERT
DATUM: 2026-05-08
EMPFAENGER: JVA STEINBERG — KUECHE (BEGLEITET DIE BUCHSPENDE)
INHALT: 1 SACHBUCH + 1 BEUTEL KUECHENKRAEUTER ('TEEKRAUT')
UEBERGABE: ALTER FISCHSPEICHER, RAMPE 3 — 22.05., 23:00
KUNDE(KUERZEL): R.H.
FAHRER(CODENAME): KIEBITZ
"""

PETROV_TXT = """TEAMAKTE (INTERN)
Codename : KIEBITZ
Bereich  : KUECHE, JVA STEINBERG
Ausweis-Nr: TC-KUECHE-2207
Terminal : kk-kueche-01
Kontakt-Codename: SPHINX
Status   : aktiv
Hinweis  : Der Ausweis gilt zugleich als Terminal-Kennung in der Krankenstation.
"""

GECKO_TXT = """TEAMAKTE (INTERN)
Codename : GECKO
Bereich  : WASCHHAUS
Ausweis-Nr: TC-WAISCHE-3311
Terminal : wa-wasch-02
Kontakt-Codename: SPHINX
Status   : urlaub
"""

WEISUNG_MD = """# WEISUNG (NACH SENDUNG 88)
Kanal wechseln. KIEBITZ schweigt ab jetzt fuer immer.
Naechste Zahlung wie ueblich, Moneros. - S.
"""

def build_protokolle():
    d = FALL_DIR / "protokolle"
    d.mkdir(parents=True, exist_ok=True)

    staff_ids = {
        "2207": (TAETER_NAME.split()[1], TAETER_NAME.split()[0]),
        ELIM_A[2]: (ELIM_A[1], ELIM_A[0]),
        ELIM_B[2]: (ELIM_B[1], ELIM_B[0]),
        "2154": None, "2078": None, "2301": None,
    }
    extra_staff = []
    pool = [p for p in PEOPLE if p not in MITGLIEDER_BUECHEREI]
    for aid in ["2154", "2078", "2301"]:
        p = pool[rng.randrange(len(pool))]
        extra_staff.append((aid, p["nachname"], p["vorname"]))
        staff_ids[aid] = (p["nachname"], p["vorname"])

    plan = ["# SCHICHTPLAN JVA STEINBERG — 09.05.2026",
            "# Format: DATUM,SCHICHT,BEREICH,AUSWEIS-NR",
            "# Zuordnung Ausweis zu Name: ausweis-register.csv"]
    for aid in staff_ids:
        plan.append(f"2026-05-09,ABEND,KUECHE,{aid}")
    for _ in range(80):
        bereich = rng.choice(["TOR", "WERKSTATT", "WAESCHE", "BIBLIOTHEK", "HOF"])
        aid = f"{rng.randint(2000, 2400)}"
        plan.append(f"2026-05-{rng.randint(1, 9):02d},{rng.choice(['FRUEH','SPAET','ABEND','NACHT'])},{bereich},{aid}")
    (d / "schichtplan.csv").write_text("\n".join(plan) + "\n", encoding="utf-8")

    reg = ["# AUSWEIS-REGISTER DER JVA STEINBERG", "# Format: AUSWEIS-NR,NACHNAME,VORNAME"]
    for aid, name in staff_ids.items():
        if name:
            reg.append(f"{aid},{name[0]},{name[1]}")
    for _ in range(280):
        p = PEOPLE[rng.randrange(len(PEOPLE))]
        reg.append(f"{rng.randint(2000, 2400)},{p['nachname']},{p['vorname']}")
    (d / "ausweis-register.csv").write_text("\n".join(reg) + "\n", encoding="utf-8")

    access = ["# ZUTRITTSLOG KUECHENLIEFERANTENTUER — 09.05.2026",
              "# Format: ZEITSTEMPEL | RICHTUNG | TUER | AUSWEIS-NR"]
    def acc(ts_, richtung, aid):
        access.append(f"{ts_} | {richtung} | KUECHE-LIEFERUNG | {aid}")
    acc(ts(h=18, mi=58), "EINGANG", ELIM_B[2]); acc(ts(h=19, mi=55), "AUSGANG", ELIM_B[2])
    acc(ts(h=20, mi=31), "EINGANG", "2207");     acc(ts(h=21, mi=33), "AUSGANG", "2207")
    acc(ts(h=20, mi=34), "EINGANG", ELIM_A[2]); acc(ts(h=21, mi=47), "AUSGANG", ELIM_A[2])
    acc(ts(h=20, mi=26), "EINGANG", "2154");    acc(ts(h=21, mi=59), "AUSGANG", "2154")
    acc(ts(h=17, mi=41), "EINGANG", "2078");    acc(ts(h=18, mi=2), "AUSGANG", "2078")
    acc(ts(h=22, mi=14), "EINGANG", "2301");    acc(ts(h=23, mi=5), "AUSGANG", "2301")
    for _ in range(50):
        day = rng.choice([7, 8, 10])
        access.append(ts(d=day, h=rng.randint(6, 22), mi=rng.randint(0, 59), se=rng.randint(0, 59)) +
                      f" | {rng.choice(['EINGANG','AUSGANG'])} | {rng.choice(['KUECHE-LIEFERUNG','HAUPTTOR','HOF'])} | {rng.randint(2000, 2400)}")
    access.sort(key=lambda ln: ln.split(" | ")[0])
    (d / "zutritts-log.log").write_text("\n".join(access) + "\n", encoding="utf-8")

    hist = ["# TERMINAL-HISTORY KRANKENSTATION (APOTHEKE) — AUSZUG 09.05.2026",
            "# Format: '# session <ZEIT> user:<KENNUNG>' gefolgt von Befehlen",
            "# Kennung zu Ausweis: terminal-nutzer.csv"]
    hist += [
        "# session 2026-05-09 19:40:11 user:arzt-leitung",
        "grep -i kopfschmerzen formular-dosierung.csv",
        "# logout 19:52:03",
        "",
        "# session 2026-05-09 21:02:55 user:kk-kueche-03",
        "less lagerbestand-tee.csv",
        "grep -i bittermandel substanzen-merkblatt.csv",
        "man curl",
        "# logout 21:24:40",
        "",
        "# session 2026-05-09 21:41:07 user:kk-kueche-01",
        "tail -n 3 lieferungen-heute.log",
        "# logout 21:48:59",
        "",
        "# session 2026-05-09 22:10:41 user:pflege-nacht",
        "echo 'Ruhezustand' >> schichtbuch.txt",
        "# logout 22:15:12",
    ]
    (d / "apotheke-history.txt").write_text("\n".join(hist) + "\n", encoding="utf-8")

    tnut = ["# TERMINAL-KENNUNGEN KRANKENSTATION", "# Format: KENNUNG,AUSWEIS-NR",
            "kk-kueche-01,2207", "kk-kueche-03," + ELIM_A[2],
            "wa-wasch-02,3311", "arzt-leitung,1901", "pflege-nacht,1966"]
    for _ in range(30):
        tnut.append(f"user-{rng.randint(100,999)},{rng.randint(2000,2400)}")
    (d / "terminal-nutzer.csv").write_text("\n".join(tnut) + "\n", encoding="utf-8")

    target_md5 = hashlib.md5(BRIEF_C.encode()).hexdigest()
    fp = ["# FINGERPRINTS BESCHLAGNAHMENER SCHREIBSTÜCKE (INTERNE LISTE)",
          "# Format: MD5,GEGENSTAND",
          "# Die Liste stammt aus der Überwachung des Paketwegs. Genau EINS der",
          "# beschlagnahmten Briefe aus B-14 muss hier auftauchen."]
    fp.append(f"{target_md5},SENDUNG-88-ANHANG")
    for i, obj in enumerate(["ZEITUNGSAUSSCHNITT-MAI", "KUECHENBESTELLUNG-WOCHE19",
                             "BIBLIOTHIKSQUITTUNG-0413", "VERPFLEGUNGSGUTHABEN-B14"]):
        fp.append(f"{hashlib.md5((obj + str(rng.random())).encode()).hexdigest()},{obj}")
    (d / "fingerprints.txt").write_text("\n".join(fp) + "\n", encoding="utf-8")

BRIEF_C = """Sehr verehrte Familie,
Pünktlich zum Pfingstmarkt laufen die Fähren
Heringssand ein; die Möwen streiten laut.
Immer noch ist das Wetter unentschlossen;
Nachbars Katze schläft derweil in meinem Sessel.
Xanthippe habe ich sie getauft. Bis bald!
"""

def build_beweisstuecke():
    d = FALL_DIR / "beweisstuecke"
    d.mkdir(parents=True, exist_ok=True)
    (d / "brief-a.txt").write_text(noise_paragraph(6) + "\n", encoding="utf-8")
    (d / "brief-b.txt").write_text(noise_paragraph(7) + "\n", encoding="utf-8")
    (d / "brief-c.txt").write_text(BRIEF_C, encoding="utf-8")
    (d / "brief-d.txt").write_text(noise_paragraph(6) + "\n", encoding="utf-8")
    (d / "brief-e.txt").write_text(noise_paragraph(7) + "\n", encoding="utf-8")

    rot = MUENZNOTIZ_PLAIN.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÄÖÜäöüß",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklmÄÖÜäöüß"))
    inventar = ("INVENTAR PERSONLICHE EFFEKTE — ZELLE B-14 (FALKENBERG, R.)\n"
                "=========================================================\n"
                "1  Armbanduhr, defekt\n"
                "1  Taschenbuch 'Die Kunst der Kommandozeile'\n"
                "     - darin: 1 unsignierter Brief (siehe separates Beweisstück)\n"
                "1  Münzbörse mit 1 Metallmünze (Anhänger)\n"
                "1  Beutel Kräuter, Etikett 'TEEKRAUT'\n"
                "1  Zettel, handschriftlich, ROT13-verdreht:\n"
                "     >>> siehe beilage-muenznotiz.rot13 <<<\n")
    tmpd = d / "_tar_tmp"
    tmpd.mkdir()
    (tmpd / "inventar.txt").write_text(inventar, encoding="utf-8")
    (tmpd / "beilage-muenznotiz.rot13").write_text(rot, encoding="utf-8")
    with tarfile.open(d / "effekten-petrov.tar.gz", "w:gz") as tf:
        tf.add(tmpd / "inventar.txt", arcname="effekten-b14/inventar.txt")
        tf.add(tmpd / "beilage-muenznotiz.rot13", arcname="effekten-b14/beilage-muenznotiz.rot13")
    shutil.rmtree(tmpd)

def rot13(s):
    return s.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))

MUENZNOTIZ_PLAIN = ("Münzbörse: 1 physischer Monero-Anhänger, innen graviert:\n"
                    "Fischspeicher, Rampe 3. Nie allein hinfahren. - K.\n")

MAIL_PLAIN = (
    "Von: unbekannt@relay.hafenkasse.example\n"
    "An: KIEBITZ\n"
    "Betreff: Sendung 88\n\n"
    "Der Zeuge schweigt ab Donnerstag. Deine Belohnung liegt am alten\n"
    "Fischspeicher, Rampe 3, wie besprochen. Danach Funkstille.\n"
    "Verbrennen. - S.\n")

EPILOG_PLAIN = """EPILOG — VERSIEGELTER BERICHT DES TCPD
======================================
Am Freitag, 22.05., 23:00 Uhr nahm das TCPD am alten Fischspeicher,
Rampe 3, den Kurier fest — und eine Überraschung: die Fahrerin war
keine andere als M. Kowalczyk, die sich ihren Freikauf verdiente.
Ihre Aussage führte direkt zur Vorstandsvorsitzenden der Hafenbank.
Fall 48/III: GELÖST. Die Hafenkasse ist Geschichte.
"""

def build_verschluesselt():
    d = FALL_DIR / "verschluesselt"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "_mail.tmp"
    src.write_text(MAIL_PLAIN, encoding="utf-8")
    enc = d / "auftraggeberin.eml.aes"
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-iter", "10000",
                    "-a", "-in", str(src), "-out", str(enc), "-pass", "pass:" + CODENAME_BOSS],
                   check=True, capture_output=True)
    chk = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-a", "-pbkdf2",
                          "-iter", "10000", "-in", str(enc), "-pass", "pass:" + CODENAME_BOSS],
                         check=True, capture_output=True)
    assert chk.stdout.decode() == MAIL_PLAIN, "AES roundtrip fehlgeschlagen"
    src.unlink()

def build_git_repo():
    repo = FALL_DIR / "repos" / "hafenkasse-versand"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git_run(repo, "init", "-b", "main", date=datetime(2026, 3, 1, 9, 0, 0))
    (repo / "README.md").write_text("# Hafenkasse Versand — interne Tourenplanung\nDiskret. Immer.\n", encoding="utf-8")
    (repo / "config").mkdir()
    (repo / "config" / "lagerraum.txt").write_text(noise_paragraph(6) + "\n", encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Initiale Lagertouren",
                                        date=datetime(2026, 3, 1, 9, 12, 0))
    (repo / "kunden").mkdir()
    (repo / "kunden" / "sendung-71.csv").write_text("# SENDUNG 71\nEMPFAENGER: KESSELBRINK 4\nINHALT: PALETEN\n", encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Sendung 71 erfasst",
                                        date=datetime(2026, 3, 18, 15, 40, 0))
    (repo / "team").mkdir()
    (repo / "team" / "petrov.txt").write_text(PETROV_TXT, encoding="utf-8")
    (repo / "team" / "gecko.txt").write_text(GECKO_TXT, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Teamdateien ergänzt",
                                        date=datetime(2026, 4, 28, 17, 5, 0))
    C_TEAM = git_out(repo, "rev-parse", "HEAD").strip()
    (repo / "kunden" / "sendung-88.csv").write_text(SENDUNG88_CSV, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Sendung 88 eingerichtet",
                                        date=datetime(2026, 5, 8, 22, 15, 0))
    C_SENDUNG = git_out(repo, "rev-parse", "HEAD").strip()
    (repo / "entwurf").mkdir()
    (repo / "entwurf" / "weisung.md").write_text(WEISUNG_MD, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Entwurf Weisung (intern)",
                                        date=datetime(2026, 5, 9, 23, 48, 0))
    DANGLING = git_out(repo, "rev-parse", "HEAD").strip()
    git_run(repo, "reset", "--hard", "HEAD~1")
    (repo / "team" / "petrov.txt").unlink()
    (repo / "team" / "gecko.txt").unlink()
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Audit: sensible Teamdateien entfernen",
                                        date=datetime(2026, 5, 10, 6, 2, 0))
    (repo / "kunden" / "sendung-88.csv").unlink()
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Archivbereinigung: Sendung 88 entfernt",
                                        date=datetime(2026, 5, 10, 6, 5, 0))
    if (repo / "team").is_dir() and not any((repo / "team").iterdir()):
        (repo / "team").rmdir()
    subprocess.run(["git", "reflog", "expire", "--expire-unreachable=now", "--all"],
                   cwd=repo, check=True, capture_output=True, env=dict(os.environ, **GIT_ENV_BASE))
    fsck = subprocess.run(["git", "fsck", "--dangling"], cwd=repo, capture_output=True,
                          text=True, env=dict(os.environ, **GIT_ENV_BASE)).stdout
    assert DANGLING in fsck, f"dangling commit fehlt: {fsck!r}"
    archiv = repo / ".gitarchiv"
    if archiv.exists():
        shutil.rmtree(archiv)
    shutil.copytree(repo / ".git", archiv)
    starter = repo / "ermittlung-starten.sh"
    starter.write_text(
        "#!/bin/sh\n"
        "# Beschlagnahmtes Server-Image des Versands wiederherstellen:\n"
        "set -e\n"
        'DIR="$(cd "$(dirname "$0")" && pwd)"\n'
        'rm -rf "$DIR/.git"\n'
        'cp -R "$DIR/.gitarchiv" "$DIR/.git"\n'
        'echo "Image wiederhergestellt. Ab jetzt: cd in dieses Verzeichnis und git nutzen."\n',
        encoding="utf-8")
    os.chmod(starter, 0o755)
    return {"C_TEAM": C_TEAM, "C_SENDUNG": C_SENDUNG, "DANGLING": DANGLING}

def build_firmenregister():
    d = FALL_DIR / "firmenregister"
    d.mkdir(parents=True, exist_ok=True)
    rows = ["# HAFENBANK TERMINAL CITY — VORSTAND (ÖFFENTLICHES REGISTER)",
            "# Format: NACHNAME,VORNAME,KUERZEL,ROLLE",
            "Holthaus,Regina,RH,Vorstandsvorsitzende"]
    ku = ["TW","MB","FK","LS"]
    for k in ku:
        p = PEOPLE[rng.randrange(len(PEOPLE))]
        rows.append(f"{p['nachname']},{p['vorname']},{k},Vorstand")
    (d / "hafenbank-vorstand.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

CRIME_SCENE = """AKTE 48/III — DIE STILLE ZEUGIN
===============================

      _______________________________
     |  J V A   S T E I N B E R G    |
     |                               |
     |  |=|=|=|=|=|=|=|=|=|=|=|=|=|  |
     |  |=|  B - 1 4          |=|=|  |   ZELLE B-14
     |  |=|=|=|=|=|=|=|=|=|=|=|=|=|  |
     |         ___                   |
     |        (   )  <- TEETASSE     |   TATNACHT: 09./10. MAI 2026
     |         \\_/      BITTERMANDEL |
     |_______________________________|

LAGEBERICHT
-----------
René FALKENBERG (49), angeklagt in der Sache 'Hafenkasse', sollte am
Donnerstag als Kronzeuge aussagen. Am Abend des 9. Mai wurde er tot in
seiner Zelle B-14 gefunden — vergiftet mit CYANID im Abendtee
(21:12 Uhr, typischer BITTERMANDELGERUCH).

Kein Gewalteinbruch. Der Tee kam regulär über die Küchenroute.
Seit Wochen las Falkenberg nur ein einziges Buch — eine SPENDE für die
Gefängnisbücherei, mit Aufkleber 'MUSEUM FÜR BASH GESCHICHTE'. In dem
Buch: ein unsignierter Brief. Die Totenwache hörte ihn noch die
ANFANGSBUCHSTABEN der Zeilen aufsagen, 'wie ein Gedicht'.

Hintergrund (Fall 47/II): Falkenbergs Kurierin sitzt inzwischen als
Kronzeugentin im Zeugenschutz — sie kooperiert. Ihr Netzwerk 'Hafen-
kasse' will verhindern, dass Falkenberg ebenfalls aussagt.

Beweisstücke
------------
* Persönliche Effekten aus B-14 (als Archiv gepackt):
      fall/beweisstuecke/effekten-petrov.tar.gz
* Fünf beschlagnahmte Briefe aus der Zelle (unsigniert):
      fall/beweisstuecke/brief-a.txt ... brief-e.txt
* Fingerabdruck-Liste des abgehörten Paketwegs:
      fall/protokolle/fingerprints.txt
* Ein verschlüsseltes E-Mail vom Server der Küchenleitung:
      fall/verschluesselt/auftraggeberin.eml.aes
* Beschlagnahmtes Tourensystem des Versands 'Hafenkasse':
      fall/repos/hafenkasse-versand   (ein echtes Git-Repository!)
* Protokolle des Tattages (Schichtplan, Zutritt, Apotheken-Terminal):
      fall/protokolle/

Zeugen (Videoaussagen, Nummern beachten!)
-----------------------------------------
AUSSAGE #%(z0)s — %(z0v)s %(z0n)s, Zellennachbar:
   riech BITTERMANDEL am Tee; das Buch und seine 'Gedicht'-Lesart.
   Details: fall/befragungen/befragung-%(z0)s

AUSSAGE #%(z1)s — %(z1v)s %(z1n)s, Küchenchef:
   Tee-Route läuft über den SCHICHTPLAN; Bücher kommen seit Monaten
   via GRÜNBLITZ CATERING.
   Details: fall/befragungen/befragung-%(z1)s

AUSSAGE #%(z2)s — %(z2v)s %(z2n)s, Gefängnisbibliothekarin:
   der Brief lag IM Buch; der Tote buchstabierte gern die
   ANFANGSBUCHSTABEN der Zeilen.
   Details: fall/befragungen/befragung-%(z2)s

Das TCPD braucht deinen Bericht: WER mischte den Tee — und WER hat es
befohlen? Prüfe deine Zwischenergebnisse jederzeit mit ./pruefer.sh
"""

ANLEITUNG = """ANLEITUNG — DIE KOMMANDOZEILEN-MORDE III
========================================

Terminal City, wenige Wochen danach: Der Kronzeuge stirbt in seiner
Zelle, giftig, präzise, abgemacht. Diesmal führen die Spuren durch
Schichtpläne, Zutrittslogs, eine Terminal-History, ein tar-Archiv,
einen Brief mit Geheimcode und das Tourensystem der 'Hafenkasse'.

REGELN
------
1. Benutze ausschließlich das Terminal. Keinen Texteditor und keine
   grafischen Tools, um Dateien im Ordner 'fall/' anzusehen.
2. Erlaubt sind: 'cat', 'less', 'head', 'tail', 'grep', 'find',
   'sort', 'uniq', 'cut', 'tr', 'tar', 'openssl', 'git', 'md5'
   bzw. 'md5sum' und alles, was im SPICKZETTEL steht.
3. Alles, was du brauchst, ist IM Fallordner versteckt. Du musst
   nichts aus dem Internet laden.
4. Steck fest? Die Dateien 'hinweis1' bis 'hinweis10' helfen — aber
   lies sie der Reihe nach und nur, wenn du wirklich nicht weiterweißt.

SO STARTEST DU
--------------
    cat anleitung          <- das hier
    cat spickzettel.md     <- Kommandozeilen-Nachschlagewerk
    ls fall/
    less fall/tatort       <- dein erster echter Lead!

WERKZEUGE
---------
    ./pruefer.sh           <- prüft deine Fortschritte (optional, macht Spaß)

ZIEL
----
Finde heraus, WER den Tee gemischt hat, WER es befohlen hat — und
unter welchem Decknamen die Order lief. Den Abschlussweg findest du
in 'loesung'.

Viel Erfolg, Detektiv.
"""

HINTS = [
"""HINWEIS 1
=========
Starte mit:  less fall/tatort
Notiere dir: Opfer, Gift-Zeitpunkt (21:12), das BUCH, den Brief und die
drei BEFRAGUNGS-NUMMERN der Zeugen.""",

"""HINWEIS 2
=========
Die drei Zeugendetails liegen hier:
    ls fall/befragungen
    cat fall/befragungen/befragung-<NUMMER>
Wichtig sind: Tee-Route über die KÜCHE, die Buchspende und der Hinweis
auf die ANFANGSBUCHSTABEN des Briefes.""",

"""HINWEIS 3
=========
Wer konnte den Tee stellen? Zwei Dateien gehören zusammen:
    fall/protokolle/schichtplan.csv      (wer war im ABEND/KUECHE?)
    fall/protokolle/zutritts-log.log     (wer ging wann rein/raus?)
Die Ausweis-Nummern löst du auf mit:
    fall/protokolle/ausweis-register.csv""",

"""HINWEIS 4
=========
Filtere die Küchen-Leute mit Zutritt zwischen ca. 20:30 und 21:35.
Dann aussortieren:
* Eine Person hatte währenddessen eine AKTIVE SESSION am Apotheken-
  Terminal (andere Gebäudehälfte): siehe apotheke-history.txt und
  terminal-nutzer.csv.
* Eine Person verließ die Tür bereits um 19:55 und kam nicht zurück.
Übrig bleibt GENAU eine Ausweis-Nummer.""",

"""HINWEIS 5
=========
Der Übrige ist dein Innendienst-Täter. Seine Sachen wurden gepackt:
    tar -tzf fall/beweisstuecke/effekten-petrov.tar.gz
    tar -xzf fall/beweisstuecke/effekten-petrov.tar.gz -C /tmp/effekten
Im Inventar steht: ein unsignierter Brief — und eine ROT13-Notiz.""",

"""HINWEIS 6
=========
Welcher der fünf Briefe aus B-14 war der geschmuggelte?
Die Überwachung listet Fingerabdrücke (MD5):
    fall/protokolle/fingerprints.txt
Prüfe alle Briefe:
    md5 fall/beweisstuecke/brief-*.txt     (Linux: md5sum)
Genau EINER passt zu 'SENDUNG-88-ANHANG'.""",

"""HINWEIS 7
=========
Der echte Brief trägt einen Geheimcode: nimm die ERSTEN BUCHSTABEN
jeder Zeile:
    cut -c1 fall/beweisstuecke/brief-c.txt | tr -d '\\n'
Was da steht, ist der CONTACT-CODENAME der Drahtzieherin — sechs
Buchstaben, eine Fabelwesen-Fräulein. Merken! Du brauchst sie als
Passwort (Hinweis 8) und als Antwort beim pruefer.""",

"""HINWEIS 8
=========
Das E-Mail der Küchenleitung ist AES-verschlüsselt:
    openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
      -in fall/verschluesselt/auftraggeberin.eml.aes -pass pass:PASSWORT
PASSWORT = der Codename aus Hinweis 7 (GROSSBUCHSTABEN).""",

"""HINWEIS 9
=========
Wer steckt hinter dem Kürzel 'R.H.'? Zwei Wege:
* Git-Forensik im beschlagnahmten Versand-Repo:
    sh fall/repos/hafenkasse-versand/ermittlung-starten.sh
    cd fall/repos/hafenkasse-versand
  Gesucht: 'team/petrov.txt' und 'kunden/sendung-88.csv' in ALTEN
  Commits (git show COMMIT:PFAD) — plus ein VERLORENER Commit
  (git fsck --lost-found) mit einer Weisung.
* Das öffentliche Register:
    fall/firmenregister/hafenbank-vorstand.csv
  Dort verrät der KURZEL den vollständigen Namen.""",

"""HINWEIS 10
===========
Wenn du den vollständigen Namen der Auftraggeberin hast:
    echo -n 'VORNAME NACHNAME' | md5
    grep -if <HASH> kodiert
Wie du den Bericht abgibst, steht in 'loesung'.""",
]

SPICKZETTEL = """SPICKZETTEL — DIE KOMMANDOZEILEN-MORDE III
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
  openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
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
"""

LOESUNG = """LÖSUNG — WIE MAN DEN FALL ABSCHLIESST
=====================================

Wenn du sicher bist, den vollständigen Namen der Auftraggeberin zu
kennen, dann prüfe ihn so (macOS):

    echo -n 'Vorname Nachname' | md5
    grep -if '<DEIN-HASH>' kodiert

Auf Linux heißt es 'md5sum' statt 'md5'. Findet grep den Hash in der
Datei 'kodiert': Herzlichen Glückwunsch, Detektiv.

Danach wartet das versiegelte EPILOG auf dich (das Passwort kennst du —
sechs Buchstaben, ein Fabelwesen):

    openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
      -in fall/verschluesselt/epilog.aes -pass pass:PASSWORT

Und './pruefer.sh' bewertet deinen Abschlussbericht.
"""

EPILOG_FINAL = """EPILOG — VERSIEGELTER BERICHT DES TCPD
======================================
Am Freitag, 22.05., 23:00 Uhr nahm das TCPD am alten Fischspeicher,
Rampe 3, den Kurier fest — und eine Überraschung: die Fahrerin war
keine andere als M. Kowalczyk, die sich ihren Freikauf verdient hat.
Ihre Aussage führte direkt zur Vorstandsvorsitzenden der Hafenbank.
Fall 48/III: GELÖST. Die Hafenkasse ist Geschichte.
"""

KODIER_FUELLER = [
    "Alicia Vogt","Benno Krause","Cem Aydin","Dörthe Peters","Emil Brandt",
    "Fenna Holm","Gustav Lehmann","Helga Ruf","Ingolf Bade","Jana Krebs",
    "Kalle Petersen","Lene Maak","Morten Siewert","Nadine Kolb","Otto Waalkes",
    "Pia Dahms","Quentin Tarantino","Rita Heyer","Sven-Ole Frahm","Telse Kruse",
    "Ulvi Alparslan","Vitus Frech","Wanja Slawik","Xenia Marschner","Yilmaz Aygün",
    "Ziska Riemann","Anselm Grunert","Berta Ohlsen","Clemens Usinger","Dagmar Vollmer",
]

def build_kodiert_loesung_epilog():
    out, seen = [], set()
    for name in KODIER_FUELLER:
        for v in (name, name.lower()):
            h = md5hex(v)
            if h not in seen:
                seen.add(h); out.append(h)
    for v in (AUFTRAGGEBERIN, AUFTRAGGEBERIN.lower()):
        h = md5hex(v)
        if h not in seen:
            seen.add(h); out.append(h)
    rng.shuffle(out)
    (GAME / "kodiert").write_text("\n".join(out) + "\n", encoding="utf-8")

    d = FALL_DIR / "verschluesselt"
    src = d / "_epilog.tmp"
    src.write_text(EPILOG_FINAL, encoding="utf-8")
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
                    "-iter", "10000", "-a", "-in", str(src),
                    "-out", str(d / "epilog.aes"), "-pass", "pass:" + CODENAME_BOSS],
                   check=True, capture_output=True)
    src.unlink()

PRUEFER_TEMPLATE = """#!/usr/bin/env bash
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
  printf '\\n== PRUEFPUNKT %s ==\\n%s\\n> ' "$nr" "$frage"
  read -r antwort
  h="$(printf '%s' "$(norm "$antwort")" | SHA256)"
  ok=0
  for ALT in ${korrekt//,/ }; do
    [ "$h" = "$ALT" ] && ok=1
  done
  if [ "$ok" = "1" ]; then
    echo "  >> RICHTIG. +$punkte Punkte"
    grep -q "^$nr " "$FORT" 2>/dev/null || printf '%s %s\\n' "$nr" "$punkte" >> "$FORT"
  else
    echo "  >> Leider nicht. (Aktenzeichen bleibt offen.)"
  fi
}

ART='
 ____________________
|  T E R M I N A L   |
|  C I T Y   I I I   |
|____________________|
   \\^~~^/  TCPD
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

ask 1 "Wie lautete der vollständige Name des Opfers?" "@H_OPFER@" 20
ask 2 "Wer hat den Tee gemischt? (vollständiger Name des Innendienst-Täters)" "@H_TAETER@" 20
ask 3 "Unter welchem Codename lief die Order der Drahtzieherin?" "@H_CODE@" 20
ask 4 "Wie lautet der vollständige Name der Auftraggeberin?" "@H_CHEFIN@" 20
ask 5 "Wo sollte die Übergabe stattfinden? (Ort)" "@H_ORT@" 20

GESAMT=$(awk '{s+=$2} END{print s+0}' "$FORT" 2>/dev/null)
GESAMT=${GESAMT:-0}
echo
echo "== ZWISCHENSTAND: $GESAMT / 100 Punkte =="

if [ "$GESAMT" = "100" ]; then
cat <<'EOF'

      _____
     |A .  |-----.
     | /.\\ |c)   |   FALL 48/III GELÖST!
     |(_._)| /\\/ |
     |  |  |-----'
     |___V_|
EOF
echo "Bravo, Detective. Reiche deinen Bericht bei loesung ein."
fi
exit 0
"""

README = """DIE KOMMANDOZEILEN-MORDE III
============================

      .______________________________________.
      |  ____  ____  ____  ____  ____  ____   |
      | ||T ||||E ||||R ||||M ||||I ||||N ||  |
      | ||__||||__||||__||||__||||__||||__||  |
      | |/==\\||/==\\||/==\\||/==\\||/==\\||/==\\|  |
      |   CITY III - DIE STILLE ZEUGIN        |
      |______________________________________|

Ein Kronzeuge stirbt in seiner Zelle — vergiftet, präzise, abgemacht.
Diesmal führen die Spuren durch Schichtpläne, Zutrittslogs, eine
Terminal-History, ein tar-Archiv, einen Brief mit Geheimcode und das
Git-System der 'Hafenkasse'.

Schnellstart
------------
    git clone <dieses-repo>
    cd <repo-name>
    cat anleitung
    less fall/tatort

Du brauchst nur ein Terminal (macOS oder Linux) mit `git`, `openssl`,
`tar` und `base64`. Keine Installation, kein Internet während des Spiels.

Für Einsteiger: `cat spickzettel.md`
Fortschritt prüfen: `./pruefer.sh`

Über dieses Projekt
-------------------
Teil III der Reihe nach "The Command Line Murders" von Noah Veltman
(github.com/veltman/clmystery), in der Tradition der deutschen
Übersetzung von redbasecap. Alle Figuren und Ereignisse sind frei
erfunden. Der Rauschtext stammt aus "Alice's Abenteuer im Wunderland"
(Antonie Zimmermann, 1869, Public Domain, Gutenberg #19778).

Lizenz: MIT — siehe LICENSE.md
"""

LICENSE = """MIT License

Copyright (c) 2026 Die Kommandozeilen-Morde III Autoren
Konzept-Tradition: "The Command Line Murders" (c) Noah Veltman, MIT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def main():
    if FALL_DIR.exists():
        shutil.rmtree(FALL_DIR)
    FALL_DIR.mkdir(parents=True)
    for name in ["kodiert", "anleitung", "spickzettel.md", "loesung", "README.md", "LICENSE.md"]:
        p = GAME / name
        if p.exists():
            p.unlink()
    for i in range(1, 11):
        p = GAME / f"hinweis{i}"
        if p.exists():
            p.unlink()

    build_streets()
    build_people()
    build_vehicles()
    build_memberships()
    build_interviews()
    build_protokolle()
    build_beweisstuecke()
    build_verschluesselt()
    gitmeta = build_git_repo()
    build_firmenregister()
    build_kodiert_loesung_epilog()

    z = ZEUGEN
    (FALL_DIR / "tatort").write_text(CRIME_SCENE % {
        "z0": z[0]["nr"], "z0v": z[0]["vorname"], "z0n": z[0]["nachname"],
        "z1": z[1]["nr"], "z1v": z[1]["vorname"], "z1n": z[1]["nachname"],
        "z2": z[2]["nr"], "z2v": z[2]["vorname"], "z2n": z[2]["nachname"],
    }, encoding="utf-8")
    (GAME / "anleitung").write_text(ANLEITUNG, encoding="utf-8")
    (GAME / "spickzettel.md").write_text(SPICKZETTEL, encoding="utf-8")
    (GAME / "loesung").write_text(LOESUNG, encoding="utf-8")
    (GAME / "README.md").write_text(README, encoding="utf-8")
    (GAME / "LICENSE.md").write_text(LICENSE, encoding="utf-8")
    for i, h in enumerate(HINTS, start=1):
        (GAME / f"hinweis{i}").write_text(h, encoding="utf-8")

    pruefer = (PRUEFER_TEMPLATE
        .replace("@H_OPFER@", sha(OPFER_NAME, OPFER_NAME.replace("é", "e")))
        .replace("@H_TAETER@", sha(TAETER_NAME))
        .replace("@H_CODE@", sha(CODENAME_BOSS))
        .replace("@H_CHEFIN@", sha(AUFTRAGGEBERIN, " ".join(AUFTRAGGEBERIN.split()[::-1])))
        .replace("@H_ORT@", sha(DROP, DROP.replace("alter ", ""),
                                DROP + ", 22.05. 23:00",
                                DROP.replace("alter ", "") + ", 22.05. 23:00")))
    p = GAME / "pruefer.sh"
    p.write_text(pruefer, encoding="utf-8")
    os.chmod(p, 0o755)

    acrostic = "".join(ln.strip()[0] for ln in BRIEF_C.strip().splitlines() if ln.strip()).upper()
    meta = {
        "opfer": OPFER_NAME, "taeter": TAETER_NAME, "chefin": AUFTRAGGEBERIN,
        "codename_chefin": CODENAME_BOSS, "codename_taeter": CODENAME_TAETER,
        "ausweis_taeter": AUSWEIS_TAETER, "drop": DROP,
        "elim_a": {"name": f"{ELIM_A[0]} {ELIM_A[1]}", "ausweis": ELIM_A[2], "terminal": ELIM_A[3]},
        "elim_b": {"name": f"{ELIM_B[0]} {ELIM_B[1]}", "ausweis": ELIM_B[2]},
        "zeugen": [w["nr"] for w in z],
        "hashes": {
            "opfer_sha256": sha(OPFER_NAME, OPFER_NAME.replace("é", "e")).split(","),
            "taeter_sha256": [sha(TAETER_NAME)],
            "code_sha256": [sha(CODENAME_BOSS)],
            "chefin_sha256": sha(AUFTRAGGEBERIN,
                                 AUFTRAGGEBERIN.split()[1] + " " + AUFTRAGGEBERIN.split()[0]).split(","),
            "ort_sha256": sha(DROP, DROP.replace("alter ", ""),
                              DROP + ", 22.05. 23:00",
                              DROP.replace("alter ", "") + ", 22.05. 23:00").split(","),
            "chefin_md5": md5hex(AUFTRAGGEBERIN),
        },
        "counts": {
            "personen": len(PEOPLE),
            "buechereiclub_size": CLUBS["Freunde_der_Gefaengnisbuecherei"],
            "interviews": len(list((FALL_DIR / "befragungen").iterdir())),
            "strassen": len(STRASSEN),
        },
        "git": gitmeta,
        "verify": {
            "muenz_rot13_sha256": hashlib.sha256(MUENZNOTIZ_PLAIN.encode()).hexdigest(),
            "acrostic": "SPHINX",
            "fingerprint_target_md5": hashlib.md5(BRIEF_C.encode()).hexdigest(),
            "history_user_elim": ELIM_A[3],
            "history_logout": "21:24:40",
            "petrov_entry": ts(h=20, mi=31),
            "petrov_exit": ts(h=21, mi=33),
            "elim_b_last_exit": ts(h=19, mi=55),
            "sendung88_contains": "FISCHSPEICHER",
            "taeter_txt_contains": AUSWEIS_TAETER,
            "dangling_contains": "KIEBITZ",
            "vorstand_contains": "Holthaus,Regina,RH",
            "mail_contains": "Fischspeicher",
        },
    }
    (Path(__file__).resolve().parent / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("OK generiert:", GAME)
    print("Acrostichon:", acrostic)
    print("Club:", CLUBS["Freunde_der_Gefaengnisbuecherei"])

if __name__ == "__main__":
    main()
