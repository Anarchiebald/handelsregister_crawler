# Handelsregister Scraper & Datenverarbeitung

Dieses Projekt dient der automatisierten Erhebung und Auswertung von Unternehmensdaten aus dem deutschen Handelsregister.

## Komponenten

### `handelsregister_spider.py`

Scrapy-Spider zur automatisierten Abfrage des Handelsregisterportals.

* Führt Suchanfragen basierend auf Stichwörtern durch
* Navigiert durch die Ergebnislisten
* Lädt strukturierte Registerinhalte ("SI-Dokument") als xml-Datei herunter

### `read_xml.py`

Verarbeitungsskript zur Extraktion und Speicherung der Daten.

* Liest heruntergeladene XML-Dateien ein
* Extrahiert Unternehmens- und Personendaten (z. B. Geschäftsführer, Prokuristen)
* Speichert die Daten in einer SQLite-Datenbank
* Filtert gezielt Unternehmen mit IT-Bezug

## Ziel

Aufbau einer strukturierten Datenbasis zur Analyse der Nachfolgesituation im deutschen IT-Mittelstand, insbesondere basierend auf Altersstrukturen von Geschäftsführern.

## Hinweis

Das Projekt ist Teil einer wissenschaftlichen Arbeit und dient ausschließlich zu Forschungszwecken.
