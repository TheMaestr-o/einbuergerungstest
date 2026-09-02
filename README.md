# Einbürgerungstest — Bogen

Ein Trainer für den deutschen Einbürgerungstest bzw. den Test „Leben in Deutschland“.
Eine einzige HTML-Datei: keine Installation, kein Server, kein Netz nötig — Fragen,
Antworten und alle Bilder stecken in der Datei.

**[index.html](index.html) herunterladen und im Browser öffnen** — oder als GitHub Page ausliefern.

## Was drin ist

* alle **300 bundesweiten** und **160 landesspezifischen** Fragen (Stand des Katalogs: **07.05.2025**)
* die **100 Bilder** des Katalogs (Wappen, Flaggen, Landkarten, Stimmzettel), aus dem
  amtlichen PDF extrahiert
* **Prüfungssimulation**: 33 Fragen (30 bundesweite + 3 aus dem gewählten Bundesland),
  60 Minuten, bestanden ab 17 richtigen Antworten
* **Training nach Themen** mit sofortiger Auflösung, Fehlerspeicher und Wiederholung —
  falsch beantwortete und noch nie gesehene Fragen kommen häufiger dran
* zu **jeder** Frage eine kurze Erklärung auf Russisch, warum genau diese Antwort stimmt
* auf dem Telefon genauso bedienbar wie am Rechner
* Tastatur am Rechner: `1`–`4` antworten, `Enter` weiter; Fortschritt bleibt im Browser gespeichert

## Woher die Daten kommen und wie sie geprüft wurden

Fragetexte, Antwortoptionen und deren Reihenfolge stammen **wörtlich aus dem amtlichen
Gesamtfragenkatalog des BAMF** ([PDF][bamf], Stand 07.05.2025). Dieses PDF enthält keine
Lösungen — die Kästchen vor den Antworten sind alle leer.

Die richtigen Antworten wurden deshalb aus zwei unabhängigen offenen Datensätzen
übernommen und **gegeneinander geprüft**:

| Quelle | Rolle |
| --- | --- |
| [BAMF-Gesamtfragenkatalog (PDF)][bamf] | maßgeblicher Wortlaut von Frage und Optionen |
| [flexsurfer/einburgerungstest][s1] | Lösung, Themenzuordnung |
| [leben-in-deutschland-scrapper][s2] | Lösung, russische Übersetzung |

Der Abgleich läuft über den **Text** der richtigen Antwort, nicht über deren Position —
die beiden Datensätze ordnen die Optionen anders an als das PDF. Ergebnis:

* **457 Fragen**: beide Quellen nennen dieselbe Antwort.
* **3 Fragen** (*Was verbietet das deutsche Grundgesetz?*, Landeshauptstadt von
  Brandenburg und von Hessen): in Quelle 2 ist das Lösungsfeld leer, es zählt Quelle 1.
* **1 Frage** (*Wappen der DDR*): die Quellen widersprechen sich. Entschieden am Bild
  aus dem PDF — Hammer, Zirkel und Ährenkranz ist **Bild 4**.
* **37 Fragen wurden zusätzlich am Bild selbst nachgeprüft**, weil die Nummerierung
  „Bild 1–4“ je nach Quelle anders ausfallen kann: 19 Wappen- und Flaggenfragen,
  16 Landkarten („Welches Bundesland ist …?“), der Stimmzettel und die Besatzungszonen.
  36 bestätigten die Datensätze, eine korrigierte sie (Wappen der DDR).

Bekannte Eigenheit: In Frage 201 steht im amtlichen PDF bei einer *falschen* Antwort
„Niedersachen“ statt „Niedersachsen“. Der Tippfehler ist bewusst nicht korrigiert —
der Text folgt dem Original.

### Erklärungen

Zu jeder der 460 Fragen steht im Feld `why` eine kurze russische Erklärung, warum die
Antwort richtig ist. Die maschinellen „Erklärungen“ aus Quelle 2 waren dafür unbrauchbar:
bei 228 von 458 Fragen steht dort nur der Platzhalter „Важный вопрос для жизни в
Германии“, und die übrigen umschreiben das Thema, statt die Antwort zu begründen. Die
Erklärungen im Repository sind daher neu geschrieben; die 160 Landesfragen folgen zehn
festen Mustern und werden aus einer Tabelle je Bundesland erzeugt.

Die maschinellen Übersetzungen aus Quelle 2 liegen weiterhin in `data/questions.json`,
die App zeigt sie nicht an — geprüft wird ohnehin nur der deutsche Text.

## Neu bauen

```bash
python3 -m venv venv && ./venv/bin/pip install pypdf pillow
curl -Lo katalog.pdf "https://www.bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/gesamtfragenkatalog-lebenindeutschland.pdf?__blob=publicationFile"
python3 build/build_html.py          # data/ + build/app.template.html -> index.html
```

* `data/questions.json` — die 460 Fragen mit Lösung, Thema, Bildern und Übersetzung
* `data/images/` — 100 WebP-Bilder aus dem PDF
* `build/app.template.html` — die App (Platzhalter `__DATA__` / `__IMAGES__`)
* `tools/` — die Aufbereitung: PDF-Text mit Koordinaten lesen, Aufgaben zerlegen,
  Trennfehler des PDFs reparieren, Lösungen abgleichen, Bilder mit ihrer Position
  auf der Seite den Fragen zuordnen

## Rechtliches

Die Fragen und Bilder sind amtliches Material des Bundesamts für Migration und
Flüchtlinge und werden hier unverändert wiedergegeben. Dieses Projekt steht in keiner
Verbindung zum BAMF und ist keine offizielle Prüfungsvorbereitung. Der Code steht unter
der MIT-Lizenz.

[bamf]: https://www.bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/gesamtfragenkatalog-lebenindeutschland.html
[s1]: https://github.com/flexsurfer/einburgerungstest
[s2]: https://github.com/leben-in-deutschland/leben-in-deutschland-scrapper
