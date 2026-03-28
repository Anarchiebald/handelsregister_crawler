import xml.etree.ElementTree as ET
import sqlite3
import re
from pathlib import Path

conn = sqlite3.connect("handelsregister.db")
c = conn.cursor()

ns = {"tns": "http://www.xjustiz.de"}

### Hilfsfunktionen Datenbank ###

def check_and_insert_person(person_nameNEU, person_geburtsdatumNEU):
    c.execute("""
        SELECT person_id
        FROM person
        WHERE person_name = ?
          AND person_geburtsdatum = ?
    """, (person_nameNEU, person_geburtsdatumNEU))

    row = c.fetchone()
    if row:
        return row[0]

    c.execute("""
        INSERT INTO person (person_name, person_geburtsdatum)
        VALUES (?, ?)
    """, (person_nameNEU, person_geburtsdatumNEU))

    return c.lastrowid

def check_it_company(unternehmen_beschreibung):
    if not unternehmen_beschreibung:
        return False
    it_woerter = re.compile(
        r"\b(it|edv|soft|software|hard|hardware|informationssysteme|computer|data|informatik|systemhaus|telekommunikationstechnik|informationstechnik)\b",
        re.IGNORECASE)
    return bool(it_woerter.search(unternehmen_beschreibung))

def insert_company(hrb, unternehmen_name, rechtsform_code, plz, bundesland, ort, strasse, hausnummer, beschreibung, stammkapital, suchwort):
    c.execute("""
        SELECT unternehmen_id
        FROM it_unternehmen
        WHERE hrb = ?
    """, (hrb,))

    row = c.fetchone()
    if row:
        return row[0]

    c.execute("""
    INSERT INTO it_unternehmen (
    hrb, unternehmen_name, rechtsform, plz, bundesland, ort, strasse, hausnummer, beschreibung, stammkapital, suchwort
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (hrb, unternehmen_name, rechtsform_code, plz, bundesland, ort, strasse, hausnummer, beschreibung,
               stammkapital, suchwort)
              )
    return c.lastrowid

def insert_funktion(unternehmen_id, person_id, rolle):
    c.execute("""
        INSERT INTO funktion (unternehmen_id, person_id, rolle)
        VALUES (?, ?, ?)
    """, (unternehmen_id, person_id, rolle))

def get_bundesland_from_plz(plz):
    c.execute("""
        SELECT bundesland
        FROM plz_bundesland
        WHERE plz = ?
    """, (plz,))

    row = c.fetchone()
    return row[0] if row else None


### Verarbeiten XML ###

def process_xml_file(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()


    def findtext(path):
        return root.findtext(path, namespaces=ns)

    unternehmen_name = findtext(".//tns:bezeichnung.aktuell")
    rechtsform_code = findtext(".//tns:angabenZurRechtsform/tns:rechtsform/code")
    hrb = findtext(".//tns:aktenzeichen.strukturiert/tns:laufendeNummer")
    plz = findtext(".//tns:anschrift/tns:postleitzahl")
    ort = findtext(".//tns:anschrift/tns:ort")
    strasse = findtext(".//tns:anschrift/tns:strasse")
    hausnummer = findtext(".//tns:anschrift/tns:hausnummer")
    beschreibung = findtext(".//tns:basisdatenRegister/tns:gegenstand")
    stammkapital = findtext(".//tns:zusatzGmbH/tns:stammkapital/tns:zahl")
    bundesland = get_bundesland_from_plz(plz) or xml_path.parent.name
    suchwort = xml_path.parts[-3]

    if not check_it_company(beschreibung):
        return False

    unternehmen_id = insert_company(hrb, unternehmen_name, rechtsform_code, plz, bundesland, ort, strasse, hausnummer, beschreibung, stammkapital, suchwort)
    beteiligungen = root.findall(".//tns:beteiligung", namespaces=ns)

    ROLLEN = {
        "086": "Geschaeftsfuehrer",
        "285": "Prokurist"
    }

    for beteiligung in beteiligungen:
        rolle = ROLLEN.get(beteiligung.findtext(".//tns:rollenbezeichnung/code", namespaces=ns))

        if not rolle:
            continue

        vorname = beteiligung.findtext(".//tns:vollerName/tns:vorname", namespaces=ns)
        nachname = beteiligung.findtext(".//tns:vollerName/tns:nachname", namespaces=ns)
        geburtsdatum = beteiligung.findtext(".//tns:geburt/tns:geburtsdatum", namespaces=ns)

        if not vorname or not nachname:
            continue

        person_name = f"{vorname} {nachname}"
        person_id = check_and_insert_person(person_name, geburtsdatum)
        insert_funktion(unternehmen_id, person_id, rolle)

    return True



### XML aus Ordnern ###

basis_ordner = Path("Daten")

conn.execute("BEGIN")

for xml_file in basis_ordner.rglob("*.xml"):
    try:
        process_xml_file(xml_file)
    except Exception as e:
        print(f"Fehler in {xml_file}: {e}")


conn.commit()
conn.close()