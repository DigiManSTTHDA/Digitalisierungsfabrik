# EMMA Studio 2.7 Benutzerhandbuch

# Einführung



# Abstrakt

**EMMA** steht für Empowering Minds, Mastering Automation.  
Innerhalb von **EMMA Studio** können Prozesse erstellt, verwaltet und ausgeführt werden.

[![image.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/scaled-1680-/image.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/image.png)

Unter ***Datei <span class="s1">→ Neu</span>*** kannst du neue [Prozesse](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/prozess "Prozess Übersicht"), [Prozessgruppen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/prozessgruppe "Prozessgruppe"), Queues und [Pläne](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/plan "Plan") erstellen und bearbeiten.  
Die Navigationsleiste auf der linken Seite ermöglicht ein schnelles und einfaches Umschalten zwischen offenen Prozessen, Prozessgruppen, Queues und Plänen sowie den Zugriff auf [Lesen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/lesen-jNv "Lesen (Wahrnehmung UI)"), [Sehen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/sehen "Sehen"), [Hören](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/horen-R21 "Hören (Wahrnehmung UI)") und [Report](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/reports "Reports").

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/wM3image.png)](http://192.168.5.129/uploads/images/gallery/2025-05/wM3image.png)

**Passwörter** Unter *<span class="s1">**Einstellungen → Passwörter**</span>* kannst du gespeicherte Passwörter für verschiedene Systeme verwalten, die in **EMMA Studio** verwendet werden.

**Sprache** <span class="s1">Gehe zu </span>***Einstellungen → Sprache***<span class="s1">, um **EMMA Studio** auf </span>**Englisch**, **Deutsch** oder **Türkisch**<span class="s1"> umzustellen.  
</span>Um die Änderung zu übernehmen, muss das Programm <span class="s2">**neu gestartet**</span> werden.

**Tastenkürzel** Unter *<span class="s1">**Einstellungen → Shortcuts**</span>* kannst du Tastenkombinationen für häufige Aktionen anzeigen und individuell anpassen.

**Graph-Einstellungen** Unter *<span class="s1">**Einstellungen → Graph-Einstellungen**</span>* kannst du festlegen, wie der Graph aussieht und sich verhält.

Folgende Optionen stehen zur Verfügung:

- **Raster anzeigen** (hier lässt sich das Raster ein- oder ausblenden)
- **An Raster ausrichten** (Schritte werden am Raster ausgerichtet)
- **Schrittnamen im Graph anzeigen**
- **Schrittnamen in der Werkzeugleiste anzeigen**

**Hilfe &amp; Kontaktinformationen** Unter *<span class="s1">**Hilfe → Info**</span>* findest du:

- <span class="s1">Links zu </span>**Kontakt**<span class="s1">, </span>**Expertenforum**<span class="s1"> und </span>**Support-Mail**
- Die <span class="s1">**Versionsnummer**</span> deiner **EMMA Studio** Installation

**Statusmeldungen anzeigen** Unter *<span class="s1">**Hilfe → Status**</span>* öffnet sich ein Pop-up-Fenster mit der <span class="s1">**Historie aller Statusmeldungen**</span> in zeitlicher Reihenfolge.

Jede Meldung enthält:

- <span class="s1">**LogLevel:**</span> Bedeutung der Meldung
    
    
    - <span class="s1">**Info**</span> – allgemeine Information über einen Vorgang
    - <span class="s1">**Warning**</span> – ein Problem ist aufgetreten, der Vorgang läuft aber weiter
    - <span class="s1">**Critical**</span> – schwerwiegender Fehler, der Vorgang wird abgebrochen
    - <span class="s1">**Debug**</span> – technische Details für den Support
- <span class="s1">**Zeitstempel:**</span> wann die Meldung erstellt wurde
- <span class="s1">**Prozess:**</span> der Teil des Programms, der die Meldung gesendet hat

# Interaktion mit dem Prozessdiagramm

Zu Automatisierungszwecken wird die Abfolge der Prozessschritte in **EMMA Studio** als Prozessdiagramm strukturiert. Im Folgenden wird beschrieben, wie du effizient durch den Graphen navigieren und ihn mit verschiedenen Werkzeugen und Funktionen der Anwendung verändern kannst.

### Grundlegende Navigation

Klicke auf einen beliebigen Schritt, um ihn auszuwählen. Zur leichteren Identifizierung werden ausgewählte Schritte schwarz hervorgehoben.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/vMximage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/vMximage.png)

### Ein- und auszoomen

Um eine bessere Ansicht des Diagramms zu erhalten oder genauere Details zu sehen, kannst du mit den folgenden Methoden ein- und auszoomen:

**Scrollen mit der Maus:** Halte die STRG-Taste gedrückt und scrolle mit dem Mausrad nach oben, um die Ansicht zu vergrößern. Scrolle nach unten, um herauszuzoomen.  
**Zoom-Schiebeleiste:** Verwende die Zoomleiste in der rechten unteren Ecke des Fensters, um die Zoomstufe anzupassen.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/wHoimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/wHoimage.png)

### Navigation innerhalb des Prozessdiagramms

**Verschieben (Panning):** Durch Verschieben kannst du dich auf der Graph-Oberfläche bewegen, um verschiedene Bereiche anzusehen.

<span class="s1">**Maus ziehen:**</span> Klicke mit der linken Maustaste auf eine beliebige Stelle der Fläche, halte die Taste gedrückt und ziehe die Maus, um die Ansicht zu verschieben.

#### Ausrichten

Wenn dein Graph unübersichtlich wird, kannst du ihn einfach neu ordnen:

<span class="s1">**Ausrichten:**</span> Klicke auf den Button <span class="s1">**Ausrichten**</span> in der Arbeitsleiste (links unten im Editor-Fenster).   
Die Schritte werden automatisch ausgerichtet und übersichtlicher dargestellt.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/mzgimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/mzgimage.png)

#### Prozessdiagramm zentrieren

Wenn du den Graph schnell wieder in die Mitte des Bildschirms holen willst, nutze den **Zentrieren**-Button:

<span class="s1">**Zentrieren:**</span> Klicke auf den Button <span class="s1">**Zentrieren**</span> in der Arbeitsleiste (links unten im Editor-Fenster). Das ist besonders hilfreich, um den gesamten Graphen auf einen Blick zu sehen.

#### Raster anzeigen

Um die Schritte besser ausrichten zu können, kannst du das Gitter einblenden:

<span class="s1">**Raster anzeigen:**</span> Aktiviere die Option <span class="s1">**Raster anzeigen**</span> im Einstellungsfenster, um ein Raster auf der Zeichenfläche darzustellen. So können die Schritte exakt am Raster ausgerichtet werden. Standardmäßig ist diese Option auf <span class="s1">**Ja**</span> gesetzt.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/hpUimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/hpUimage.png)

#### Am Raster ausrichten

Damit der Graph geordnet bleibt, kannst du die Funktion <span class="s1">**Am Raster ausrichten**</span> nutzen:

<span class="s1">**Am Raster ausrichten:**</span> Aktiviere die Option <span class="s1">**Am Raster ausrichten**</span> im Einstellungsfenster. Standardmäßig ist diese Option auf <span class="s1">**Ja**</span> gesetzt. Wenn die Option aktiviert ist, rasten die Schritte beim Verschieben automatisch an den nächstgelegenen Schnittpunkten des Rasters ein.

#### Schrittnamen anzeigen

Für eine bessere Übersicht über die einzelnen Schritte:

<span class="s1">**Schrittnamen anzeigen:**</span> Aktiviere die Option <span class="s1">**Schrittnamen anzeigen** im Einstellungsfenster</span>, damit die Namen direkt auf der Zeichenfläche erscheinen. So erkennst du die Schritte auf einen Blick, ohne sie auswählen zu müssen. Standardmäßig ist diese Option aktiv.

#### Schrittnamen in der Werkzeugleiste anzeigen

Diese Option hilft dir dabei, das passende Schrittsymbol schneller zu finden:

<span class="s1">**Schrittnamen in der Werkzeugleiste anzeigen:**</span> Wenn diese Option aktiviert ist, wird der Name eines Schritts rechts neben dem Symbol in der Werkzeugleiste eingeblendet.

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-10/scaled-1680-/bnvimage.png)](http://192.168.5.129/uploads/images/gallery/2024-10/bnvimage.png)

# Login & Sicherheit

Ein grundlegender Überblick über das Login-System für EMMA Studio

# Login & Sicherheit

Um sicherzustellen, dass nur berechtigte Benutzer Zugang zu sensiblen Daten und Prozessen erhalten, ist eine Anmeldung mit Benutzernamen und Passwort erforderlich. Nach erfolgreicher Anmeldung wählt der Benutzer ein *<span class="s1">**Projekt**</span>* und eine *<span class="s1">**Umgebung**</span>* aus. Über diese Auswahl wird festgelegt, in welchem Kontext der Benutzer arbeitet und welche Prozesse geöffnet werden können.

[![Screenshot 2025-06-10 at 11.47.48.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/screenshot-2025-06-10-at-11-47-48.png)](http://192.168.5.129/uploads/images/gallery/2025-06/screenshot-2025-06-10-at-11-47-48.png)

### Auswahl des Projekts und der Umgebung

Jeder Prozess ist einem bestimmten Projekt und einer bestimmten Umgebung zugeordnet. Prozesse können nur geöffnet werden, wenn der Benutzer mit dem jeweiligen Projekt und der jeweiligen Umgebung verbunden ist.

> Beispiel: Ein Prozess, der im Projekt „Sales“ und der Umgebung „Testing“ gespeichert ist, kann nur geöffnet werden, wenn der Benutzer als Projekt „Sales“ und als Umgebung „Testing“ ausgewählt hat.

Zur Rechtevergabe gibt es zudem die speziellen Platzhalter <span class="s1">**Any-Projekt**</span> und **Any-**<span class="s1">**Umgebung**</span>. Über diese Platzhalter können Administratoren Rechte unabhängig von konkreten Projekten oder Umgebungen zuweisen:

- Ein Benutzer mit Rechten für <span class="s1">Any</span>-Projekt und <span class="s1">Any</span>-Umgebung verfügt über <span class="s2">**alle**</span> Rechte für alle Kombinationen von Projekten und Umgebungen.
- Das bedeutet <span class="s1">**nicht**</span>, dass der Benutzer alle Prozesse sofort öffnen kann. Das Öffnen eines Prozesses setzt voraus, dass der Benutzer mit der exakt passenden Kombination aus Projekt und Umgebung angemeldet ist.

> Beispiel: Ein Benutzer mit <span class="s3">Any-Any</span>-Rechten kann einen Prozess, der in <span class="s3">Any</span>-Projekt aber in der <span class="s3">Testing</span>-Umgebung gespeichert ist, <span class="s1">**nur**</span> öffnen, wenn er sich mit „<span class="s3">Any“</span> als Projekt <span class="s1">**und**</span> „Testing“ als Umgebung anmeldet – nicht mit <span class="s3">Any-Any</span>.

Diese Trennung zwischen <span class="s1">**Rechtevergabe**</span> und <span class="s1">**tatsächlichem Zugriff**</span> verhindert ungewollte Änderungen an Prozessen durch falsch gewählte Kontexte.

### Zugriffsrechte und Rollen

Welche Prozesse, Queues, Pläne oder Objekte ein Benutzer sehen oder bearbeiten kann, hängt von den zugewiesenen Rechten ab. Besitzt der Benutzer z. B. das <span class="s1">**Ansichtsrecht**</span>, werden diese Objekte in der Übersicht angezeigt. Weitere spezielle Rechte sind:

- <span class="s1">**Projekt zuweisen**</span>: Erlaubt die Verwaltung von Objekten in einem Projekt (z. B. das Erstellen oder Bearbeiten von Prozessen).
- <span class="s1">**Entsperren**</span>: Gibt dem Benutzer die Möglichkeit, von anderen Benutzern gesperrte Prozesse zu entsperren.
- <span class="s1">**Löschen**</span>: Erlaubt das Löschen einzelner oder mehrerer Prozesse über das Kontextmenü.

Diese Rechte können in **EMMA Configuration** im Tab **Rollen &amp; Berechtigungen** verwaltet werden.

### Sperren &amp; Entsperren

Sobald ein Benutzer einen Prozess öffnet und bearbeitet, wird dieser automatisch für andere Benutzer <span class="s1">**gesperrt**</span>. Die Sperre verhindert eine gleichzeitige Bearbeitung und dient als Schutz vor Datenverlusten oder Inkonsistenzen.

Ein gesperrter Prozess ist damit gewissermaßen <span class="s1">**reserviert**</span> für den aktuell bearbeitenden Benutzer. Will ein anderer Benutzer diesen Prozess bearbeiten, muss dieser über das <span class="s1">**Recht zum Entsperren**</span> verfügen. Erst dann kann der Benutzer die Sperre aufheben und den Prozess selbst bearbeiten.

### Erweiterte Konfiguration

<span lang="DE">In den folgenden Schritten werden die Eingabemasken und Einstellmöglichkeiten für Benutzer erklärt. Detaillierte Erläuterungen wie die Einrichtung von Benutzerrollen und -rechten sowie von Projekten und Umgebungen werden speziell für Administratoren im **EMMA Administration Guide** beschrieben. Für weitere Fragen zum Rechte- und Rollenmodell hinter den verschiedenen Projekten und Umgebungen wendest du dich am besten an den für **EMMA Studio** zuständigen Administrator in deinem Unternehmen.</span>

# Konfiguration der Datenbankverbindung

Das Fenster zur Konfiguration der Datenbank erscheint automatisch beim ersten Start von **EMMA Studio**. Die Datenbankeinstellungen können jederzeit über den Menüpunkt ***Einstellungen → DB Connection*** angepasst werden (siehe 4.1.3.2).

[![Screenshot 2025-08-07 at 09.57.01.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2025-08/scaled-1680-/3Gpscreenshot-2025-08-07-at-09-57-01.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2025-08/3Gpscreenshot-2025-08-07-at-09-57-01.png)

##### Server

Name des Servers

##### Database

Name der Datenbank

##### Use Domain Account

Authentifizierung über die Windows-Domain, falls aktiviert.  
Wenn diese Option aktiviert ist, wird der bei Microsoft Windows angemeldete Benutzer zur Anmeldung in der Datenbank verwendet.

Andernfalls erfolgt die Anmeldung mit dem Username und Password aus der Eingabemaske.

##### Username

Benutzername

##### Password

Passwort

##### Trusted Connection

„Yes“ oder „No“: Diese Optionen haben keine Auswirkung mehr und werden in künftigen Versionen entfernt.

##### Integrated Security

„Yes“ oder „No“:

Bei „Yes“ wird der bei Microsoft Windows angemeldete Benutzer zur Anmeldung in der Datenbank verwendet. Der Benutzername muss hierfür eingegeben werden, das Passwort kann jedoch leer bleiben. Dies funktioniert nur, wenn der verwendete Computer Mitglied einer Active Directory Domain ist.

Bei „No“ erfolgt die Anmeldung mit dem Username und Password aus der Eingabemaske.


##### Connection Timeout

Zeit in Sekunden, bis ein Verbindungsfehler mit der Datenbank erkannt wird.

##### Verlängerter Timeout

Connection Timeout nur für Reportabfragen.

# Benutzer-Login

<span lang="DE">Das Login-Fenster erscheint, wenn **EMMA Studio** zum ersten Mal gestartet wird. Die Login-Einstellungen können zu einem späteren Zeitpunkt über den Menüpunkt ***Einstellungen → Login*** angepasst werden (siehe </span><span lang="DE">4.1.3.1</span><span lang="DE">).</span>

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/b7oimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/b7oimage.png)

<span lang="DE">Bild 6 – Benutzer-Login </span>

### <span lang="DE">Eingabefelder – Dialogfenster „</span><span lang="DE">Login</span><span lang="DE"> Benutzer“</span><span lang="DE">:</span>

##### <span lang="DE">Benutzername</span>

<span lang="DE">Benutzername</span>

##### <span lang="DE">Passwort</span>

<span lang="DE">Passwort</span>

##### <span lang="DE">Projekt/Umgebung</span>

<span lang="DE">Das Projekt und die Umgebung, in dem bzw. der der Benutzer während dieser Sitzung arbeiten möchte.</span>

##### <span lang="DE">auto login</span>

<span lang="DE">**EMMA Studio** meldet sich beim nächsten Start automatisch mit diesen Anmeldedaten an. </span>

<p class="callout info"><span lang="DE">ACHTUNG: Die nächste Anmeldung von **EMMA Service** erfolgt ebenfalls über </span><span lang="DE">denselben Account.</span></p>

# Login-Dialog

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/ueFimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/ueFimage.png)

  
Sowohl der Menüpunkt ***Einstellungen <span lang="DE">→</span> Login*** als auch das **Login**-Symbol können verwendet werden, um eine neue Sitzung mit einem anderen Benutzer, einem anderen Projekt oder einer anderen Umgebung zu starten. Zudem kann ein Benutzer an dieser Stelle sein ***Passwort ändern***.

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/9oyimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/9oyimage.png)

### DB Connection

<span lang="DE">Es öffnet sich derselbe Bildschirm wie bei der Eingabe der [Datenbankverbindungs­einstellungen](http://192.168.5.129/link/63#bkmrk-page-title) beim ersten Start von **EMMA Studio**.</span>

# Automatischer Login & gespeicherte Zugangsdaten

Für den unbeaufsichtigten Einsatz von **<span class="s1">EMMA Studio</span>** – etwa beim automatischen Start über **EMMA Service** zur Ausführung geplanter Prozesse – können sowohl der <span class="s1">**Benutzer-Login**</span> als auch die <span class="s1">**Datenbankverbindung**</span> so konfiguriert werden, dass gespeicherte Zugangsdaten für den <span class="s1">**automatischen Login**</span> verwendet werden.

**EMMA Studio** und der zugehörige **<span class="s1">EMMA Service</span>** unterstützen die automatische Anmeldung und verwenden dieselben Anmeldedateien.

---

### Benutzer-Login: Verhalten beim Auto-Login

Wird beim Login das Kontrollkästchen *<span class="s1">**Auto-Login**</span>* aktiviert, werden sowohl Username und Password als auch die ausgewählte Kombination aus Projekt und Umgebung in einer verschlüsselten Anmeldedatei auf dem lokalen Rechner gespeichert.

Beim nächsten Start von **EMMA Studio** wird der Benutzer automatisch angemeldet, sofern sich diese Datei an einem der definierten Speicherorte befindet (siehe unten), und eine Verbindung mit dem gespeicherten Projekt und der gespeicherten Umgebung hergestellt.

Nach dem Login kann der Benutzer <span class="s1">**jederzeit das Projekt oder die Umgebung wechseln**</span>, ohne das Passwort erneut eingeben zu müssen.

---

### Datenbank-Login: Verhalten beim Auto-Login

Auch der Datenbank-Login kann für den automatischen Verbindungsaufbau konfiguriert werden. Wenn eine gültige Konfigurationsdatei vorhanden ist, stellt **EMMA Studio** beim Start automatisch die Verbindung zur Datenbank her – ganz ohne Benutzereingabe.

---

### Speicherorte für Anmeldedateien

Es gibt <span class="s1">**zwei mögliche Speicherorte**</span> für die Anmeldedateien (sowohl für Benutzer als auch für die Datenbank):

- **Benutzerspezifisch:**
    
    Im Ordner <span class="s1">**AppData** </span>des angemeldeten Benutzers (jeder Benutzer kann eigene Zugangsdaten speichern)
    
    > C:\\Users\\<span class="s2">username</span>\\AppData\\Roaming\\OTTRobotics\\EMMA Studio\\Config
- **Systemweit:**
    
    Im Ordner <span class="s1">**C:\\Programme**</span> (für alle Benutzer auf dem System verfügbar)
    
    > C:\\Programme\\OTTRobotics\\Emma Studio\\Config

Der automatische Login wird ausgelöst, wenn die jeweiligen Dateien vorhanden sind:

- <span class="s1">**Anmeldedatei für Benutzer-Login:** ucon.conf</span>
    - für die automatische Benutzeranmeldung

- <span class="s1">**Datenbank-Konfigurationsdatei:** d</span><span class="s1">bcon.conf</span>
    
    
    - für den automatischen Verbindungsaufbau mit der Datenbank

---

### Gemeinsame Nutzung in Studio &amp; Service

Sowohl **<span class="s1">EMMA Studio</span>** als auch der **<span class="s1">EMMA Service</span>** greifen auf dieselben gespeicherten Anmeldedateien zurück.

Wenn der **<span class="s1">EMMA Service</span>** zum ersten Mal mit diesen Dateien gestartet wird, werden sowohl der Dialog für den Benutzer-Login als auch für den Datenbank-Login angezeigt – jedoch mit bereits vorausgefüllten Feldern. Die Anmeldung muss in diesem Fall <span class="s1">**einmalig manuell bestätigt**</span> werden.

Nach dieser <span class="s1">**ersten Bestätigung**</span> meldet sich der **EMMA Service** bei künftigen Starts <span class="s1">**vollautomatisch ohne weitere Benutzerinteraktion**</span> an.

---

### Typisches Anwendungsszenario

Ein gängiges Setup könnte wie folgt aussehen:

- Die Anmeldedatei für den <span class="s1">**Benutzer-Login** </span>liegt im Ordner <span class="s1">**AppData**</span> → benutzerspezifisch
- Die <span class="s1">**Datenbank-Konfigurationsdatei**</span> liegt im Ordner <span class="s1">**C:\\Programme**</span> → für alle Benutzer verfügbar

So können einzelne Benutzer **EMMA Studio** mit ihren persönlichen Zugangsdaten starten, während gleichzeitig ein zentraler Datenbankzugang für alle Benutzer zur Verfügung steht.

# Passwortverwaltung

Verwalten von Passwörtern innerhalb von EMMA Studio

# Passwort-Tresor

Der **Passwort-Tresor** wird über das Menü ***Einstellungen <span lang="DE">→</span> Passwörter*** geöffnet.

Der Zweck des Passwort-Tresors ist eine zentrale, geschützte Speicherung von Passwörtern durch einen Benutzer. Anschließend kann mit den gespeicherten Passwörtern über die [Variable](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/variablen-und-deren-nutzung "Variablen und deren Nutzung") des Typs „Passwort“ gearbeitet werden.

Passwörter sind nur für den aktuellen Benutzer und innerhalb des Projekts bzw. der Umgebung gültig, in dem/der sie erstellt wurden.  
Dadurch kann derselbe Prozess immer das Passwort eingeben, welches ein Benutzer für die aktuelle Umgebung hinterlegt hat.

Passwörter werden von **EMMA Studio** sicher gespeichert und können ausschließlich von dem Benutzer gelesen werden, der sie erstellt hat. Auch über die entsprechenden Befehle im Prozessschritt ***Tippen*** können die Passwörter nicht gelesen werden. Sie können dort lediglich verwendet werden, um direkt in eine Anwendung, beispielweise ein Passwortfeld, eingefügt zu werden.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/MSGimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/MSGimage.png)

### <span lang="DE">Buttons/Eingabefelder</span>

##### <span lang="DE">Ändern</span>

<span lang="DE">Ruft die Bereichsauswahl auf, über die das Projekt bzw. die Umgebung festgelegt wird, in dem/der das entsprechende Passwort verwendet wird.</span>

##### <span lang="DE">Neues Passwort hinzufügen</span>

<span lang="DE">Mit einem Klick auf diesen Button werden die Eingabefelder **Passwortname**, **Passwort** und **Passwort bestätigen** für die Erstellung eines Passworts freigegeben.</span>

##### Passwortname

<span lang="DE">Benennung des Passworts, z. B. Name der Software oder der Website, zu der das Passwort gehört, um es innerhalb von **EMMA Studio** erkennen und zuordnen zu können, z. B. wenn es als Variable verwendet wird.</span>

##### Passwort

<span lang="DE">Eingabe des Passworts, das auf der Website oder innerhalb der Software verwendet wird, für die ein Prozess automatisiert werden soll. Die Länge ist auf 255 Zeichen begrenzt und Sonderzeichen können ohne Einschränkungen direkt eingegeben werden (in früheren Versionen mussten Sonderzeichen in {} eingegeben werden, z. B. {#}).  
</span>

##### Passwort bestätigen

Bestätigung des Passworts.

##### Löschen

<span lang="DE">Wenn auf ein bereits erstelltes Passwort geklickt wird, wird es orange markiert. Anschließend kann dieses Passwort durch Klick auf **Löschen** gelöscht werden.</span>

##### Speichern

<span lang="DE">Nachdem ein neues Passwort eingegeben wurde, muss es über den Button **Speichern** gespeichert werden. Es erscheint anschließend in der Liste.</span>

# Verwendung gespeicherter Passwörter in einem Prozess

Wenn ein Passwort wie im Abschnitt [Passwort-Tresor](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/passwort-tresor "Passwort-Tresor") beschrieben hinterlegt wurde, kann dieses einer Variablen vom Typ „Passwort“ zugewiesen und verwendet werden.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/1nGimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/1nGimage.png)

Zu diesem Zweck muss der Variablen zunächst ein **Name** zugewiesen werden. Der Name kann mit dem Namen des Passworts aus dem Passwort-Tresor identisch sein. Anschließend muss der Typ der Variablen auf „Passwort“ gesetzt werden, bevor ein Eintrag im Feld **Wert** vorgenommen wird. Erst dann erscheint nach Eingabe des ersten Buchstabens des Passwortnamens aus dem Passwort-Tresor im Feld **Wert** eine Drop-down-Liste, aus der das gewünschte Passwort ausgewählt werden kann.

[![oo3image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/u85oo3image.png)](http://192.168.5.129/uploads/images/gallery/2025-05/u85oo3image.png)

Nach dem Anlegen der Variablen vom Typ „Passwort“ wird die korrekte Verknüpfung mit dem Passwort aus dem Passwort-Tresor durch einen grünen Hintergrund angezeigt. Liegt ein Problem mit dem Passwort vor, z. B. weil der Administrator das Master-Passwort zurückgesetzt hat oder weil im Passwort-Tresor kein Passwort zu dem Namen gefunden wurde, wird die Zeile rot hervorgehoben.

Wie bei allen Variablen können auch auf Variablen vom Typ „Passwort“ bestimmte Operatoren angewendet werden (siehe Kapitel [Variablen und deren Nutzung](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/variablen-und-deren-nutzung "Variablen und deren Nutzung")). So kann z. B. eine Variable vom Typ „Passwort“, die für Anmeldungen verwendet wird, innerhalb eines Prozesses überschrieben werden, wenn sich innerhalb des Prozesses das Konto oder die Website ändert, für die eine Anmeldung erforderlich ist.

Wenn Operatoren auf Variablen vom Typ „Passwort“ angewendet werden, wirken sie sich nicht auf das Passwort selbst aus, sondern darauf, mit welchem Passwort die Variable verknüpft ist.   
Die Änderung des Passworts in der Passwort-Variable ist damit temporär und ändert nicht das Passwort im Passwort-Tresor.

Nehmen wir zum Beispiel an, dass der Benutzer zwei Passwörter im Passwort-Tresor hat:   
Twitter, das den Wert „Password“ speichert.  
Twitter2, das den Wert „SecurePassword“ speichert.   
Wenn eine Passwort-Variable den Wert „Twitter“ speichert und dann durch Variablenmanipulation der Wert in „Twitter2“ geändert wird, würde bei der nächsten Verwendung der Passwort-Variable der Text „SecurePassword“ eingegeben werden.

# Begrifflichkeiten

Standardbegriffe und Definitionen, die im Handbuch verwendet werden.

# Objekt

**EMMA Studio** kann Objekte auf dem Bildschirm oder in Dokumenten bzw. Bildern erkennen, indem diese mit den in der Datenbank gespeicherten Beispielen verglichen werden. Diese Beispiele heißen in **EMMA Studio** *Objekte* und werden unter der Rubrik ***Sehen*** erstellt. Die Objekte bestehen im Wesentlichen aus drei Teilen:

#### <span lang="DE">Kontur</span>

<span lang="DE">Kantendefinition des Suchobjekts  
</span><span lang="DE">Linien, die die Grenzen eines Objekts markieren  
Trägt zur Erkennung und Unterscheidung von Formen bei</span>

#### <span lang="DE">Bild</span>

<span lang="DE">Ausschnitt des Originalbilds</span>

#### <span lang="DE">Region</span>

<span lang="DE">Definition des Ausschnitts</span>

<span lang="DE">*Objekt* und *Bild* beschreiben dabei das zu suchende Objekt und stehen für die tatsächliche Suche im ***Finden***-Schritt zur Auswahl. Anhand des folgenden Beispiels soll der grundlegende Unterschied zwischen *Objekt* und *Bild* erläutert werden:</span>

<span lang="DE">Man erstellt ein Objekt mit einer leeren Checkbox. Wenn nun bei der Suche das *Objekt* (also nur die Formkontur) dieser Checkbox benutzt wird, findet **EMMA** eine Checkbox sowohl mit als auch ohne Häkchen. Sucht man stattdessen nach dem *Bild*, so wird nur eine Checkbox ohne Häkchen gefunden. Bei dem Formmuster wird die Übereinstimmung bzw. das Vorhandensein der Kontur des Objekts überprüft. Diese wird durch das Hinzufügen eines Häkchens nicht verändert. Beim *Bild* hingegen muss das Objekt pixel- und farbgetreu wiedererkannt werden.</span>

<span lang="DE">Weitere Details zur Erstellung eines *Objekts* sind im Abschnitt </span>[<span lang="DE">Sehen</span>](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/sehen "Sehen")<span lang="DE"> und zur Suche im Abschnitt </span>[<span lang="DE">Finden</span>](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/finden "Finden")<span lang="DE"> enthalten.</span>

# Variablen

**Variablen** sind wie Container und enthalten Informationen, die während der Ausführung eines Prozesses benötigt werden. Sie dienen zur temporären Speicherung von Daten, beispielsweise Benutzerdaten oder Einstellungen, die in mehreren Teilen des Prozesses verwendet werden können.

Eine Variable kann nur in dem Prozess verwendet werden, in dem sie erstellt wurde. Der Wert einer Variable lässt sich jedoch an über- oder untergeordnete Prozesse weitergeben. Dafür wird im über- oder untergeordneten Prozess eine Variable mit demselben Namen und Typ angelegt. In der Schnittstellendefinition wird dann festgelegt, in welche Richtung der Wert übertragen werden soll.  
<span lang="DE">Wird z. B. in einem Prozess eine Variable mit dem Namen „Anzahl“ und dem Typ „Dezimal“ verwendet, wird der Wert dieser Variable automatisch von einem Unterprozess mit derselben definierten Variable übertragen.  
Wenn der Unterprozess den Wert dieser Variable ändert, wird dieser nach Abschluss des Unterprozesses wieder an den aufrufenden Prozess übergeben.</span>

<span lang="DE">Variablen können zwischen Schritten oder Prozessen kopiert werden. Dazu eine oder mehrere Variablen auswählen und im Variablen-Management per Rechtsklick in den nächsten Prozess kopieren.</span>

[![c6df1dd0-689a-4470-ba3d-d83487cabd4a.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/c6df1dd0-689a-4470-ba3d-d83487cabd4a.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/c6df1dd0-689a-4470-ba3d-d83487cabd4a.png)  
  
<span lang="DE">Eine Variable wird immer durch einen bestimmten, im Folgenden aufgelisteten Datentyp definiert:</span>

#### Boolean

<div id="bkmrk-wahr-oder-falsch">Wahr oder Falsch</div>#### Ganzzahl

<div id="bkmrk-ein-zahl-ohne-kommas">Zahl ohne Kommastellen</div>#### Dezimalzahl

<div id="bkmrk-ein-zahl-mit-kommast">Zahl mit Kommastellen</div>#### Text

<div id="bkmrk-beliebige-zeichen-bu">Abfolge aus beliebigen Zeichen inkl. Buchstaben, Zahlen und Sonderzeichen</div>#### Datum&amp;Uhrzeit

Zeitangabe, z. B. 1. September 2022 7:05:32

#### Timer

<div id="bkmrk-kann-die-dauer-eines">Messung der Prozessdauer durch Verwendung der Operatoren „Start“ und „Stop“</div>#### Passwort

<div id="bkmrk-passw%C3%B6rter-k%C3%B6nnen-im">Passwörter können im [Passwort-Tresor](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/passwort-tresor "Passwort-Tresor") hinterlegt und dann in einer Variable vom Typ „Passwort“ genutzt werden. Prozesse, für die eine sichere Anmeldung erforderlich ist, können auf diese Weise erstellt werden, ohne dass das Passwort einem für den Prozess zuständigen Mitarbeitenden mitgeteilt werden muss. Ein über den Passwort-Tresor erstelltes Passwort kann über eine Variable lediglich verwendet, aber nicht ausgelesen werden.</div><span lang="DE">Sobald der Datentyp zum ersten Mal definiert wurde, kann er nicht mehr geändert werden. Manipulationen an Variablen hängen von diesem Datentyp ab (siehe [Variablen und deren Nutzung](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/variablen-und-deren-nutzung "Variablen und deren Nutzung")). Eine Variable kann für Berichte markiert werden. Diese Variable wird dann in den druckbaren Berichten in den Eigenschaften eines Prozesses aufgelistet.</span>

# Wahrnehmung

Überblick über die Möglichkeiten der Wahrnehmung im User Interface.

# Sehen

[![image.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/scaled-1680-/3ayimage.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/3ayimage.png)

Der Bereich ***Sehen*** lässt sich über die Menüleiste auf der linken Seite öffnen (Unterpunkt ***Wahrnehmung***). Wie bereits zu Beginn von Kapitel 4 beschrieben, basiert ein Teil der Suche in **EMMA Studio** auf Objekt-/Bildvergleichen. Das heißt, dass ein zu suchendes Element als Objekt/Bild in der Datenbank vorhanden sein muss, um es in der Prozesserstellung bzw. zur Laufzeit verwenden zu können. Im Bereich ***Sehen*** lassen sich die entsprechenden Objekte erstellen, bearbeiten und auch löschen.

<span lang="DE">Erläuterung des Begriffs *Objekt* siehe Kapitel </span><span lang="DE">4.3.1.</span>

Für die allgemeine Steuerung stehen in der Menüleiste die folgenden Buttons zur Verfügung:

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/1FKimage.png)](http://192.168.5.129/uploads/images/gallery/2025-06/1FKimage.png)

#### Quelle 

<span lang="DE">Hier kannst du auswählen, ob das Bild via Screenshot erstellt oder von der Festplatte geladen werden soll.</span>

#### <span lang="DE">Neu [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/bQhimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/bQhimage.png)</span>

<span lang="DE">Erstellt einen Screenshot.</span>

#### <span lang="DE">Delay (Verzögerung)</span>

<span lang="DE">Hier kannst du festlegen, mit welcher Verzögerung ein Screenshot erstellt wird.   
Die Optionen sind:</span>

- <span lang="DE">Keine Verzögerung</span>
- <span lang="DE">3 Sekunden</span>
- <span lang="DE">5 Sekunden</span>
- <span lang="DE">10 Sekunden</span>

#### <span lang="DE">Öffnen [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/BtQimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/BtQimage.png)</span>

<span lang="DE">Öffnet ein Bild aus einem auszuwählenden Ordner (weitere Details siehe Kapitel 4.5.2).</span>

#### <span lang="DE">Speichern [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/D2vimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/D2vimage.png)</span>

<span lang="DE">Speichert das aktuelle Bild bzw. Objekt in der Datenbank und macht es damit im Prozess verfügbar.</span>

#### <span lang="DE">Hilfe </span>![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719578821812.png)

<span lang="DE">Öffnet das **EMMA Studio Handbuch**.</span>

#### Zurücksetzen [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/TYzimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/TYzimage.png)

<span lang="DE">Verwirft den letzten Screenshot und die bereits erfolgten Einträge unter Bildeigenschaften auf der rechten Seite.</span>

#### Einstellungen

<span lang="DE">Öffnet das Fenster für allgemeine Einstellungen, wie Graph-Einstellungen, Shortcuts und Sprache.</span>

### <span lang="DE">Aufteilung der Seite</span>

<span lang="DE">Der Bereich ***Sehen*** ist im Tab **Neues Objekt** in zwei Hauptbereiche unterteilt: links befindet sich die Bildquelle, rechts der Bearbeitungsbereich der Objekte.</span>

<span lang="DE">Über die Schaltfläche ***Neu*** kannst du ein Bild von deinem PC aufnehmen. **EMMA Studio** minimiert sich selbst und erstellt einen Screenshot des Bildschirms.</span>

#### <span lang="DE">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/2G6image.png)](http://192.168.5.129/uploads/images/gallery/2025-06/2G6image.png)Linker Bereich – Bildaufnahme</span>

<span lang="DE">Im linken Bereich kann mithilfe der STRG-Taste und der linken Maustaste navigiert werden. Halte die STRG-Taste gedrückt und drehe das Scrollrad, um innerhalb dieses Bildschirmausschnitts ein- und auszuzoomen.</span>

<span lang="DE">**Objekt erstellen:** Klicke und ziehe mit der linken Maustaste ein Rechteck um den gewünschten Bereich. Der gewünschte Bereich wird mit der ausgewählten Farbe markiert. </span>

<span lang="DE">**Objekt bewegen:** Das Rechteck kann bewegt werden, indem man darauf klickt und es per Drag &amp; Drop an den gewünschten Ort zieht. </span>

<span lang="DE">Wähle mit der Liste am unteren Bildschirmrand die **Farbe der Auswahl** für das Markierungsrechteck. Dies ermöglicht eine bessere visuelle Unterscheidung bei Mehrfachauswahl.</span>

<span lang="DE">Mit dem Pfeil (</span>[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/VdLimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/VdLimage.png)<span lang="DE">) in der Mitte übernimmt man den gewählten Ausschnitt der Bildquelle in den Bearbeitungsbereich. </span><span lang="DE">Alternativ kann über den Tab **Objekt öffnen** ein bereits gespeichertes Objekt über einen Doppelklick oder einfaches Anklicken mit anschließendem Klick auf den Pfeil ([![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/VdLimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/VdLimage.png)</span><span lang="DE">) in den Bearbeitungsbereich übernommen werden.</span>

#### <span lang="DE">Rechter Bereich – Objektbearbeitung</span>

<span lang="DE">Die rechte Seite des Fensters dient zur Bearbeitung des Objekts. Dieser Bereich ist in drei Teile unterteilt: Bildausschnitt, Konfiguration und Eigenschaften.</span>

<span lang="DE">Im oberen Feld ist das umrahmte Objekt bzw. die Formkontur (aus dem linken Bildschirm übernommen) vergrößert zu sehen. Die grünen Markierungen stellen die von **EMMA** gefundenen Objektstrukturen visuell dar. Die Konturfarbe kann im unteren Bereich unter ***Konfiguration* –** ***Konturfarbe*** geändert werden.</span>

<span lang="DE">Im Ausschnitt sind eine blaue horizontale und eine vertikale Linie zu sehen, deren Schnittpunkt durch Verschieben der Linien verändert werden kann. Der Schnittpunkt ist das vom Schritt ***Finden*** gelieferte Ergebnis und ist bei Click- und Touch-Prozessschritten wichtig, da der Klick von **EMMA** exakt an der Stelle des Schnittpunkts („Fadenkreuz“) getätigt wird.   
Damit ist der Schnittpunkt bei Verwendung des Objekts der gewünschte **Klickpunkt**.</span>

<span lang="DE">Die orangefarbene Doppellinie in der Mitte des Bildschirms kann horizontal bewegt werden, sodass die beiden Bildflächen links und rechts vergrößert oder verkleinert werden können. Folgende Parameter sind im Bereich ***Konfiguration*** relevant.</span>

#### <span lang="DE">Objekteigenschaften</span>

<span lang="DE">In den **Eigenschaften** wird das Feld **ID** automatisch nach dem Speichern des Objekts befüllt.   
Der **Name** des Objekts wird darunter vergeben.  
Bereits verwendete Namen werden im Bereich darunter angezeigt, wobei sich die Anzeige automatisch je nach den bereits eingetragenen Buchstaben im Feld **Name** ändert.</span>

<span lang="DE">Jedem Objekt können ein oder mehrere **Tags** zugewiesen werden. Diese **Tags** werden in **EMMA Configuration** (**Bild &amp; Sound Tags**) angelegt.</span>

<span lang="DE">Im Bereich **Konfiguration** sind die Anpassungen dargestellt, die an dem oben angezeigten Objekt vorgenommen werden.  
Bei der **Konturfarbe** kann aus dem Drop-down-Menü *grün*, *rot*, *blau*, *weiß*, *schwarz* oder *None* (keine Konturfarbe) gewählt werden.</span>

<span lang="DE">Die **Obere Tiefenschärfe** sowie die **Untere Tiefenschärfe** können über den Schieberegler eingestellt werden. Mit diesen Einstellungen kann die Objektkontur angepasst werden.   
</span><span lang="DE">Über den Kontrastwert werden die Kanten bzw. Ränder des ausgewählten Bilds erfasst, wodurch dieses als Objekt abgespeichert werden kann. Normalerweise werden über die Standardwerte sehr gute Ergebnisse erzielt. Sollten Anpassungen erforderlich sein, wird folgende Vorgehensweise empfohlen:</span>

1. <span lang="DE">Den Regler für **Obere Tiefenschärfe** auf 1000 und für **Untere Tiefenschärfe** auf 0 einstellen.</span>
2. <span lang="DE">Den Regler für **Obere Tiefenschärfe** so lange nach links ziehen, bis alle gewünschten Kanten bzw. Pixel markiert sind.</span>
3. <span lang="DE">Den Regler für **Untere Tiefenschärfe** nur bis zu der Stelle nach rechts ziehen, bei der die ersten Kanten bzw. Pixel gerade noch nicht verschwinden.  
    </span>· <span lang="DE">Obere Tiefenschärfe Standardwert: 200  
    · Untere Tiefenschärfe Standardwert: 50  
    </span>· <span lang="DE">Werteliste: \[0 bis 1000, ganzzahlig\]</span>

#### <span lang="DE">Eigenschaften</span>

<span lang="DE">In einige wenige Felder müssen Werte eingetragen werden, die restlichen werden vom System ausgefüllt.</span>

##### <span lang="DE">ID</span>

<span lang="DE">Die eindeutige ID eines Objekts. Dieser Wert wird automatisch gesetzt. Wenn der Wert nicht gesetzt ist, wird das aktuell bearbeitete Bild als neues Objekt gespeichert.</span>

##### <span lang="DE">Name</span>

<span lang="DE">Der Benutzer definiert einen eindeutigen Namen. Ob der eingetragene Name bereits besetzt ist, wird im Feld darunter (**Benutzte Namen**) angezeigt.</span>

##### <span lang="DE">Benutz</span><span lang="DE">te </span><span lang="DE">Namen</span>

<span lang="DE">Anzeige bereits verwendeter Bezeichnungen zur Vereinfachung der Namensfindung.</span>

##### <span lang="DE">Global verfügbar</span>

<span lang="DE">Wenn das Kontrollkästchen aktiviert ist, steht das Objekt nicht nur in der Umgebung des aktuell bearbeiteten Projekts zur Verfügung, sondern auch in derselben Umgebung in anderen Projekten.</span>

##### <span lang="DE">Tags</span>

<span lang="DE">Auswahl der Tags, die einem Objekt zugeordnet werden sollen. Die verfügbaren Tags können in **EMMA Configuration** individuell definiert werden.</span>

##### <span lang="DE">Benutzt in Prozess</span>

<span lang="DE">Anzeige aller Prozesse und der zugehörigen Prozessschritte, in denen das aktuelle Objekt verwendet wird. Mit dem darunterliegenden Button ***Objekt* *löschen*** kann ein Objekt gelöscht werden – sofern dieses in keinem Prozess verwendet wird.</span>

### <span lang="DE">Erstellen eines Objekts von einer Bildschirmaufnahme</span>

<span lang="DE">Zur Erstellung eines Objekts sind die folgenden Schritte durchzuführen:</span>

1. <span lang="DE">Gehe zu ***Wahrnehmung – Sehen***.</span>
2. <span lang="DE">Erstelle ein neues Bildschirmbild über den Button ***Neu*** in der Menüleiste.</span>
3. <span lang="DE">Navigiere über STRG + linke Maustaste.</span>
4. <span lang="DE">Markiere den Objektbereich mit der linken Maustaste.</span>
5. <span lang="DE">Übertrage das Objekt über den Pfeil in der Mitte in das Feld auf der rechten Seite.</span>
6. <span lang="DE">Prüfe, ob die Objektkontur in Ordnung ist und passe diese ggf. über die Regler **Obere Tiefenschärfe** und **Untere Tiefenschärfe** an.</span>
7. <span lang="DE">Gib dem Objekt einen Namen und optional Tags.</span>
8. <span lang="DE">Speichere das Objekt über den Menübutton ***Speichern*** oder STRG+S.</span>
9. <span lang="DE">Bestätige das Fenster mit der Objekt-ID mittels OK.</span>

<span lang="DE">Das erstellte Objekt steht nun über den Objektnamen oder die Objekt ID im Prozess zur Verfügung.</span>

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/eO0image.png)](http://192.168.5.129/uploads/images/gallery/2024-06/eO0image.png)

### <span lang="DE">Suchen und Bearbeiten des Objekts</span>

<span lang="DE">Um ein Objekt/Bild aus der Liste gespeicherter Objekte zu laden, wählt man die Datei über den Tab **Objekt öffnen** aus.</span>

<span lang="DE"> </span>[![image.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/V2Bimage.png)](http://192.168.5.129/uploads/images/gallery/2024-06/V2Bimage.png)

<span lang="DE">Nach Auswahl des Tabs **Objekt öffnen** auf der linken Seite </span><span lang="DE">können im Bereich **Suchkriterien** die auswählbaren Bilder durch die Eingabe von Tags gefiltert werden. Über das Textfeld **Name** kann eine Suche durchgeführt werden.   
Die Suche wird über die ENTER-Taste gestartet und kann erst nach Eingabe von mindestens drei Zeichen ausgeführt werden. Die Suche kann dabei auf den Objektnamen oder die zugehörige ID angewendet werden.</span>

<span lang="DE">Im unteren Bereich **Bilder** stehen die entsprechenden Bilder zur Auswahl. Das jeweilige Objekt wird über folgende Werte definiert:</span>

##### <span lang="DE">ID</span>

<span lang="DE">ID des Objekts</span>

##### <span lang="DE">Name</span>

<span lang="DE">Name des Objekts</span>

##### <span lang="DE">Durchschnittlicher Score</span>

<span lang="DE">Durchschnittliche Trefferquote, mit der **EMMA** das entsprechende Objekt in einem Prozess identifiziert. Wenn das Objekt noch nicht gefunden wurde, liegt der Score bei 0,000.</span>

##### <span lang="DE">Fehler Zähler</span>

<span lang="DE">Anzahl der Suchvorgänge, bei denen das Objekt nicht gefunden wurde. Dieser Wert ist mit Vorsicht zu genießen, weil ein Prozess auch so angelegt werden kann, dass ein bestimmtes Objekt nicht gefunden werden darf.</span>

##### <span lang="DE">Project</span>

<span lang="DE">Projekt/e, in dem/denen das Objekt verfügbar ist</span>

##### <span lang="DE">Environment</span>

<span lang="DE">Umgebung/en, in der/denen das Objekt verfügbar ist</span>

##### <span lang="DE">Owner</span>

<span lang="DE">**EMMA**-Benutzer, der das Objekt angelegt hat.</span>

##### <span lang="DE">Erstellungsdatum</span>

<span lang="DE">Datum der Erstellung</span>

##### <span lang="DE">Änderungsdatum</span>

<span lang="DE">Datum der letzten Änderung</span>

##### <span lang="DE">Pixel</span>

<span lang="DE">Maße des Objekts</span>

##### <span lang="DE">PPM</span>

<span lang="DE">Pixel-pro-Millimeter-Faktor</span>

##### <span lang="DE">Quelle</span>

<span lang="DE">Bildquelle</span>

<span lang="DE">Durch Klick auf die Pfeiltaste (</span>[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/m92image.png)](http://192.168.5.129/uploads/images/gallery/2024-05/m92image.png)<span lang="DE">) in der Mitte des Programmfensters bzw. durch Doppelklick auf den entsprechenden Eintrag wird das Bild in den Arbeitsbereich übernommen. Weitere Bearbeitungsschritte sind analog zu Kapitel </span><span lang="DE">4.5.1</span><span lang="DE">. Zu beachten ist, dass das entsprechende Objekt bei einem Speichervorgang überschrieben wird, sofern ein Eintrag im ID-Feld vorhanden ist.</span>

# Lesen

[![Wahrnehmung.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/wahrnehmung.png)](http://192.168.5.129/uploads/images/gallery/2025-06/wahrnehmung.png)

Das Lesen kann über die Menüleiste auf der linken Seite (Unterpunkt Wahrnehmung) aufgerufen werden. Dies ist ein Vorschritt für den Schritt des Leseformulars. Das heißt, damit das Leseformular Informationen korrekt extrahieren kann, muss die leere Dokumentenvorlage zuvor im Lesebereich bearbeitet und korrekt in der Datenbank gespeichert werden. In der Lesung können die entsprechenden Dokumente über Formular öffnen erstellt, bearbeitet oder gelöscht werden.

Für die allgemeine Steuerung befinden sich die folgenden Schaltflächen in der Menüleiste:

### <span lang="DE">Lesen (Obere Leiste)</span>

[![Lesen obere Leiste.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/lesen-obere-leiste.png)](http://192.168.5.129/uploads/images/gallery/2025-06/lesen-obere-leiste.png)

<span lang="DE">Die Erläuterung der Steuerelemente von links nach rechts:</span>

#### <span lang="DE">Neu </span>[![Neu.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/hyuneu.png)](http://192.168.5.129/uploads/images/gallery/2025-06/hyuneu.png)

Erzeugt ein neues Objekt. Wenn Sie darauf klicken, erscheint ein Pop-up-Fenster. Ändern Sie die Einstellung für das Gerätefeld von „Screenshot“ auf „Disk“. Sie werden aufgefordert, eine Datei für die Vorlage zu wählen. Hier sollten Sie die leere Vorlage wählen. Die Verzögerung sollte auf „keine Verzögerung“ eingestellt werden.

[![PopUp.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/popup.png)](http://192.168.5.129/uploads/images/gallery/2025-06/popup.png)

#### <span lang="DE">Formular einfügen [![Formular einfügen.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/formular-einfugen.png)](http://192.168.5.129/uploads/images/gallery/2025-06/formular-einfugen.png)</span>

Alternative Möglichkeit ein neues Formular zu erstellen.

#### <span lang="DE">Speichern [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706793451395.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706793451395.png)</span>

Speichern des aktuellen Formulars auf der Festplatte.

#### <span lang="DE">Kopieren </span>[![Kopieren.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/kopieren.png)](http://192.168.5.129/uploads/images/gallery/2025-06/kopieren.png)

Speichern einer Kopie eines erstellten Formulars. Damit gibt es nun eine exakte Kopie des Formulars, die bearbeitet werden kann, ohne dass das Original verändert wird.

#### <span lang="DE">Hilfe [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706793458585.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706793458585.png)</span>

<span lang="DE">Öffnet das EMMA Studio Handbuch</span>


## Bearbeiten einer Vorlage

Das Lesen ist in der Registerkarte Neues Formular in zwei Hauptbereiche unterteilt: Links befindet sich die Formularquelle, rechts ist der Bearbeitungsbereich des Formulars. Mit Hilfe der Felder auf der rechten Seite wird der ausgewählte Ausschnitt der Formularquelle durch einen rechteckigen Ausschnitt im Formularbereich eingerahmt. Alternativ kann eine bereits gespeicherte ID über den Reiter Formular öffnen übernommen werden.

Dieses Bild zeigt den Lesebereich mit den Registerkarten „Neues Formular“ und „Formular öffnen“

#### „Neues Formular“

Ist bereits voreingestellt und wird immer beibehalten, solange nicht auf „Formular öffnen“ geklickt wird.

#### „Neues Formular“

Wenn Sie darauf klicken, können Sie ein bereits bearbeitetes Formular öffnen. Die Auswahl eines Formulars öffnet das Formular mit allen Änderungen und schaltet die Registerkarte zurück auf „Neues Formular“.

[![Neues Formular.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/neues-formular.png)](http://192.168.5.129/uploads/images/gallery/2025-06/neues-formular.png)

Der zweite Bereich ist der Bearbeitungsbereich.

Es enthält mehrere Felder und Boxen, mit denen Sie arbeiten können. Das Dokument kann wie folgt bearbeitet werden.

[![Neues Formular bearbeiten.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/neues-formular-bearbeiten.png)](http://192.168.5.129/uploads/images/gallery/2025-06/neues-formular-bearbeiten.png)

[![Feld 1.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/feld-1.png)](http://192.168.5.129/uploads/images/gallery/2025-06/feld-1.png)

<table aria-rowcount="10" border="1" class="Table Ltr TableWordWrap SCXW23454373 BCX0" data-tablelook="1696" data-tablestyle="MsoTableGrid" id="bkmrk-field%C2%A0-description%C2%A0-"><tbody class="SCXW23454373 BCX0"><tr aria-rowindex="1" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstRow FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader">Feld

</td><td class="FirstRow LastCol SCXW23454373 BCX0" data-celllook="0" role="columnheader">Beschreibung

</td></tr><tr aria-rowindex="2" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader">Feldname

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">Name zur Identifizierung dieses Informationsabschnitts

</td></tr><tr aria-rowindex="3" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW23454373 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW23454373 BCX0">Feldtyp</span></span><span class="EOP SCXW23454373 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"335559738":0,"335559739":0}"> </span>

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">Die Schriftart des Textes innerhalb des Abschnitts (Schreibmaschine, Gothic, etc...)

</td></tr><tr aria-rowindex="4" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader">Sprache

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">Die Sprache des Textes innerhalb des Abschnitts (Deutsch, Englisch, etc...)

</td></tr><tr aria-rowindex="5" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader">Inhalt

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">Die Art des Textes innerhalb des Abschnitts (Währung, E-Mail, etc...)

</td></tr><tr aria-rowindex="6" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW23454373 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SpellingErrorV2Themed SCXW23454373 BCX0">Zusatz</span></span><span class="EOP SCXW23454373 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"335559738":0,"335559739":0}"> </span>

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">kann ein Validierungsmuster enthalten, wie in den [Eigenschaften des Lesen Schritts](http://192.168.5.129/link/87#bkmrk-text-eigenschaften)

</td></tr><tr aria-rowindex="7" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW23454373 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW23454373 BCX0">X</span></span><span class="EOP SCXW23454373 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"335559738":0,"335559739":0}"> </span>

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">steht für die horizontale Position des Anfangspunkts des Rechtecks (oder der linken Kante)

</td></tr><tr aria-rowindex="8" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW23454373 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW23454373 BCX0">Y</span></span><span class="EOP SCXW23454373 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"201341983":0,"335551550":1,"335551620":1,"335559685":0,"335559737":0,"335559738":0,"335559739":0,"335559740":240}"> </span>

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">steht für die vertikale Position des Anfangspunkts des Rechtecks (oder der oberen Kante)

</td></tr><tr aria-rowindex="9" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol SCXW23454373 BCX0" data-celllook="0" role="rowheader">Breite

<span class="EOP SCXW23454373 BCX0" data-ccp-props="{}"> </span>

</td><td class="LastCol SCXW23454373 BCX0" data-celllook="0">gibt die horizontale Größe des Rechtecks an

</td></tr><tr aria-rowindex="10" class="TableRow SCXW23454373 BCX0" role="row"><td class="FirstCol LastRow SCXW23454373 BCX0" data-celllook="0" role="rowheader">Höhe

<span class="EOP SCXW23454373 BCX0" data-ccp-props="{}"> </span>

</td><td class="LastCol LastRow SCXW23454373 BCX0" data-celllook="0">gibt die vertikale Größe des Rechtecks an

</td></tr></tbody></table>

Der markierte Bereich kann wie zuvor erwähnt über das Feld im Bearbeitungsbereich oder durch Anfassen der Kanten im Formularbereich in der Größe verändert werden.

Wenn Sie einen Bereich erfolgreich festgelegt haben, wird dieser orange umrandet dargestellt. Pro Bereich kann nur eine einzige Informationsart erfasst werden. (Hier wurde als Beispiel die „Anschrift der Wohngeldbehörde" ausgewählt.)

[![Neues Formular 2.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/neues-formular-2.png)](http://192.168.5.129/uploads/images/gallery/2025-06/neues-formular-2.png)

Sobald ein Feld fertig ist und ein Abschnitt richtig definiert ist. Um einen weiteren Abschnitt hinzuzufügen, drücken Sie auf die grün markierte Schaltfläche „Hinzufügen“. Dadurch wird ein neues Feld erstellt und der Prozess der Bearbeitung dieses Feldes beginnt, bis es weitere benötigte Informationen enthält.

[![Hinzufügen.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/hinzufugen.png)](http://192.168.5.129/uploads/images/gallery/2025-06/hinzufugen.png)

#### Vergrößern/Verkleinern:

- Verwenden Sie Strg + Mausrad, um das Formular zu vergrößern oder zu verkleinern, um eine detailliertere Ansicht zu erhalten.

Die Farbe für den Abschnitt ist orange vorgegeben und kann nicht geändert werden.

#### Formular Eigenschaften:

[![Formular Eigenschaften.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/formular-eigenschaften.png)](http://192.168.5.129/uploads/images/gallery/2025-06/formular-eigenschaften.png)

<table aria-rowcount="5" border="1" class="Table Ltr TableWordWrap SCXW68877422 BCX0" data-tablelook="1696" data-tablestyle="MsoTableGrid" id="bkmrk-option%C2%A0-description%C2%A0"><tbody class="SCXW68877422 BCX0"><tr aria-rowindex="1" class="TableRow SCXW68877422 BCX0" role="row"><td class="FirstRow FirstCol SCXW68877422 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW68877422 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW68877422 BCX0">Option</span></span><span class="EOP SCXW68877422 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"335551550":2,"335551620":2,"335559738":0,"335559739":0}"> </span>

</td><td class="FirstRow LastCol SCXW68877422 BCX0" data-celllook="0" role="columnheader">Beschreibung

</td></tr><tr aria-rowindex="2" class="TableRow SCXW68877422 BCX0" role="row"><td class="FirstCol SCXW68877422 BCX0" data-celllook="0" role="rowheader"><span class="TextRun SCXW68877422 BCX0" data-contrast="auto" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW68877422 BCX0">ID</span></span><span class="EOP SCXW68877422 BCX0" data-ccp-props="{"134233117":false,"134233118":false,"335559738":0,"335559739":0}"> </span>

</td><td class="LastCol SCXW68877422 BCX0" data-celllook="0"><span class="TextRun SCXW68877422 BCX0" data-contrast="auto" lang="EN-US" xml:lang="EN-US"><span class="NormalTextRun SCXW68877422 BCX0">Die eindeutige ID eines Formulars. Wenn der Name des Formulars zufällig geändert oder vergessen wird. Sie können es anhand dieser ID finden.</span></span>

</td></tr><tr aria-rowindex="3" class="TableRow SCXW68877422 BCX0" role="row"><td class="FirstCol SCXW68877422 BCX0" data-celllook="0" role="rowheader">Name

</td><td class="LastCol SCXW68877422 BCX0" data-celllook="0"><span class="TextRun SCXW68877422 BCX0" data-contrast="none" lang="DE-DE" xml:lang="DE-DE"><span class="NormalTextRun SCXW68877422 BCX0">Ein Name für ein Formular. Dieser Wert kann geändert werden.</span></span>

</td></tr><tr aria-rowindex="4" class="TableRow SCXW68877422 BCX0" role="row"><td class="FirstCol SCXW68877422 BCX0" data-celllook="0" role="rowheader">global verfügbar

</td><td class="LastCol SCXW68877422 BCX0" data-celllook="0">Ist das Kästchen aktiviert, steht das Objekt nicht nur in der Umgebung des aktuell bearbeiteten Projekts zur Verfügung, sondern auch in der gleichen Umgebung in anderen Projekten.

</td></tr><tr aria-rowindex="5" class="TableRow SCXW68877422 BCX0" role="row"><td class="FirstCol LastRow SCXW68877422 BCX0" data-celllook="0" role="rowheader">Tags

</td><td class="LastCol LastRow SCXW68877422 BCX0" data-celllook="0">Auswahl der Tags, die einer Objektkomposition zugewiesen werden sollen. Die verfügbaren Tags können individuell unter EMMA Configuration definiert werden.

</td></tr></tbody></table>

## Änderung der Vorlage

Klicken Sie auf die Registerkarte „Vorlage öffnen“ auf der linken Seite. Im Abschnitt „Suchkriterium“ können Sie die auswählbaren Vorlagen filtern, indem Sie bei der Suche über das Textfeld „Name“ Tags eingeben. Durch Drücken der ENTER-Taste wird die Suche gestartet, die erst nach Eingabe von mindestens drei Zeichen ausgeführt werden kann. Die entsprechenden Vorlagendokumente werden im unteren Bereich - unter Vorlagen - zur Auswahl angeboten. Die jeweilige Vorlage wird durch die folgenden Werte gekennzeichnet:

#### ID

ID der Vorlage

#### Name

Name der Vorlage

#### Project

Projekt(e) in denen die Vorlage nutzbar ist

#### Environment

Umgebung(en) in denen die Vorlage nutzbar ist

#### Erstellungsdatum

Datum der Erstellung

#### Änderungsdatum

Datum an dem es zuletzt geändert wurde

# Hören

[![image.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/scaled-1680-/9Qfimage.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/9Qfimage.png)

<span lang="DE">Der Prozessschritt ***Sprechen*** (Abspielen eines Sounds in Richtung des Device) </span><span lang="DE">kann als Input Sounddateien verwenden. Das Anlegen und die Verwaltung dieser Dateien erfolgen mithilfe der Wahrnehmung ***Hören***. Dieser lässt sich über die Menüleiste auf der linken Seite öffnen (Unterpunkt ***Wahrnehmung***).  
  
[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/l8Ximage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/l8Ximage.png)</span>

<span lang="DE">Zur allgemeinen Steuerung stehen in der Menüleiste die folgenden Buttons zur Verfügung:</span>

#### <span lang="DE">Öffnen [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/rbAimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/rbAimage.png)</span>

<span lang="DE">Öffnet eine Sounddatei aus einem auszuwählenden Ordner (weitere Details siehe Kapitel 4.5.2).</span>

#### <span lang="DE">Speichern [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/JN4image.png)](http://192.168.5.129/uploads/images/gallery/2024-05/JN4image.png)</span>

<span lang="DE">Speichert die aktuelle Sounddatei auf der Festplatte.</span>

#### <span lang="DE">Hilfe [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/RB0image.png)](http://192.168.5.129/uploads/images/gallery/2024-05/RB0image.png)</span>

<span lang="DE">Öffnet das **EMMA Studio Benutzer**</span><span lang="DE">**handbuch**.</span>

#### <span lang="DE">Zurücksetzen [![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/N3yimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/N3yimage.png)</span>

<span lang="DE">Verwirft die bearbeitete Sounddatei und die bereits erfolgten Einträge unter **Sound Eigenschaften** auf der rechten Seite.</span>

### <span lang="DE">Hinzufügen einer neuen Sounddatei</span>

<span lang="DE">[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/YuYimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/YuYimage.png)</span>

<span lang="DE">Um einen Sound in **EMMA** zu laden, muss eine Wave-Datei über den ***Öffnen***-Button der Menüleiste von der Festplatte ausgewählt und diese anschließend mit dem Pfeil ([![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/VdLimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/VdLimage.png)</span><span lang="DE">) in den Arbeitsbereich (rechte Seite der Maske) übernommen werden.</span>

### <span lang="DE">Benutzerdefinierte Werte</span>

#### <span lang="DE">Name</span>

<span lang="DE">Der Benutzer legt einen eindeutigen Namen fest. Ob dieser bereits besetzt ist, wird im darunterliegenden Feld **Benutzte Namen** angezeigt.</span>

#### <span lang="DE">Tags</span>

<span lang="DE">An dieser Stelle können den jeweiligen Sounds vordefinierte Tags zugeordnet werden. Die Tags werden in **EMMA Configuration** (siehe Kapitel 5.4) definiert.</span>

### <span lang="DE">Automatisch ausgefüllte Werte</span>

#### <span lang="DE">ID</span>

<span lang="DE">Die eindeutige ID eines Sounds. Dieser Wert wird automatisch gesetzt. Wenn der Wert nicht gesetzt ist, wird die aktuell bearbeitete Audiodatei als neuer Sound gespeichert.</span>

#### <span lang="DE">Benu</span><span lang="DE">tzte Na</span><span lang="DE">men</span>

<span lang="DE">Anzeige bereits verwendeter Bezeichnungen zur Vereinfachung der Namensfindung.</span>

#### <span lang="DE">Quelle</span>

<span lang="DE">Quelle des Sounds</span>

#### <span lang="DE">Format</span>

<span lang="DE">Audioformat</span>

#### <span lang="DE">Benutzt in Prozess</span>

<span lang="DE">Anzeige aller Prozesse und der zugehörigen Prozessschritte, in denen der aktuell ausgewählte Sound verwendet wird. Mit dem darunterliegenden Button ***Sound löschen*** kann der vorliegende Sound gelöscht werden – sofern dieser in keinem Prozess verwendet wird.</span>

### <span lang="DE">Bearbeiten eines vorhandenen Sounds</span>

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/xBVimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/xBVimage.png)

<span lang="DE">Über den Tab **Sound öffnen** kann ein Sound zum Bearbeiten geöffnet werden. Man kann an dieser Stelle den Namen und die Tags anpassen, den Sound löschen (sofern dieser nicht verwendet wird) und über den Tab **Neuer Sound** die vorliegende Audiodatei ersetzen.</span>

# Dokumentvorlagen erstellen

Der Schritt ***Dokumentenanalyse*** (Analyse der Dokumente mit einer bestimmten Vorlage – siehe Dokumentenanalyse) benötigt eine Dokumentvorlage als Eingabe. Diese Vorlagen werden bei den Dokumenten gespeichert und verwaltet. Sie können über die Menüleiste auf der linken Seite (Unterpunkt ***Wahrnehmung***) geöffnet werden.

Zur allgemeinen Steuerung befinden sich in der Menüleiste die folgenden Schaltflächen:

#### Quelle der Vorlage

Hier kann ausgewählt werden, ob die Vorlage per Screenshot erstellt oder von der Festplatte als Datei PDF/Bild geöffnet werden soll.

#### Neu

Erzeugt einen Screenshot, um darauf basierend eine neue Vorlage zu erstellen.

#### Öffnen

Öffnet eine Vorlage aus einem wählbaren Ordner (weitere Details siehe Kapitel 4.5.2).

#### Speichern

Über diesen Button wird die aktuelle Dokumentvorlage gespeichert.

## Erstellen einer neuen Vorlage

Beginnen wir mit dem Baustein der Vorlage – dem Abschnitt. Jeder Abschnitt enthält die folgenden Elemente (siehe Abb.):

##### Feldname

Ein benutzerdefinierter Name für den Abschnitt, damit der Benutzer einen aussagekräftigen Namen für eine bessere Benutzerfreundlichkeit vergeben kann.

##### Textstil

Die Schriftart des Texts im Abschnitt (Handschrift, Gotisch etc.).

##### Sprache

Die Sprache des Texts im Abschnitt (Deutsch, Englisch etc.).

##### Inhalt

Die Art des Texts im Abschnitt (Währung, E-Mail etc.)

##### Koordinaten des Rechtecks  


**X:** Gibt die horizontale Position des Anfangspunkts des Rechtecks an (oder den linken Rand).

**Y:** Gibt die vertikale Position des Anfangspunkts des Rechtecks an (oder die obere Kante).

**Breite:** Gibt die horizontale Ausdehnung des Rechtecks an.

**Höhe:** Gibt die vertikale Ausdehnung des Rechtecks an.

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/pp5image.png)](http://192.168.5.129/uploads/images/gallery/2024-06/pp5image.png)

Um eine neue Dokumentvorlage zu erstellen, wähle zunächst die Datei.

Der Arbeitsbereich besteht aus zwei Bereichen. Auf der linken Seite kannst du das Rechteck durch Ziehen mit der Maus grafisch vergrößern bzw. verkleinern. Die rechte Seite ist wiederum in zwei Bereiche unterteilt: den oberen, in dem die Abschnitte dargestellt werden (siehe Abbildung oben), und den unteren, der die Eigenschaften der Vorlage enthält.

In einigen wenigen Feldern in den Eigenschaften müssen Werte eingetragen werden. Der Rest wird vom System ausgefüllt.

##### ID  


Die eindeutige ID der Dokumentvorlage. Dieser Wert wird automatisch eingestellt. Wenn der Wert nicht gesetzt ist, wird die aktuell bearbeitete Vorlage als neue Dokumentvorlage gespeichert.

##### Name  


Der Benutzer legt einen eindeutigen Namen fest. Ob der Name bereits verwendet wird, wird im folgenden Feld (**Verwendete Namen**) angezeigt.

##### Verwendete Namen  


Anzeige der bereits verwendeten Namen, um die Namensauswahl zu erleichtern.

##### Global  


Wenn das Kontrollkästchen aktiviert ist, steht die Vorlage nicht nur in der Umgebung des aktuell bearbeiteten Projekts zur Verfügung, sondern auch in derselben Umgebung in anderen Projekten.

##### Schlagwörter  


Auswahl der Tags, die einer Dokumentvorlage zugewiesen werden sollen. Die verfügbaren Tags können individuell unter **EMMA Configuration** definiert werden (siehe Kapitel 5.3).

### Ändern der Vorlage  


Der Tab **Vorlage öffnen** befindet sich auf der linken Seite. Der Abschnitt **Suchkriterien** ermöglicht die Filterung der auswählbaren Vorlagen durch Eingabe von Tags, wenn eine Suche über das Textfeld **Name** durchgeführt wird. Die Suche wird mit der ENTER-Taste gestartet und kann erst nach Eingabe von mindestens drei Zeichen ausgeführt werden. Im unteren Bereich unter **Vorlagen** werden die entsprechenden Dokumentvorlagen zur Auswahl angeboten. Die jeweilige Vorlage ist ein Objekt mit den folgenden Werten:

##### ID  


ID der Vorlage

##### Name  


Name der Vorlage

##### Projekt  


Projekt/e, in dem/denen die Vorlage verfügbar ist

##### Umgebung  


Umgebung/en, in der/denen die Vorlage verfügbar ist

##### Erstellungsdatum  


Datum der Erstellung

##### Datum der Änderung  


Datum der letzten Änderung

Durch Klick auf die Pfeiltaste <span lang="DE">([![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/VdLimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/VdLimage.png)</span><span lang="DE">)</span> in der Mitte des Programmfensters oder durch Doppelklick auf den entsprechenden Eintrag wird das Objekt in den Arbeitsbereich übernommen. Die weiteren Bearbeitungsschritte sind analog zu Kapitel 4.5.1. Dabei ist zu beachten, dass bei einem Eintrag im Feld **ID** das entsprechende Objekt bei einem Speichervorgang überschrieben wird.

# Lernen

[![image.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/scaled-1680-/GCvimage.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/GCvimage.png)

Im Abschnitt ***Lernen*** können Benutzer Modelle für maschinelles Lernen (Skills) trainieren. Diese können später im Schritt ***Klassifizierung*** verwendet werden, um beispielsweise Bilder oder Dokumente zu klassifizieren. Dieser Bereich bietet eine Oberfläche zur Definition von Kategorien, zum Trainieren von Modellen sowie zum Exportieren dieser Modelle zur weiteren Verwendung.[![image.png](http://192.168.5.129/uploads/images/gallery/2025-05/scaled-1680-/DeVimage.png)](http://192.168.5.129/uploads/images/gallery/2025-05/DeVimage.png)

### Allgemeiner Überblick

Dieser Abschnitt gliedert sich in die folgenden Hauptbereiche:

- Modellauswahl
- Kategorien
- Modelloptionen
- Ergebnisse

#### Modellauswahl

In diesem Bereich kann der Benutzer den Pfad des Trainingsservers (Skill-Engine-Pfad) auswählen. Auf diesem Server wird der Trainingsprozess ausgeführt. Dabei ist der Server eine lokale .exe-Datei, die die Skill Engine darstellt.

Unter **Trainer** wird der Pfad zu dem Server angegeben, der das Modelltraining ausführt.

#### Kategorien

Hier legen die Benutzer die Kategorien (Labels) fest und verknüpfen die Ordner der Trainingsdaten.

- **Category Name**: Der Name der Kategorie (z. B. „Rechnungen“ oder „Verträge“).
- **Folder Location**: Ordner, der Bilder oder Dokumente für die entsprechende Kategorie enthält.

#### Modelloptionen

In diesem Abschnitt werden modellspezifische Parameter konfiguriert.

- **Fähigkeit**: Der Name, der dem trainierten Modell zugewiesen wurde.
- **Trainingsziel** (auch Zielgenauigkeit genannt): Der Mindestprozentsatz an Genauigkeit, den ein Modell erreichen muss, um als erfolgreich trainiert zu gelten. 
    - Standardwert: 80 %

#### Ergebnisse

Nach Abschluss des Trainings werden die folgenden Bewertungsmetriken angezeigt:

- **Genauigkeit**: Der Prozentsatz der richtigen Klassifizierungen während des Trainings.
- **Präzision**: Der Prozentsatz der korrekt klassifizierten positiven Proben von allen vorhergesagten positiven Proben.
- **Abrufen**: Der Prozentsatz der korrekt klassifizierten positiven Proben unter allen tatsächlich positiven Proben.

Mithilfe dieser Metriken kann die Qualität des trainierten Modells bewertet werden.

### Workflow

#### Trainingskategorien definieren

Erstelle Kategorien und weise den entsprechenden Ordnern passende Bilder oder Dokumente zu.

#### Trainingsparameter festlegen

Konfiguriere zunächst den Pfad zum Trainingsserver und gib anschließend den Namen der Fähigkeit an. Lege anschließend das Trainingsziel fest (erforderliche Mindestgenauigkeit).

#### Training beginnen

Klicke auf den Button ***Trainieren***, um das Modelltraining zu starten. Der Trainingsserver verarbeitet die Daten, trainiert das Modell und evaluiert dessen Leistung.

#### Überprüfung der Ergebnisse

Überprüfe die Metriken **Genauigkeit**, **Präzision** und **Abrufen** im Ergebnisbereich.

#### Speichern des Modells

Wenn du mit den Ergebnissen zufrieden bist, klicke auf ***Fähigkeit speichern***, um die trainierte Fähigkeit als .joblib-Datei zu exportieren.

### Notizen

- Wenn das Trainingsziel nicht erreicht wird, können Benutzer: 
    - weitere Trainingsbeispiele hinzufügen, um den Datensatz zu verbessern.
    - die Datenqualität verbessern, indem sie beispielsweise klarere Bilder verwenden oder unterschiedlichere Beispiele hinzufügen.
- Gespeicherte Fähigkeiten können später im Schritt ***Klassifizierung*** verwendet werden.

# Prozesse

Prozesse erstellen und verwalten

# Prozess

<span lang="DE">Ein neuer Prozess kann entweder über die Menüleiste (***Datei* → *Neu* → *Prozess***) oder in der Navigationsleiste auf der linken Seite durch Klicken auf ***Prozess*** und dann auf ***Neu*** </span>[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/zv0image.png)](http://192.168.5.129/uploads/images/gallery/2024-05/zv0image.png) <span lang="DE">in der Symbolleiste erstellt werden. Ein bestehender Prozess kann entweder über die Menüleiste (***Datei* → *Öffnen* → *Prozess***) oder in der Navigationsleiste auf der linken Seite durch Klicken auf ***Prozess*** und dann auf ***Öffnen*** </span>[![image.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/kTDimage.png)](http://192.168.5.129/uploads/images/gallery/2024-05/kTDimage.png) <span lang="DE">in der Symbolleiste geöffnet werden. </span>

<span lang="DE">Ein **Prozess** ist eine Sammlung bzw. Aneinanderreihung oder Verknüpfung von einzelnen Prozessschritten und wird in **EMMA Studio** grafisch dargestellt. Das Ziel bei der Erstellung eines Prozesses ist es, einen Graphen mit gültigen Szenarien zu definieren, der vom Prozessschritt ***Start*** zum Prozessschritt ***Success*** führt. Ein auftretendes Szenario, das nicht innerhalb des Prozesses definiert wurde, wird automatisch als Fehlverhalten gewertet und führt zum Prozessabbruch.</span>

<span lang="DE">Die Maske besteht im Wesentlichen aus drei Feldern: **Prozess**, **Beweisbild** und **Einstellungen**. Durch horizontales oder vertikales Verschieben der orangefarbenen Linien kann die Größe der Felder verändert werden.</span>

# Prozess öffnen

Um mit der Automatisierung eines Prozesses zu beginnen, erstellt man entweder einen neuen Prozess über ***Neu*** oder wählt einen vorhandenen Prozess über ***Öffnen***. Während bei der Option ***Neu*** ein neuer Prozess direkt im [Prozesseditor](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/prozess-editor) geöffnet wird, wird bei der Option ***Öffnen*** die folgende Auswahlmaske angezeigt, in der der zu bearbeitende Prozess ausgewählt wird.

[![240621 Prozess öffnen.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-prozess-offnen.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-prozess-offnen.png) *Benutzeroberfläche für das Öffnen von Prozessen*

Durch einen Doppelklick oder durch die Auswahl der Zeile und anschließendes Klicken auf das Häkchen unten rechts wird der gewählte Prozess im [Prozesseditor](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/prozess-editor) geöffnet. Nach Auswahl der Zeile kann durch einen Rechtsklick auf die erste Spalte des Prozesses ein Menü zur Anpassung des Prozessstatus geöffnet werden. Ergänzend können Administratoren hier den Prozess einer anderen Umgebung oder einem anderen Projekt zuweisen. Das Entsperren wird ebenfalls in dieser Maske ermöglicht, woraufhin ein Prozess auch gelöscht werden kann. Zur leichteren Orientierung kann die angezeigte Liste der Prozesse mithilfe der Filter-Felder über der Tabelle eingeschränkt werden.

### Filter

#### Name

Dieser Filter filtert die Prozesse nach dem eingegebenen Namen oder nach der ID des Prozesses. Wird z. B. die Zahl „1“ eingegeben, werden die Prozesse (1 , 10 , 11 , 12 etc.) angezeigt, da diese Prozess-IDs die Zahl „1“ enthalten. Wird alternativ der Text „RegT“ in das Feld eingegeben, werden alle Prozesse angezeigt, die „RegT“ in ihrem Namen enthalten.

#### Kategorie

Mit diesem Filter werden die Prozesse nach den Kategorien gefiltert, mit denen die Prozesse gekennzeichnet sind. Wird hier eine Kategorie ausgewählt, werden nur die Prozesse angezeigt, die mit dieser Kategorie gekennzeichnet sind.

### Tabellenspalten

##### ID

Die zugewiesene ID des Prozesses.

##### Name

Der zugewiesene Name des Prozesses.

##### Kategorien

Eine durch Kommata getrennte Liste aller Kategorien, mit denen der Prozess gekennzeichnet ist.

##### Erstellungsdatum

Das Datum, an dem der Prozess erstmals erstellt wurde.

##### Ersteller

Der ursprüngliche Ersteller des Prozesses.

##### Änderungsdatum

Das Datum, an dem der Prozess zuletzt geändert wurde.

##### Bearbeiter

Die Person, die den Prozess zuletzt geändert hat. Wenn der Prozess gesperrt ist, ist dies der Name des Benutzers, der derzeit die Sperre für den Prozess besitzt.

##### Projekt und Umgebung

Das aktuelle Projekt und die Umgebung, in der sich der Prozess befindet. Befindet sich der Benutzer derzeit im Projekt „Any“ und in der Umgebung „Any“, dann können nur Prozesse geöffnet werden, die sich in „Any/Any“ befinden. Der Benutzer muss die Umgebung wechseln, um einen anderen Prozess zu öffnen.

### Zeilenfarben

##### Grau

Der Prozess ist derzeit von niemandem freigeschaltet und kann daher vom Benutzer freigeschaltet und bearbeitet werden.

##### Gelb

Der Prozess ist derzeit von einem anderen Benutzer freigeschaltet. Dadurch wird der Prozess in einen „Nur-Lesen“-Status gesetzt, was bedeutet, dass keine Änderungen am Prozess gespeichert werden können.

##### Grün

Der aktuelle Benutzer hat den Prozess für alle anderen Benutzer gesperrt, sodass nur noch er in der Lage ist, diesen Prozess zu bearbeiten und Änderungen am Prozess zu speichern. Benutzer mit dem Recht „Unlock\_Process“ können den Prozess aber wie oben beschrieben entsperren.

### Rechtsklickmenü

[![240621 Prozess öffnen Rechtsklick.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-prozess-offnen-rechtsklick.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-prozess-offnen-rechtsklick.png)

*Abbildung des Rechtsklickmenüs der Benutzeroberfläche des ausgewählten Prozesses*

Um das Rechtsklickmenü öffnen zu können, muss zunächst die Zeile ausgewählt und dann ein Rechtsklick in der ersten Spalte ausgeführt werden (die Spalte vor ID).

##### Öffnen

Öffnet den aktuell ausgewählten Prozess. Es erscheint eine Fehlermeldung, wenn sich der Benutzer in einem anderen Projekt und/oder einer anderen Umgebung angemeldet hat, als der Prozess, der geöffnet werden soll.

##### Entsperren

Wenn ein Prozess gesperrt ist (entweder vom aktuellen Benutzer oder von einem anderen Benutzer), wird diese Sperre gelöscht und der Prozess ist wieder für alle Benutzer änderbar.

##### Projekt/Umgebung zuweisen

Verschiebt den Prozess in das/die ausgewählte Projekt/Umgebung. Dieser Eintrag ist nur bei nicht gesperrten, grau hinterlegten Prozessen aktiviert.  
**ACHTUNG:** Externe Ressourcen, wie referenzierte Objekte, müssen gesondert in das entsprechende Projekt verschoben werden.

##### Löschen

Löscht den ausgewählten Prozess. Dieser Eintrag ist nur bei nicht gesperrten, grau hinterlegten Prozessen aktiviert.

# Prozesseditor

Der Prozesseditor ist das Herzstück von **EMMA Studio** und ermöglicht es Benutzern, ihre Ideen zur Prozessautomatisierung in die Realität umzusetzen.

[![Qsqimage_new.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/qsqimage-new.png)](http://192.168.5.129/uploads/images/gallery/2025-06/qsqimage-new.png)*Beschriftete Abbildung des Prozesseditors*

Die Prozesserstellung lässt sich in zwei Hauptteile unterteilen: den Ablaufplan (linke Seite) und die Eigenschaften der einzelnen Prozessschritte (rechte Seite).

Auf der linken Seite des Editors können Schritte erstellt, miteinander verbunden, verschoben, bearbeitet und gelöscht werden.  
Die rechte Seite des Bildschirms dient der Bearbeitung der Schritteigenschaften im Detail.

Beide Bereiche sind für die erfolgreiche Erstellung eines Automatisierungsprozesses wichtig.

## Teile der Benutzeroberfläche

### Werkzeugleiste

Die Werkzeugleiste enthält Werkzeuge, mit denen der Zustand des Diagramms bearbeitet werden kann.  
Alle Schaltflächen in der Werkzeugleiste bestimmen, was passiert, wenn man mit der Maus auf das Diagramm klickt.  
Jedes Werkzeug kann auch mit einer Tastenkombination aktiviert werden, sofern keine andere Konfiguration vorgenommen wurde.  
Somit besitzt jedes Werkzeug in der Werkzeugleiste eine eigene Tastenkombination, was eine schnelle Bearbeitung des Graphen ermöglicht. Die Tastenkombinationen (Shortcuts) können unter ***[Einstellungen → Shortcuts](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/shortcuts)*** individuell angepasst und für jeden Nutzer im persönlichen %AppData%-Verzeichnis gespeichert werden.  
Der Name eines Werkzeugs wird angezeigt, wenn du mit dem Mauszeiger über das Werkzeug in der Werkzeugleiste fährst.  
Unter ***Einstellungen → Graph-Einstellungen*** kann auch festgelegt werden, dass der Werkzeugname dauerhaft angezeigt wird.

### Obere Werkzeugleiste

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/ZMQimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/ZMQimage.png)

Die obere Werkzeugleiste enthält die folgenden Werkzeuge zur allgemeinen Bearbeitung der Prozessgraphen:

<table border="1" id="bkmrk-werkzeugbild-tastenk" style="border-collapse: collapse; width: 100%; height: 401.734px;"><colgroup><col style="width: 15.0163%;"></col><col style="width: 15.3725%;"></col><col style="width: 69.6004%;"></col></colgroup><tbody><tr style="height: 29.7969px;"><td style="height: 29.7969px;">**Werkzeugsymbol**</td><td style="height: 29.7969px;">**Tastenkombination**</td><td style="height: 29.7969px;">**Beschreibung**</td></tr><tr style="height: 73.1875px;"><td style="height: 73.1875px;">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/gqKimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/gqKimage.png)

Cursor

</td><td style="height: 73.1875px;">{Escape}</td><td style="height: 73.1875px;">**Auswahlwerkzeug:** Ermöglicht die Auswahl und die Anordnung von Prozessschritten. Wenn ein Schritt ausgewählt ist, werden die zugehörigen Einstellungen und – falls der Schritt bereits ausgeführt wurde – die jeweiligen Ausführungsergebnisse angezeigt.  
  
</td></tr><tr style="height: 72.1875px;"><td style="height: 72.1875px;">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/gU4image.png)](http://192.168.5.129/uploads/images/gallery/2025-02/gU4image.png) Radiergummi

</td><td style="height: 72.1875px;">{D}</td><td style="height: 72.1875px;">**Löschen:** Löscht den Schritt oder den Pfeil, wenn er mit der linken oberen Ecke des Radiergummis angeklickt wird.</td></tr><tr style="height: 73.1875px;"><td style="height: 73.1875px;">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/Sfqimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/Sfqimage.png)

Grüner Pfeil

</td><td style="height: 73.1875px;">{T}</td><td style="height: 73.1875px;">**Wahr-Pfeil erstellen** (grün): Erzeugt einen Wahr-Pfeil von einem Schritt zu einem anderen. Wenn bereits ein Wahr-Pfeil von dem Schritt ausgeht, wird der vorherige Pfeil deaktiviert (wird grau) und der neue aktive Wahr-Pfeil wird zum aktuellen Pfeil.</td></tr><tr style="height: 75.1875px;"><td style="height: 75.1875px;">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/HQcimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/HQcimage.png)

Roter Pfeil

</td><td style="height: 75.1875px;">{F}</td><td style="height: 75.1875px;">**Falsch-Pfeil erstellen** (rot): Erzeugt einen Falsch-Pfeil von einem Schritt zu einem anderen. Wenn bereits ein Falsch-Pfeil von dem Schritt ausgeht, wird der vorherige Pfeil deaktiviert (wird grau) und der neue aktive Falsch-Pfeil wird zum aktuellen Pfeil.</td></tr><tr style="height: 78.1875px;"><td style="height: 78.1875px;">[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/x0bimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/x0bimage.png)

Flagge

</td><td style="height: 78.1875px;">{B}</td><td style="height: 78.1875px;">**Haltepunkt hinzufügen** (Flagge): Setzt oder löscht einen Haltepunkt, wenn ein Schritt angeklickt wird. Wird der Prozess ausgeführt, stoppt die Ausführung vor diesem Schritt, was für das Debugging hilfreich ist. Der Haltepunktstatus des Schritts wird beim Speichern des Prozesses nicht gespeichert.</td></tr></tbody></table>

### Linke Werkzeugleiste

Die linke Werkzeugleiste (Schrittauswahlleiste) enthält alle verfügbaren Prozessschritte, die in einem Ablaufplan (Prozessgraph) verwendet werden können.  
Wenn ein Schritterstellungswerkzeug ausgewählt ist, ändert sich der Cursor zu einem Kreis. Klickt man nun mit dem Cursor auf das Diagramm, wird ein Schritt des ausgewählten Typs erstellt. Dabei werden alle ausgewählten Schritte als Parent-Schritte des neu erstellten Schritts übernommen.  
Alternativ kann ein Schritt auch erstellt werden, indem man das Icon des Schritterstellungswerkzeugs per Drag &amp; Drop in den Graphen zieht.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/nEPimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/nEPimage.png)

### Ergebnisfeld

[![ergebnisfenster.PNG](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/ergebnisfenster.PNG)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/ergebnisfenster.PNG)

Das Ergebnisfeld zeigt die Ergebniswerte des aktiven Schritts an und gibt Auskunft darüber, ob der Schritt korrekt abgeschlossen wurde.  
Die Größe des Ergebnisfelds passt sich dynamisch an die Anzahl der vom Schritt erzeugten Ergebnisse an. Die Ergebnisbox zeigt die Schritt-ID an. Per Klick kann direkt zum Schritt gesprungen werden.  
Eine Erläuterung der verschiedenen Werte in diesem Feld ist im Abschnitt [Schrittergebnisse](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/prozessschritt-ergebnisse) zu finden.

### Untere Werkzeugleiste

[![untere Werkzeugleiste.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/untere-werkzeugleiste.png)](http://192.168.5.129/uploads/images/gallery/2025-06/untere-werkzeugleiste.png)


#### Zentrieren

Neuausrichtung und Vergrößerung des Diagramms, sodass alle aktuell erstellten Schritte in der Ansicht sichtbar sind.

#### Ausrichten

Verschiebt die Schritte so, dass ein logischer Fluss von oben nach unten entsteht. Der **Startschritt** befindet sich am oberen Rand der Ansicht und der Schritt, der am weitesten vom **Startschritt** entfernt ist, am unteren Rand.

#### Ergebnisse

Hier können Benutzer die Ergebnisse verschiedener Läufe einsehen. Wenn die Ergebnisse eines Laufs in einen bestimmten Prozess übertragen werden sollen, können sie hier ausgewählt werden. Derzeit werden sowohl Ergebnisse aus verschachtelten Testfällen und Berichten als auch aus einzelnen Läufen unterstützt. Bei Auswahl eines bestimmten Ergebnisses werden die Farben der Schritte im Laufmodus sowie die angezeigten Ergebnisse in beiden Modi aktualisiert.

#### Modus

Mit diesem Button kannst du den aktiven Modus des Editors zwischen ***Modus: Lauf*** und ***Modus: Bearbeiten*** umschalten.

### Ergebnisbild

Das Ergebnisbild ist der Screenshot, der vom ausgewählten Schritt nach dessen Ausführung angezeigt wird.  
Falls das Schrittergebnis Koordinaten enthält (zum Beispiel von einer gefundenen Position), werden diese durch Linien oder Kästen hervorgehoben, um das Ergebnis zu visualisieren.  
Wenn kein Ergebnisbild vorhanden ist (entweder weil der Prozess noch nicht ausgeführt wurde oder weil der Schritt keine Bildausgabe erzeugt hat), bleibt das Feld leer.

### Variablennutzung

Anstelle des Ergebnisbilds kann auf der rechten Seite auch eine Tabelle der Variablennutzung angezeigt werden.  
Diese Tabelle listet für alle Schritte die Regeln zur Variablenmanipulation auf.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/kYwimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/kYwimage.png)

Die Tabellenspalten können mit einem Klick auf den Spaltennamen sortiert werden.  
Zusätzlich wird bei Doppelklick auf eine der ersten drei Zellen einer Zeile (Zeilenkopf, Schritt-ID und Schrittname) der entsprechende Schritt im Graphen auf der linken Seite aktiviert und die Eigenschaften unterhalb der Tabelle angezeigt. Die ausgewählte Regel zur Variablenmanipulation wird dabei hervorgehoben.

### Schrittsuche

[![schritt suche.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/schritt-suche.png)](http://192.168.5.129/uploads/images/gallery/2025-06/schritt-suche.png)

  
Diese Funktion ermöglicht es dem Benutzer, nach bestimmten Schritten zu suchen. Das Suchfeld kann standardmäßig mit der Tastenkombination STRG+F geöffnet werden.

#### Textfeld

Hier kann der Benutzer den gesuchten Text eingeben. Die Suche wird mit der ENTER-Taste oder per Klick auf die Lupe gestartet.

#### Auswahl des Suchtyps

Hier kann der Benutzer die Eigenschaften auswählen, die bei jedem Schritt durchsucht werden sollen:

- **Alle:** Findet alle Schritte, bei denen ein Teil des Schritts mit der gesuchten Zeichenfolge übereinstimmt.
- **Kommentar:** Findet alle Schritte, bei denen der Kommentar des Schritts die gesuchte Zeichenfolge enthält.
- **Konstante:** Findet alle Schritte, bei denen eine Schritteigenschaft auf eine Konstante gesetzt ist, die dem gesuchten Wert entspricht.
- **Variable:** Findet alle Schritte, bei denen entweder eine Schritteigenschaft auf eine Variable mit dem gesuchten Wert gesetzt ist oder bei denen eine Variablenmanipulation auf die gesuchte Variable angewendet wurde.
- **Schrittergebnis:** Findet alle Schritte, bei denen eine Schritteigenschaft auf den eingegebenen Feldnamen des Schrittergebnisses gesetzt ist oder bei denen die eingegebene ID mit der ID des Schritts im Schrittergebnis übereinstimmt.
- **Operator:** Findet alle Schritte, bei denen der Operator für die Variablenmanipulation mit dem gesuchten Wert übereinstimmt.
- **Bild:** Findet alle Schritte, die ein bestimmtes Ergebnisbild enthalten.
- **Schritttyp:** Findet alle Schritte, bei denen der Schritttyp mit dem gesuchten Wert übereinstimmt.
- **Haltepunkt:** Findet alle Schritte, die aktuell einen Haltepunkt darstellen.

### Suchaktionen

#### Pfeil nach oben

Wechselt zum vorherigen Schritt in den Suchergebnissen.

#### Pfeil nach unten

Wechselt zum nächsten Schritt in den Suchergebnissen.

#### Lupen-Symbol

Startet die Suche.

#### Kreuz-Symbol

Schließt das Suchfeld.

#### Groß-/Kleinschreibung ignorieren

Legt fest, ob die Groß- und Kleinschreibung bei der Suche nach Schritten berücksichtigt werden soll.

### Allgemeine Schritteigenschaften

Dies ist der Teil der Schritteigenschaften, der unabhängig vom ausgewählten Schritt immer gleich bleibt. Hier kannst du den Namen des Schritts, die Kommentare und die Bedingungen für den nächsten Schritt ändern.

### Spezielle Schritteigenschaften

Dies ist der Teil der Benutzeroberfläche, in dem du Änderungen an einzelnen Schritten vornehmen kannst. Dieser Bereich kann je nach dem ausgewählten Schritttyp stark variieren. Die speziellen Einstellungsmöglichkeiten werden im Abschnitt [Schritteigenschaften](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/chapter/schritt-eigenschaften) detailliert erläutert.

### Rechtsklickmenü

Durch einen Rechtsklick auf den Graphen sind verschiedene Bearbeitungsoptionen verfügbar:

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-02/scaled-1680-/zJEimage.png)](http://192.168.5.129/uploads/images/gallery/2025-02/zJEimage.png)

#### Löschen

Die aktuell ausgewählten Schritte werden gelöscht.

#### Kopieren

Die aktuell ausgewählten Schritte werden im XML-Format in die Zwischenablage kopiert.

#### Einfügen

Die in der Zwischenablage gespeicherten Schritte werden eingefügt. Die Einfügeposition verhält sich dabei wie folgt:

Wenn ***Einfügen*** über das Rechtsklickmenü ausgewählt wurde, wird der Schritt in der oberen linken Ecke des Menüs eingefügt.

Wenn mit **STRG+V** eingefügt wird, erscheint der Schritt in der Mitte des Diagramms, sofern dieses leer ist. Andernfalls wird der Schritt an der ersten freien Stelle in der rechten unteren Ecke der Mitte eingefügt.

#### Gruppe erstellen

Die aktuell ausgewählten Schritte werden in einer Gruppe zusammengeführt.

#### Haltepunkt

Bei einem ausgewählten Schritt wird ein Haltepunkt gesetzt oder entfernt. Wenn der ausgewählte Schritt bereits als **Haltepunktschritt** markiert ist, wird der Haltepunkt entfernt.

# Prozesseigenschaften

Sind die Eigenschaftsfenster der Prozessschritte geschlossen (z. B. durch Drücken des X-Symbols), werden an dieser Stelle die Prozesseigenschaften zur Bearbeitung angezeigt

[![240621 Prozesseigenschaften.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-prozesseigenschaften.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-prozesseigenschaften.png) Im Tab ***Prozess Eigenschaften*** werden die Eigenschaften eines Prozesses definiert, die entweder zur Verwaltung dienen (Name, Referenz etc.) oder die für alle Prozessschritte gleich sein sollen (Variablen, Ausnahmebehandlung). Die folgenden Felder können vom Benutzer ausgefüllt werden:

#### Name

Name des Prozesses.

#### Priorität

Vom Benutzer wählbarer Wert, der die Priorität widerspiegeln soll. Der Benutzer entscheidet über die Art der zu verwendenden Skala.

#### Kritikalität

Vom Benutzer wählbarer Wert, der die Kritikalität widerspiegeln soll.

#### Referenz

Verweis auf andere Systeme (zu Dokumentationszwecken).

#### Beschreibung

Beschreibung des Prozesses.

#### Erwartetes Ergebnis

Das erwartete Ergebnis des Prozesses.

Weitere Einstellungen können über die Buttons ***Ausnahmebehandlung***, ***Variablen*** und ***Kategorie*** vorgenommen werden. Die Buttons befinden sich am unteren Rand des Tabs ***Prozess Eigenschaften***.

### Verwendung als verschachtelter Prozess 

Der Tab ***Verwendet als Nested Prozess*** zeigt an, in welchen anderen Prozessen der aktuelle Prozess als [verschachtelter Prozess](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/verschachtelter-prozess) verwendet wird.

[![240621 Verschachtelter Prozess.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-verschachtelter-prozess.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-verschachtelter-prozess.png) *Abbildung 27 – Prozess – Verwendet als Nested Prozess*

In diesem Tab werden alle Prozesse aufgelistet, die den gewählten Prozess als verschachtelten Prozess verwenden, sowie die Kommentare, die innerhalb des Prozesses zur Beschreibung des Schritts des verschachtelten Prozesses verwendet werden.

### Ausnahmebehandlung

[![240621 Ausnahmebehandlung.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-ausnahmebehandlung.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-ausnahmebehandlung.png) *Abbildung 28 – Prozess – Ausnahmebehandlung*

Die ***Ausnahmebehandlung*** ermöglicht die Behandlung und Beseitigung von außergewöhnlichen Ereignissen, die während der Ausführung eines Prozesses auftreten können. Dies kann z. B. ein Pop-up-Fenster von einem anderen Programm sein. Ähnlich wie beim verschachtelten Prozess können mehrere vordefinierte Prozesse eingebettet werden, um eventuell auftretende Situationen so zu behandeln, dass der eigentliche Prozess fortgesetzt werden kann.  
Die eingebetteten Prozesse werden bei einem unerwarteten/unbehandelten Fehler eines Prozessschrittes nacheinander abgearbeitet, bis einer dieser Prozesse mit positivem Ergebnis abgeschlossen wurde. Daraufhin setzt **EMMA** die Ausführung des eigentlichen Prozesses an dem Schritt fort, an dem der Fehler ursprünglich aufgetreten ist.  
Damit die Prozesse für die Ausnahmebehandlung schnell und einfach gefunden werden können, ist es hilfreich, diese entsprechend zu kennzeichnen (z. B. durch eine Kategorie).

### Variablen

[![240621  Variablenmanagement.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-variablenmanagement.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-variablenmanagement.png)

*Abbildung 29 – Prozess – Variablen*  
Hier werden die [Variablen](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/variablen) für einen Prozess definiert. Die folgenden Felder können ausgefüllt werden:

#### Name

Gewünschter Name für die Variable.

#### Wert

Der Wert, der der Variablen zugewiesen werden soll. Dies hängt vom gewählten Typ ab. Mit Ausnahme des Typs „Text“ benötigen alle Typen einen Anfangswert.

#### Typ

Vom Benutzer auswählbar:

- **Boolean** (wahrer oder falscher Wert)
- **Ganzzahl**
- **Dezimalzahl** (nicht-ganzzahliger Dezimalwert)
- **Text**
- **Datum&amp;Uhrzeit** (formatiertes Datum)
- **Timer** (kann die Dauer eines Vorgangs mit den Operatoren „start“ und „stop“ messen)
- **Passwort**

#### In Report übernehmen

Wenn dieses Häkchen gesetzt ist, wird die Variable im Report aufgeführt.

#### Schnittstelle

Nach dem Hinzufügen der Variable mit einem Klick auf ***Hinzufügen*** kann nun die Schnittstelle festgelegt werden. Der Benutzer kann aus folgenden Optionen wählen:

- **Privat**: Die Variable ist nur in dem Prozess sichtbar und bearbeitbar, in dem sie verwendet wird. Ist dieser Prozess z. B. über einen verschachtelten Prozess in einen anderen Prozess eingebettet, kann dort nicht auf die Variable zugegriffen werden.
- **Eingehend**: Die Variable kann einen Wert von einem aufrufenden Prozess enthalten. Das bedeutet, dass sie von einem anderen Prozess initialisiert, aber nicht gelesen werden kann.
- **Ausgehend**: Die Variable kann ihren Wert an einen aufrufenden Prozess zurückgeben. Das bedeutet, dass sie von einem anderen Prozess gelesen, aber nicht initialisiert werden kann.
- **EinAus**: Die Variable kann ihre Werte von einem aufrufenden Prozess erhalten und nach Beenden des Prozesses auch einen geänderten Wert an den aufrufenden Prozess zurückgeben. Dies bedeutet, dass sie von einem anderen Prozess sowohl initialisiert als auch gelesen werden kann.

### Kategorien

[![240621 Kategorien.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-kategorien.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-kategorien.png)  
*Abbildung 30 – Prozess – Kategorien*

Um die spätere Suche nach Prozessen zu erleichtern, können diese verschiedenen benutzerdefinierten Kategorien zugeordnet werden. Kategorien werden nur zu Dokumentationszwecken und für die Suche nach Prozessen verwendet.

# Menüleiste

Wird ein Prozess im Prozessdiagramm angezeigt, sind folgende Optionen in der oberen Werkzeugleiste verfügbar:

#### Neu [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795390165.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795390165.png)

Erstellt einen neuen, leeren Prozess in einem separaten Tab.

#### Öffnen [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795397435.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795397435.png)

Zeigt eine Übersicht aller in der Datenbank gespeicherten Prozesse, aus denen ein Prozess zur Bearbeitung ausgewählt werden kann.

#### Speichern [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795402243.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795402243.png)

Speichert den aktuellen Prozess und überschreibt dabei ggf. die bestehende Version.

#### Kopieren [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795407162.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795407162.png)

Erstellt eine Kopie des aktuellen Prozesses und lädt diese direkt in den Editor.

#### Hilfe [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795415058.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795415058.png)

Öffnet das **EMMA Studio Benutzerhandbuch**.

#### Rückgängig [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795420331.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795420331.png)

Hebt die letzte Änderung im Prozessdiagramm auf.

#### Wiederholen [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795426393.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795426393.png)

Wendet die zuletzt rückgängig gemachte Änderung erneut an.

#### Starten [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795433498.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795433498.png)

Startet die Ausführung des Prozesses ab dem definierten **Start**-Schritt.

#### Folgende [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795440666.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795440666.png)

Startet die Ausführung ab dem ausgewählten Schritt und durchläuft nur die folgenden Schritte.

#### Nächsten [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795447392.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795447392.png)

Führt ausschließlich den aktuell markierten Schritt aus.

#### Stop [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795454298.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795454298.png)

Beendet die Ausführung des Prozesses. Dabei wird der aktuell laufende Schritt noch zu Ende geführt (bei einem **Finden**-Schritt kann das beispielsweise etwas dauern).

#### Sperren/Entsperren [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795461954.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795461954.png)

Sperrt oder entsperrt den Prozess für die Bearbeitung durch andere Benutzer. Gesperrte Prozesse können angesehen, aber nicht verändert werden.

#### Minimiert [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795474737.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795474737.png)

Wenn aktiviert, minimiert sich **EMMA Studio** während der Prozessausführung. Ist die Option deaktiviert, bleibt das Fenster im Vordergrund.

#### Zurücksetzen [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795479161.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795479161.png)

Setzt alle Variablen und Werte auf ihren Anfangszustand zurück.

#### Renummerieren [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706795486194.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706795486194.png)

Vergibt neue Nummern für die Prozessschritte entsprechend ihrer Reihenfolge im Ablaufplan.

# Variablen und deren Nutzung

Jede im Prozess definierte Variable wird zum Start der Prozessausführung mit ihrem initialen Wert bereitgestellt. Danach ist es in jedem Schritt möglich, die Werte der Variablen zu ändern. Diese Änderung (Manipulation) einer Variable in einem Prozessschritt erfolgt nach Ausführung des Schritts. Daher wird der neue Variablenwert erst im folgenden Schritt wirksam.

Im Allgemeinen können einfache Operationen zur Änderung der Werte ausgeführt sowie Ergebniswerte und andere Variablen zugewiesen werden. Die möglichen Operationen sind vom Variablentyp abhängig.

Die Variablenoperationen werden im Tab ***Variablen*** eingerichtet:

[![240621  Manipulation Variablen.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-manipulation-variablen.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-manipulation-variablen.png)   
*Abbildung 37 – Schritteigenschaften – Variablen*

Durch einen Doppelklick auf eine Variable, die in den Schritteigenschaften unter „**Verfügbare Variablen**" aufgelistet ist, wird eine neue Variablenoperation erstellt (neue Zeile in der Tabelle „**Manipulation der Variable**") und die Variable wird in das Feld „**Variable**" eingetragen.

Anschließend können in den Feldern „**Linker Wert**", „**Rechter Wert**" und „**Operation**" die folgenden Werte eingegeben bzw. definiert werden. Die Auswahlmenüs für „**Linker Wert**" und „**Rechter Wert**" lassen sich per Rechtsklick auf das jeweilige Feld öffnen.

Die Variablenoperationen werden in der dargestellten Reihenfolge von oben nach unten ausgeführt. Die Reihenfolge kann per Drag &amp; Drop geändert werden.

Der aktuelle Wert einer Variable kann hier auch direkt geändert werden, indem man das Feld auswählt und mittels F2-Taste die Bearbeitung startet.

### Manipulationsoperationen nach Variablentyp

#### Alle

Gültige Ergebnisfeldtypen: **Alle**

<table id="bkmrk-operation-beschreibu"><thead><tr><th>**Operation**</th><th>**Beschreibung der Manipulation**</th></tr></thead><tbody><tr><td>Wert zuweisen</td><td>Zuweisung eines Werts.</td></tr></tbody></table>

#### Boolean (Vergleichsoperator)

Gültige Ergebnisfeldtypen: **Konstanter Wert**, **Ausgeführt**, **Nächster Schritt**

<table id="bkmrk-operation-beschreibu-1" style="width: 100%;"><thead><tr><th style="width: 9.77106%;">**Operation**</th><th style="width: 90.2181%;">**Beschreibung der Manipulation**</th></tr></thead><tbody><tr><td style="width: 9.77106%;">||</td><td style="width: 90.2181%;">Logisches ODER: Gibt WAHR zurück, wenn mindestens ein Argument WAHR ist. Gibt FALSCH zurück, wenn beide Argumente FALSCH sind.</td></tr><tr><td style="width: 9.77106%;">&amp;&amp;</td><td style="width: 90.2181%;">Logisches UND: Gibt WAHR zurück, wenn beide Argumente WAHR sind. Gibt FALSCH zurück, wenn mindestens ein Argument FALSCH ist.</td></tr><tr><td style="width: 9.77106%;">!</td><td style="width: 90.2181%;">Logisches NOT: Invertiert den Wert eines Arguments.</td></tr></tbody></table>

#### Dezimalzahl

Gültige Ergebnisfeldtypen: **Konstanter Wert**, **X**, **Y**, **Links**, **Rechts**, **Oben**, **Unten,** **Breite**, **Höhe**, **Score**, **Rotation**, **Skaliert**, **Farbwert**.

<table id="bkmrk-operation-beschreibu-2" style="width: 76.9048%;"><thead><tr><th style="width: 11.9364%;">**Operation**</th><th style="width: 88.0504%;">**Beschreibung der Manipulation**</th></tr></thead><tbody><tr><td style="width: 11.9364%;">+</td><td style="width: 88.0504%;">Addition: VNew = linker Wert + rechter Wert</td></tr><tr><td style="width: 11.9364%;">–</td><td style="width: 88.0504%;">Subtraktion: VNew = linker Wert – rechter Wert</td></tr><tr><td style="width: 11.9364%;">\*</td><td style="width: 88.0504%;">Multiplikation: VNew = linker Wert \* rechter Wert</td></tr><tr><td style="width: 11.9364%;">/</td><td style="width: 88.0504%;">Division: VNew = linker Wert / rechter Wert</td></tr><tr><td style="width: 11.9364%;">Runden</td><td style="width: 88.0504%;">Gerundeter Wert: VNew = runden (linker Wert) auf Anzahl der Dezimalstellen (rechter Wert)</td></tr><tr><td style="width: 11.9364%;">Zufällig</td><td style="width: 88.0504%;">Random: VNew = Zufallswert (zwischen 0 und 1)</td></tr></tbody></table>

#### Text und Passwort

Bei Passwörtern beziehen sich alle Manipulationen nicht auf das Passwort selbst, sondern auf den Namen, nach dem gesucht wird. Wenn zum Beispiel die Variable „**Passwort**" auf „**Google**" gesetzt wird, wird das System bei der nächsten Verwendung der Variable versuchen, das Passwort „**Google**" aus der Datenbank abzurufen, anstatt den Wert des Passworts selbst auf „**Google**" zu ändern.

Gültige Ergebnisfeldtypen: **Alle**

<table id="bkmrk-operation-beschreibu-3" style="width: 100%; height: 531.975px;"><thead><tr style="height: 33.3097px;"><th style="width: 16.2081%; height: 33.3097px;">**Operation**</th><th style="width: 83.781%; height: 33.3097px;">**Beschreibung der Manipulation**</th></tr></thead><tbody><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Großbuchstaben</td><td style="width: 83.781%; height: 46.5057px;">Wandelt Text aus dem Feld „**Rechter Wert**" in Großbuchstaben um.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Kleinbuchstaben</td><td style="width: 83.781%; height: 46.5057px;">Wandelt Text aus dem Feld „**Rechter Wert**" in Kleinbuchstaben um.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Zusammenfügen</td><td style="width: 83.781%; height: 46.5057px;">Verknüpft zwei Zeichenketten. Fügt den linken Wert dem rechten Wert hinzu.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Ersetzen</td><td style="width: 83.781%; height: 46.5057px;">Spezifizierter Wert, wenn konstant, sonst nicht verwendet. Die Teile eines erfassten Texts, die mit den im Feld „**Linker Wert**" eingegebenen Zeichen übereinstimmen, werden durch die im Feld „**Rechter Wert**" eingegebenen ersetzt.</td></tr><tr style="height: 63.3097px;"><td style="width: 16.2081%; height: 63.3097px;">Extrahieren</td><td style="width: 83.781%; height: 63.3097px;">Nach RegEx formatierte Zeichenkette. Definition des Formats: &lt;Suchen&gt; &lt;Ersetzen&gt;&lt;Optionen&gt;. Extrahiert Teilzeichenketten, wie durch eine RegEx-Anweisung im zweiten Argument beschrieben, z. B.: „/(\\d{4})/$1" extrahiert die ersten vier in der Zeichenkette gefundenen Ziffern (siehe Kapitel 4.7.3.1.3.1 sowie weitere Informationen zu RegEx in Kapitel 4.7.3.2.2.1.4).</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Linker Teil bis</td><td style="width: 83.781%; height: 46.5057px;">Gibt die ersten „n" Zeichen einer Zeichenfolge zurück. Beispiel: „Linker Teil bis 1" von „ABC" = „A". Der linke Wert ist der Eingabetext und der rechte Wert die Anzahl der zurückgegebenen Zeichen.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Rechter Teil ab</td><td style="width: 83.781%; height: 46.5057px;">Gibt alle Zeichen rechts von der Position „n" zurück. Beispiel: „Rechter Teil ab 1" von „ABC" = „BC". Der linke Wert ist der Eingabetext und der rechte Wert das Startzeichen, ab dem gelesen wird.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Rechter Anzahl</td><td style="width: 83.781%; height: 46.5057px;">Gibt die letzten „n" Zeichen einer Zeichenkette zurück. Beispiel: „Rechter Teil (Anzahl) 1" von „ABC" = „C". Der linke Wert ist der Eingabetext und der rechte Wert die Anzahl der Zeichen von rechts, die gelesen werden.</td></tr><tr style="height: 63.3097px;"><td style="width: 16.2081%; height: 63.3097px;">Zwischenablage zuweisen</td><td style="width: 83.781%; height: 63.3097px;">Text im Speicher abgelegt. Die Variable wird mit dem im Speicher abgelegten Text überschrieben (STRG + C). Keine Eingabe von linker/rechter Wert notwendig.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.2081%; height: 46.5057px;">Formatieren</td><td style="width: 83.781%; height: 46.5057px;">Der linke Wert wird durch die Definition des rechten Werts formatiert. Weitere Informationen siehe unten.</td></tr></tbody></table>

#### Datum &amp; Uhrzeit

Gültige Ergebnisfeldtypen: **Konstanter Wert**

<table id="bkmrk-operation-beschreibu-4" style="width: 84.2857%; height: 237.614px;"><thead><tr style="height: 29.7017px;"><th style="width: 25.6225%; height: 29.7017px;">**Operation**</th><th style="width: 74.3641%; height: 29.7017px;">**Beschreibung der Manipulation**</th></tr></thead><tbody><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Jahre hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Jahren zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Monate hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Monaten zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Tage hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Tagen zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Stunden hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Stunden zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Minuten hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Minuten zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Sekunden hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Sekunden zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr><tr style="height: 29.7017px;"><td style="width: 25.6225%; height: 29.7017px;">Millisekunden hinzufügen</td><td style="width: 74.3641%; height: 29.7017px;">Fügt die angegebene Anzahl von Millisekunden zur Variable **Datum &amp; Uhrzeit** hinzu.</td></tr></tbody></table>

#### Timer

Gültiger Ergebnisfeldtyp: **Keine**

<table id="bkmrk-operation-beschreibu-5"><thead><tr><th>**Operation**</th><th>**Beschreibung der Manipulation**</th></tr></thead><tbody><tr><td>Starten</td><td>Speichert die aktuelle Zeit.</td></tr><tr><td>Stoppen</td><td>Subtrahiert die Startzeit von der aktuellen Zeit und speichert die Dauer im Datumsformat.</td></tr></tbody></table>

### Spezifische Erklärungen zu Operationen

#### Extrahieren

Der Variablenmanipulationsoperator **Extrahieren** erlaubt es, Teile eines Texts aus anderen Variablen oder Ergebnisfeldern vom Typ **Text** mithilfe regulärer Ausdrücke zu extrahieren. Reguläre Ausdrücke (RegEx) mit dem Variablenmanipulationsoperator **Extrahieren** folgen derselben Syntax wie im Abschnitt **Text suchen** für die Anweisung **Ersetzen** beschrieben. Die integrierte .NET-Engine für reguläre Ausdrücke in **EMMA** verwendet die folgende Syntax:

`[<Trennzeichen>]<Erfassungs-Muster>[<Trennzeichen><Ergebnis-Muster>[<Trennzeichen><Optionen>]]`

Die Angaben in eckigen Klammern sind dabei optional.

Es ist ausreichend, nur ein „Erfassungs-Muster" (bzw. Suchmuster) anzugeben. In diesem Fall wird der Textanteil extrahiert, der dem Erfassungsmuster entspricht.

Beispiel:

`/This is \w+!/$0/i`

Dieser Ausdruck extrahiert den Satz `This is EMMA!` sowie alle anderen Sätze, die mit `This is` beginnen (unabhängig von der Groß- und Kleinschreibung), danach ein Wort mit mindestens einem Wortzeichen enthalten und durch das Ausrufezeichen `!` abgeschlossen werden.

#### Parameter (Flags)

Der Grund dafür, dass die Groß- und Kleinschreibung nicht berücksichtigt wird, liegt in der Verwendung des Parameters „i“ am Ende des regulären Ausdrucks, der hinter einem Schrägstrich gesetzt wird.

Parameter bzw. Flags ermöglichen es dem Benutzer, bestimmte Suchoptionen mit regulären Ausdrücken ein- und auszuschalten, wie in unserem Beispiel das Ignorieren der Groß- und Kleinschreibung.

Während reguläre Ausdrücke im Schritt ***Finden*** stets das globale Flag `/g` (für alle Vorkommen) verwenden – welches nicht explizit angegeben werden muss –, können beim Operator **Extrahieren** beliebige Flags verwendet werden. So ermöglicht beispielsweise das Flag `/m`, dass die Eingabe als mehrzeiliger Text behandelt wird. Dadurch beziehen sich die Anker `^` und `$` auf den Beginn bzw. das Ende jeder einzelnen Zeile innerhalb der Eingabe und nicht auf den Anfang und das Ende der gesamten Zeichenkette.

Weitere nützliche Flags sind in der folgenden Tabelle aufgeführt.

<table id="bkmrk-flag-erl%C3%A4uterung-%2Fx-" style="width: 100%;"><thead><tr><th style="width: 6.55265%;">**Flag**</th><th style="width: 93.4365%;">**Erläuterung**</th></tr></thead><tbody><tr><td style="width: 6.55265%;">/x</td><td style="width: 93.4365%;">Ermöglicht das Hinzufügen von Leerzeichen zum Muster für reguläre Ausdrücke, um diese lesbarer zu machen. Die Leerzeichen werden dabei ignoriert.</td></tr><tr><td style="width: 6.55265%;">/n</td><td style="width: 93.4365%;">Es werden nur benannte Erfassungsgruppen extrahiert.</td></tr><tr><td style="width: 6.55265%;">/m</td><td style="width: 93.4365%;">Behandelt den Quelltext als mehrzeilige Zeichenkette. Die Anker ^ und $ beziehen sich dabei auf den Anfang bzw. das Ende der jeweiligen Zeile.</td></tr><tr><td style="width: 6.55265%;">/s</td><td style="width: 93.4365%;">Der gesamte Ausdruck wird als eine einzige Zeile behandelt, d. h. ^ und $ sollen dem Anfang bzw. dem Ende des gesamten Quelltexts entsprechen.</td></tr><tr><td style="width: 6.55265%;">/i</td><td style="width: 93.4365%;">Groß- und Kleinschreibung wird ignoriert (Groß- und Kleinbuchstaben sind gleich).</td></tr><tr><td style="width: 6.55265%;">/o</td><td style="width: 93.4365%;">Der ursprüngliche OCR-Text (Optical Character Recognition) wird mit Sonderzeichen zurückgegeben, aber mit seinem Standard-Gegenstück abgeglichen:   
- Zeilenumbruch: \\u2028 (\\n im RegEx-Erfassungsmuster)   
- Absatzwechsel: \\u2029 (\\r im RegEx-Erfassungsmuster)   
- Tabulator: \\u0009 (\\t im RegEx-Erfassungsmuster)</td></tr><tr><td style="width: 6.55265%;">/t</td><td style="width: 93.4365%;">Die Sonderzeichen des ursprünglichen OCR-Texts werden in ihre üblichen RegEx-Entsprechungen umgewandelt (siehe oben).</td></tr></tbody></table>

*Tabelle 6 – Tabellarische Übersicht der verfügbaren Flags*

#### Trennzeichen (Delimiter)

Trennzeichen wie der Schrägstrich `/` in unserem Beispiel umschließen den regulären Ausdruck. Zur Vereinfachung kann das Trennzeichen am Anfang weggelassen werden, wenn es ein Schrägstrich `/` ist. Möchte man ein anderes Trennzeichen verwenden, so muss dieses als erstes Zeichen eingegeben werden. Jedes andere Zeichen, z. B. `!`, `#`, `%`, `+` oder `~`, kann ebenfalls verwendet werden. Dies ist nützlich, wenn der reguläre Ausdruck viele Schrägstriche enthält, die umgangen werden müssen.

#### Ergebnismuster (Extract Pattern)

Das Ergebnismuster ist der wichtigste Teil der Syntax, da es angibt, wie die Ausgabe aussehen soll. Es ist eine optionale Anweisung. Wenn keine Eingabe erfolgt, wird `$0` angenommen.

`$0` gibt den gesamten Text zurück, auf den die regulären Ausdrücke passen, während `$1`, `$2`, `$3` usw. die Treffer der ersten, zweiten, dritten usw. Erfassungsgruppe zurückgeben, die in Klammern definiert sind.

Der reguläre Ausdruck `/(to be) or (not to be)/$2 or $1`

extrahiert

`not to be or to be`

aus dem Text

`to be or not to be`

Erfassungsgruppen können auch benannt werden. Mit der Syntax `(?<named_group>\w+)` oder alternativ `(?'named_group'\w+)` für die ansonsten unbenannte Erfassungsgruppe `(\w+)` wird diese Gruppe `named_group` genannt. Der Vorteil ist, dass dieser Name auch im Extraktions-Statement verwendet wird.

Wenn wir eine lange Inventarliste von Produkten haben und den Bestand an Äpfeln, Bananen, Kiwis und Mangos für die spätere Verwendung extrahieren wollen, können wir die Erfassungsgruppen entsprechend benennen, um sicherzustellen, welche extrahierte Zahl verwendet wird. So muss man sich nicht auf die Nummerierung $1, $2, $3 und $4 verlassen, deren Zuordnung man vielleicht vergisst.

Der reguläre Ausdruck

`apples:\s(?<apples>\d+)|bananas:\s(?<bananas>\d+)|kiwis:\s(?<kiwis>\d+)|mangos:\s(?<mangos>\d+)/${apples},${bananas},${kiwis},${mangos}`

gibt für den Text

```
inventory of bananas: 9000

inventory of apples: 1250

inventory of mangos: 875

inventory of kiwis: 7500

```

folgendes Ergebnis aus:

`1250,9000,7500,875`

Dabei sind alle abgefragten Werte per Komma voneinander getrennt. Wenn beispielsweise aus der folgenden Liste der aktuellen Lieferungen von Bananen:

```
delivery of bananas on 10.09.2021: 9000
delivery of bananas on 19.08.2021: 8000

```

die Bestellmengen der letzten zwei Lieferungen extrahiert werden sollen, kann der folgende reguläre Ausdruck verwendet werden:

`:\s(\d+)/$2[1];$1[2]`

Das Ergebnis ist dann:

`9000;8000`

Erklärung:

Das Erfassungsmuster `\s(\d+)` definiert, das alle zusammenhängenden Ziffern in d 1 übernommen werden sollen, wenn sie im Text nach einem Doppelpunkt gefolgt von mindestens einem Leerzeichen stehen. Da die Operation **Extrahieren** den Text zeilenweise auswertet, wird für jede Zeile eine solche Erfassungsgruppe 1 erstellt.

Das Ergebnismuster `$2[1];$1[2]` gibt an, dass aus den Ergebnissen der Erfassung mit dem Ergebnismuster die Erfassungsgruppe 2 „($2)“ der ersten Zeile „\[1\]“, danach ein Semikolon und anschließend die Erfassungsgruppe 1 „($1)“ der zweiten Zeile „\[2\]“ ausgegeben werden soll.

Die Zahlen in eckigen Klammern beziehen sich dabei auf das jeweilige Ergebnis des Erfassungsmusters. Außerdem ist `$n[1]` gleich `$n`, also `$0[1]` ist gleich `$0`, `$1[1]` gleich `$1` und so weiter. `$n[0]` liefert alle Übereinstimmungen im CSV-Format: `$n[1], $n[2], ...`

#### Zusätzliche Informationen

Weitere Informationen über die Sprache der regulären Ausdrücke sind im Internet verfügbar:   
Microsoft .NET Dokumentation: [Sprachelemente für reguläre Ausdrücke – Kurzübersicht](https://learn.microsoft.com/de-de/dotnet/standard/base-types/regular-expressions)

### Operation „Formatieren“

Manchmal ist es notwendig, Werte wie Daten oder Preise in einem bestimmten Format in ein Formular oder eine Anwendung zu übergeben. Dies kann erreicht werden, indem der betreffende Wert mithilfe der Operation „Formatieren“ einer Variablen vom Typ „Text“ zugewiesen wird. Um z. B. nur den „Tagesanteil" einer Variable namens `The_Timer` vom Typ „Datum&amp;Uhrzeit“ zu erhalten, kann die Operation „Formatieren“ mit einem Format-String von D wie folgt verwendet werden:

[![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706883936595.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706883936595.png)   
*Abbildung 38 – Schritteigenschaften – Variablenmanipulation*

Dadurch wird der Datumsanteil der Variable „The\_Timer“ in die Variable „F\_Time“ geschrieben.

[![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706883941761.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706883941761.png)  
*Abbildung 39 – Schritteigenschaften – Variablenmanipulation 2*

Es gibt zahlreiche Formatspezifikationen für die verschiedenen Variablentypen:

<table id="bkmrk-typ-der-variable-wer"><thead><tr><th>**Typ der Variable**</th><th>**Wert der Variable**</th><th>**Format-spezifikation**</th><th>**Ergebnis**</th><th>**Beschreibung**</th></tr></thead><tbody><tr><td>Dezimalzahl</td><td>1234,567</td><td>0.00</td><td>1234,47</td><td>Ausgabe mit zwei Nachkommastellen  
**Wichtig:** In der Formatspezifikation dient ein Punkt (kein Komma) als Dezimaltrennzeichen.</td></tr><tr><td>Dezimalzahl</td><td>1234,56</td><td>0,000.00</td><td>1.234,56</td><td>Ausgabe mit Tausenderpunkt  
**Wichtig:** In der Formatspezifikation dient ein Komma (kein Punkt) als Tausendertrennzeichen.</td></tr><tr><td>Dezimalzahl</td><td>123,45</td><td>C</td><td>123,45€</td><td>Ausgabe in lokaler Währung</td></tr><tr><td>Dezimalzahl</td><td>123,4567</td><td>F1</td><td>123,5</td><td>Runden auf eine Nachkommastelle</td></tr><tr><td>Dezimalzahl</td><td>0.6578</td><td>P1</td><td>65,8%</td><td>Ausgabe in Prozent und auf eine Nachkommastelle gerundet</td></tr><tr><td>Ganzzahl</td><td>1234</td><td>D6</td><td>001234</td><td>Sechsstellige Ausgabe mit führenden Nullen</td></tr><tr><td>Ganzzahl</td><td>1234</td><td>10:D</td><td>......1234</td><td>Ausgabe von 10 Zeichen mit führenden Leerzeichen, rechtsbündig</td></tr><tr><td>Ganzzahl</td><td>1234</td><td>-10:D</td><td>1234......</td><td>Ausgabe von 10 Zeichen mit folgenden Leerzeichen, linksbündig</td></tr><tr><td>Ganzzahl</td><td>256</td><td>X</td><td>FF</td><td>Ausgabe als Hexadezimalzahl</td></tr><tr><td>Datum&amp;Uhrzeit</td><td>2009-06-15T13:45:30</td><td>D</td><td>Montag, 15. Juni 2009</td><td>Ausgabe des Datums in regionaler Langform</td></tr><tr><td>Datum&amp;Uhrzeit</td><td>2009-06-15T13:45:30</td><td>d</td><td>15.06.2009</td><td>Ausgabe des Datums im regionalen Kurzformat</td></tr><tr><td>Datum&amp;Uhrzeit</td><td>2009-06-15T13:45:30</td><td>T</td><td>13:45:30</td><td>Ausgabe der Zeit im 24-Stunden-Format</td></tr><tr><td>Datum&amp;Uhrzeit</td><td>2009-06-15T13:45:30</td><td>yyyyMMdd</td><td>20090615</td><td>Ausgabe des Jahrs (vierstellig), gefolgt von Monat und Tag (zweistellig)</td></tr></tbody></table>

Die vollständige Liste der verfügbaren Formatspezifikationen ist im Internet verfügbar:   
[Microsoft .Net Standardmäßige Zahlenformatzeichenfolgen](https://learn.microsoft.com/de-de/dotnet/standard/base-types/standard-numeric-format-strings)

# Ergebnisse von Prozessschritten

Wenn ein Schritt ausgeführt wird, erzeugt er eine Reihe von Ergebnissen. Auf diese Schritte kann bei der Konfiguration zukünftiger Schritte, im Schalterschritt zu Vergleichszwecken sowie bei der Manipulation von Kontextvariablen Bezug genommen werden.

<table id="bkmrk-schrittergebnis-typ-" style="width: 100%; height: 674.148px;"><thead><tr style="height: 29.7017px;"><th style="width: 16.6847%; height: 29.7017px;">**Schrittergebnis**</th><th align="center" style="width: 12.8699%; height: 29.7017px;"><div style="width: 90;">**Typ**</div></th><th style="width: 70.4345%; height: 29.7017px;">**Erläuterung**</th></tr></thead><tbody><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Erfüllt</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Bolean</td><td style="width: 70.4345%; height: 29.7017px;">Prozessschritt wurde erfolgreich ausgeführt? (wahr/falsch)</td></tr><tr style="height: 46.5057px;"><td style="width: 16.6847%; height: 46.5057px;">Nächster Schritt gefunden</td><td align="center" style="width: 12.8699%; height: 46.5057px;">Bolean</td><td style="width: 70.4345%; height: 46.5057px;">Nachfolger wurde für die im Schritt definierte Verzweigungsbedingung und das TaskFulfilled-Ergebnis gefunden? (wahr/falsch)</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Nächster Schritt ID</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Ganzzahl</td><td style="width: 70.4345%; height: 29.7017px;">ID des nächsten Schritts.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">X/Y</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">X- oder Y-Koordinate des Ergebnisses.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Links</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Abstand vom linken Bildschirmrand zum linken Rand des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Rechts</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Abstand vom linken Bildschirmrand zum rechten Rand des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Oben</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Abstand vom oberen Rand des Bildschirms zum oberen Rand des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Unten</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Abstand vom oberen Rand des Bildschirms zum unteren Rand des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Breite</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Breite des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Höhe</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Höhe des gefundenen Textfelds in Pixeln.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Anzahl</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Ganzzahl</td><td style="width: 70.4345%; height: 29.7017px;">Anzahl der Treffer.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.6847%; height: 46.5057px;">Startzeit</td><td align="center" style="width: 12.8699%; height: 46.5057px;">Datum&amp;Uhrzeit</td><td style="width: 70.4345%; height: 46.5057px;">Zeitpunkt, zu dem der Prozessschritt ausgeführt wurde.</td></tr><tr style="height: 46.5057px;"><td style="width: 16.6847%; height: 46.5057px;">Laufzeit</td><td align="center" style="width: 12.8699%; height: 46.5057px;">Datum&amp;Uhrzeit</td><td style="width: 70.4345%; height: 46.5057px;">Zeit in Millisekunden, die für die Ausführung benötigt wurde.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Score</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Wahrscheinlichkeit des Ergebnisses (0 &lt; Score &lt; 1).</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Rotation</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Rotation des Musters.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Skalierung</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Auftretende Skalierung des Musters.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Farbwert</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Dezimalzahl</td><td style="width: 70.4345%; height: 29.7017px;">Farbübereinstimmungsfaktor (0 &lt; Farbe &lt; 1).</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Gefundener Text</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Text</td><td style="width: 70.4345%; height: 29.7017px;">Der erkannte Text (über die Schritte ***Finden*** und ***Hören***).</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Seitennummer</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Ganzzahl</td><td style="width: 70.4345%; height: 29.7017px;">Aktuelle Seitennummer.</td></tr><tr style="height: 29.7017px;"><td style="width: 16.6847%; height: 29.7017px;">Ergebnisindex</td><td align="center" style="width: 12.8699%; height: 29.7017px;">Ganzzahl</td><td style="width: 70.4345%; height: 29.7017px;">Die Trefferzahl der von **EMMA** gefundenen Ergebnisse.</td></tr></tbody></table>

# Prozess importieren

**EMMA Studio** unterstützt sowohl **normale** als auch **gesicherte Prozessimporte**. Die Typen von Prozessdateien werden anhand ihrer Dateierweiterung unterschieden:

- **Gesicherter Prozess** (`.semtc`): Diese Dateien sind für zusätzliche Sicherheit verschlüsselt. Um sie zu importieren, muss der Benutzer ein Token angeben, um seine Zugriffsrechte zu verifizieren und die Datei zu entschlüsseln.
- **Normaler Prozess** (`.emtc`): Diese Dateien können ohne zusätzliche Schritte oder Überprüfung direkt importiert werden. Sie sind für Standardanwendungsfälle konzipiert und erfordern kein Token.

### Prozess importieren

Vor dem Import erscheint ein Dialogfeld mit diesen Optionen:

- - **Aktuellen Prozess überschreiben:** Der vorhandene Prozess wird überschrieben und der importierte Prozess wird im aktuell geöffneten Fenster geöffnet.
    - **Als neuer Prozess:** Der Prozess wird in neuem Prozessfenster geöffnet.
    - **Abrechen:** Fenster wird geschlossen

Die gewünschte Option auswählen und mit der Dateiauswahl fortfahren.

[![image.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/scaled-1680-/99zimage.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-02/99zimage.png)

#### Importieren

- Öffne **EMMA Studio**.
- Klicke im Menü auf ***Datei*** und wähle ***Importieren***.
- Klicke auf ***Prozess*** und wähle die Datei, die du **importieren** möchtest (.emtc oder .semtc).

#### Gesicherten Prozess importieren (.semtc)

Bei einem gesicherten Prozess sind die folgenden zusätzlichen Schritte erforderlich:

##### Schritt 1: Token eingeben

- Gib das beim Kauf bereitgestellte Token in das Feld ein, wenn du dazu aufgefordert wirst.
- Das Token ist erforderlich für die Verifizierung und Entschlüsselung der Datei.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/4ckimage.png)](http://192.168.5.129/uploads/images/gallery/2025-06/4ckimage.png)

##### Schritt 2: Verifizierung

- **EMMA Studio** verifiziert das eingegebene Token automatisch.

##### Schritt 3: Entschlüsselung der Datei

- Nach der Verifizierung entschlüsselt **EMMA Studio** die Datei und macht sie einsatzbereit.

#### Normalen Prozess importieren (.emtc)

Bei normalen Prozessen gestaltet sich der Import noch einfacher: Nach der Dateiauswahl wird der Import sofort durchgeführt, ohne dass ein Token oder eine Entschlüsselung erforderlich ist.

#### Überprüfen und Abschließen des Imports

- Nachdem die Datei importiert wurde, erscheint ein Fenster mit den Einzelheiten zum Vorgang.
- Wenn die Datei verschachtelte Prozesse enthält, kannst du auswählen, welche davon importiert werden sollen.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/N16image.png)](http://192.168.5.129/uploads/images/gallery/2025-06/N16image.png)

### Verwandte Themen

- [Prozesse exportieren](http://192.168.5.129/books/emma-studio-27-manual/page/export-process)

# Prozess exportieren

**EMMA Studio** bietet zwei Optionen für den Export von Prozessen: **normaler Prozess** und **gesicherter Prozess**. Diese Optionen ermöglichen es dem Benutzer, Prozesse entweder mit oder ohne Verschlüsselung zu exportieren, je nach dem gewünschten Sicherheitsniveau. Die folgenden Schritte beschreiben, wie man die Exportfunktion nutzt.

[![image.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/g8Yimage.png)](http://192.168.5.129/uploads/images/gallery/2025-06/g8Yimage.png)

### Prozess exportieren

1. **Menü *Datei → Exportieren* öffnen**
    
    
    - Öffne das Menü ***Datei*** und wähle die Option ***Exportieren***.
    - Klicke auf ***Prozess***, um die Exportkonfigurationsmaske zu öffnen.
2. **Export konfigurieren**
    
    
    - Die Exportmaske bietet Konfigurationseinstellungen für den Exportprozess. Benutzer können zwischen einem **normalen** und einem **gesicherten** Prozess wählen:  
        
        - **Normaler Prozess**: Der exportierte Prozess kann in andere **EMMA**-Instanzen importiert werden, ohne dass ein Token erforderlich ist.
        - **Gesicherter Prozess**: Während des Importvorgangs ist ein Token erforderlich, um zusätzliche Sicherheit zu gewährleisten.
3. **Optionen in der Exportmaske**
    
    
    - **Kontrollkästchen „Sicher“**: Mit dieser Option wird die Verschlüsselung aktiviert und der exportierte Prozess abgesichert.
    - **Feld „Schlüssel“**: Gib eine benutzerdefinierte Zeichenfolge manuell ein oder erstelle eine über den Button ***Neu***. Mit diesem Schlüssel wird die exportierte Datei verschlüsselt.
    - **Kontrollkästchen „Editierbar“**: Wenn diese Option aktiviert ist, kann der Benutzer nach dem Import Änderungen an dem Prozess vornehmen.
    - **Kontrollkästchen „Exportierbar“**: Wenn diese Option aktiviert ist, kann der Benutzer den Prozess nach dem Import erneut exportieren.
    - **Feld „Sicherheitsschlüssel“**: Wenn diese Option aktiviert ist, kann der Benutzer den Prozess nach dem Import erneut exportieren. Dieses zusätzliche Schlüsselfeld wird verwendet, um den Sicherheitsschlüssel für die exportierte Datei zu definieren. Der Schlüssel kann manuell eingegeben oder automatisch generiert werden.
4. **Exports abschließen**
    
    
    - Nachdem du die Einstellungen vorgenommen hast, klicke auf den Button **Genehmigen**.
    - Es erscheint eine neue Maske, in der du angeben kannst, wo die exportierte Datei gespeichert werden soll.

### Wichtiger Hinweis

- Der während des Exportvorgangs verwendete Verschlüsselungscode wird nicht direkt beim Importvorgang verwendet. Stattdessen wird ein Token erzeugt, das für den Import des gesicherten Prozesses benötigt wird.

Diese Schritte ermöglichen einen effektiven und schnellen Export der Prozesse. Gleichzeitig wird für ein hohes Maß an Sicherheit und Flexibilität beim Import gesorgt.

# Prozess drucken

Zu Dokumentationszwecken kann der aktuell ausgewählte Prozess in eine PDF-Datei exportiert werden. Beim Exportieren können drei verschiedene Teile des Prozesses einbezogen werden:

### Grafisches Layout

Das grafische Layout des Prozesses wird exportiert und zeigt die Position, den Namen, die ID und die Verbindungen der einzelnen Schritte an. Wenn das Layout zu groß ist und nicht auf eine einzige Seite passt, wird es auf mehrere Seiten aufgeteilt. Dieses Layout entspricht dem, was auf der linken Seite des Bildschirms in der Standardprozessansicht angezeigt wird.

### Schritteigenschaften

Die Eigenschaften der einzelnen Schritte können in eine Tabelle exportiert werden. Diese Tabelle enthält den Schrittnamen, die Schritt-ID, Kommentare und spezifische Eigenschaften, die mit jedem Schritt verbunden sind.

### Variablen

Alle Prozessvariablen werden in eine Tabelle exportiert. Diese Tabelle enthält die ID, den Namen, den Typ und den Anfangswert aller Variablen.

# Prozesse wiederherstellen

**EMMA Studio** speichert geöffnete Projekte jetzt automatisch in regelmäßigen Abständen lokal. Nach einem unerwarteten Absturz können Projekte beim Neustart über den Dialog „Projekte wiederherstellen“ wiederhergestellt werden.

[![12198dfb-8d80-4815-a0be-5a54d85156c0.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/VzA12198dfb-8d80-4815-a0be-5a54d85156c0.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/VzA12198dfb-8d80-4815-a0be-5a54d85156c0.png)

# Schritteigenschaften



# Start

Der Prozessschritt **Start** ist der erste Schritt in jedem Prozessablauf. Es gibt nur einen Startschritt pro Prozess, der den Startpunkt des Prozesses definiert. Es handelt sich um einen Prozessschritt, der bereits am Anfang eines jeden Prozesses existiert und nicht gelöscht oder dupliziert werden kann. Er kann nicht explizit über das Menü eingefügt werden, sondern wird von **EMMA Studio** automatisch erstellt, wenn ein neuer Prozess angelegt wird.

  
[![](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/image-1750255805202.png)](http://192.168.5.129/uploads/images/gallery/2025-06/image-1750255805202.png)

Während dieser Prozessschritt selbst keine andere Funktion als den Beginn der Ausführung hat, kann er verwendet werden, um z. B. die Variablen für den weiteren Ablauf vorzubereiten.

# Finden

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719473832434.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719473832434.png)

Beim Erstellen eines Prozesses ist ***Finden*** einer der wichtigsten Schritttypen, da die meisten Prozesse in **EMMA** auf Bildvergleichen basieren. Das Verständnis dessen, was angezeigt wird, ist für nahezu alle Prozesse entscheidend. Man kann beispielsweise nach „Objekt“, „Text“, „RegEx“, „Bild“, „Sprachen“ und „Freeze“ suchen. Der Unterschied zwischen Objekt und Bild – beides bildbasierte Suchen – wird unter [Objektkomposition](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/objekt) beschrieben.

Bei einer Suche mit dem **Gegenstand** „Objekt“ oder „Bild“ sind für die Ausführung des Prozessschritts ***Finden*** Bilddaten erforderlich. Diese Bildausschnitte müssen zuvor erstellt werden und unter ***Sehen*** vorhanden sein.

Bei Auswahl der Option „Text“ wird der im Bild vorhandene Text extrahiert und der vorab definierte Text darin gesucht. Dies erfolgt durch eine OCR-Erkennung (Optical Character Recognition bzw. optische Zeichenerkennung).

Mit „RegEx“ (reguläre Ausdrücke) kann anstelle eines bestimmten Texts auch nach Textmustern gesucht werden.

Mit „Sprachen“ kann untersucht werden, wie hoch der Anteil einer bestimmten Sprache in Prozent ist, beispielsweise auf einer Website. Die Summe der Prozentwerte kann dabei 100 übersteigen, zum Beispiel aufgrund von Anglizismen, die mehreren Sprachen zugeordnet werden. Ein einfacher Linksklick auf den Prozessschritt ***Finden*** liefert unter „Gefundener Text“ die Ausgabe des gefundenen Texts.

„Freeze“ (eingefrorener Bildschirm) wird erkannt, indem zwei Bilder miteinander verglichen werden. Die oben dargestellte Eingabemaske variiert je nach dem Element, das gesucht werden soll.

Wenn ein Parameter verhindert, dass der Prozessschritt ausgeführt werden kann, so wird das zugehörige Eingabefeld mit einer roten Umrandung angezeigt. Zum Beispiel, wenn bei einer objektbasierten Suche keine Bildkomposition ausgewählt wurde.

### Eingabefelder

#### Tab „Find Eigenschaften“:

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719473884298.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719473884298.png)

##### Gegenstand

Hier kann zwischen der Suche nach „Objekt“, „Text“, „RegEx“, „Bild“, „Sprachen“ und „Freeze“ ausgewählt werden. Abhängig von der getroffenen Auswahl können sich die möglichen Eingabefelder verändern.

##### Warte vor Start (ms)

Die Wartezeit ab der Beendigung des vorhergehenden Prozessschritts bis zum Start der Suche. Der Zweck hinter dieser Option ist, eventuell vorhandene Animationen oder die Ladezeit einer Homepage zu berücksichtigen, um das Suchergebnis nicht zu verfälschen.

##### Timeout (ms)

Die Dauer, nach der die Suche als erfolglos abgebrochen werden soll. Bei Auswahl von „Freeze“ bezieht sich dieser Wert auf die Zeit zwischen den Bildern, die miteinander verglichen werden sollen.

##### Objektnummer

(Nur für „Objekt“ und „Bild“) ID der Bildkomposition. Über den Tab **Zu suchendes Objekt** kannst du nach dem entsprechenden Objekt suchen oder die ID direkt in das Feld eingeben.

##### Minimaler Score

In der Ergebnisliste werden nur Treffer ausgegeben, deren Bewertung gleich oder höher als der minimale Score ist.

- Standardwert: 0.9
- Wertvorschläge: {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}
- Typischer Wertebereich: 0 ≤ minimaler Score ≤ 1
- Minimale Schrittweite: 0,01
- Empfohlene Schrittweite: 0,05

##### Suchtext

(Nur für „Text“ und „RegEx“) Eingabe des Texts, der im Bild gesucht und gefunden werden soll.

##### Groß-/Kleinschreibung beachten

(Nur für „Text“ und „RegEx“) Auswahl, ob die Groß- und Kleinschreibung beim Textvergleich beachtet werden soll oder nicht.

##### Quelldokument

Unter Quelldokument wird festgelegt, wo gesucht werden soll. Zur Auswahl steht auf dem Bildschirm, in einer Datei oder in einem Ergebnisfeld eines vorherigen Prozessschritts.

Bei Auswahl des Eingabetyps „Konstanter Wert“, kann entweder „Datei“ oder „Bildschirm“ als Quelle angegeben werden.  
Beim Eingabetyp „Ergebnisfeld“ kannst du auch auf Ergebnisse aus früheren Schritten im selben Prozess zugreifen.

Die Option „Ergebnisfeld“ kann helfen, die Anzahl der OCR-Lesevorgänge zu reduzieren, was zu Einsparungen bei den Lizenzgebühren führen kann. Wenn der Text bereits in einem früheren Schritt gelesen wurde, kann er erneut verwendet werden, ohne dass er noch einmal eingelesen werden muss. Stattdessen wird einfach auf den bereits erkannten Text verwiesen.

##### Datei

Wenn bei Quelldokument „Datei“ ausgewählt ist, wird der Inhalt der Datei durchsucht.

##### Seiten

Wenn eine mehrseitige Datei als Quelle für die Suche verwendet wird, können in diesem Eingabefeld die Seiten angegeben werden, die durchsucht werden sollen. Die Angabe erfolgt dabei ähnlich wie bei der Druckausgabe durch eine Liste von Seitennummern oder Bereichen, z. B.:

- für alle Seiten ab der ersten Seite: „1–“
- für die Seiten 1 bis 3: „1–3“
- für die Seiten 1, 2 und 5: „1,2,5“
- für die letzte Seite „–1“

#### Tab „Text Eigenschaften“

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719474313116.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719474313116.png)

Nach Auswahl der Option „Text“ kannst du im Tab **Text Eigenschaften** die Einstellungen für die Texterkennung anpassen. Mit Ausnahme von **Ergebnisauswahl** und **Variablen** können alle anderen Tabs ignoriert werden.

Die wichtigsten Einstellungen werden in den folgenden Abschnitten beschrieben.

##### Profil

Hier wird das Hauptprofil für die OCR-Textumwandlung definiert. Es gibt fünf verschiedene Profile.

Standardwert: **Default**

Werteliste:

- **Default**: Diese Einstellung ist für Dokumente mit einer einfachen Struktur vorgesehen.
- **Aus**: Dokumentenanalyseverfahren wie Farb- und Schriftanalyse werden übersprungen. Diese Option funktioniert vor allem bei Bildschirmen mit wenigen bis keinen nicht-textbasierten Inhalten.
- **Text**: Diese Option gibt der Texterkennung Vorrang vor der Kantenerkennung.
- **Tabelle**: Diese Einstellung bewirkt, dass **EMMA** versucht, Tabellen anstelle von einfachen Kanten zu finden (Kästchenbildung).
- **Tabelle erzwingen**: Diese Option geht einen Schritt weiter und zwingt **EMMA**, alle möglichen Tabellenstrukturen zu erkennen, auch solche mit asymmetrischem Layout und verbundenen Zellen.

##### Modus

Standardwert: **Default**

Werteliste:

- **Default**: Diese Option ist der Textextraktionsmodus für die folgenden Standardbedingungen: 
    - Mindesttextgröße von 10 pt
    - Durchschnittlicher Kontrast von 50 %
    - Tabellen – unter der Voraussetzung, dass sie eine klare und erkennbare Struktur haben (z. B. mit langen Kanten)
    - keine komplexen Strukturen wie verschlungene Tabellen
- **Schnell**: In diesem Modus wird eine grobe Bildanalyse durchgeführt, d. h. es wird zunächst zwischen Bereichen mit Text und den Bereichen mit Bildern unterschieden. Auf Grundlage dieser Unterscheidung wird die optische Zeichenerkennung (OCR) nur in den als Textbereiche erkannten Abschnitten durchgeführt.
- **Genau**: Dieses Verfahren erfordert eine deutlich höhere Rechenleistung und kann für schwierige Fälle eingesetzt werden, in denen die Buchstabenerkennung mit anderen Modi nicht die erwarteten Ergebnisse liefert. Außerdem ermöglicht dieser Modus die Erkennung von Text in Bildern und auf bildähnlichen Hintergründen.
- **Feld**: Dieser Modus wird empfohlen, wenn der Suchbereich sehr textlastig ist und keine Ränder hat, da alles als Text behandelt wird.

##### Mit neuer Auflösung

Diese Funktion passt den dpi-Wert des Bildes an, sodass auch Bilder mit kleinen Schriftarten verwendet werden können. Es gibt drei kategorische Optionen (0, 1 und 2) sowie ein dpi-Spektrum zur Auswahl.

Standardwert: **2**

- 0: Keine Anpassung
- **1**: Automatische Anpassung – Die Berechnung wird durchgeführt und der optimale Wert wird einmal festgelegt und bleibt bei jeder weiteren Ablesung konstant.
- **2**: Dynamische Anpassung – Jede Berechnung liefert einen neuen optimalen Wert.
- **50–3200**: In diesem Bereich kann ein exakter Wert für die Neuskalierung eingegeben werden.

##### Zoom

Bei einem anderen Zoomwert als 1 wird die Bildquelle vor der Anwendung einer optischen Zeichenerkennung um den angegebenen Faktor verändert. Dadurch kann z. B. die Gesamtgröße der Buchstaben erhöht werden. Zoom = 2.0 vergrößert das Bild beispielsweise auf die doppelte Breite und Höhe.

Standardwert: **1.0**

##### Bildverbesserung für die Textsuche

Bei dieser Einstellung geht es um Helligkeits- oder Farbabweichungen, die nicht von der Abbildung selbst stammen, sondern von elektronischen Quellen wie Scannern oder Kameras („Bereinigen“), die körnig aussehende Bilder verursachen können. Die Einstellung „Schärfen“ glättet und schärft durch Komprimierung der betroffenen Bilder.

Standardwert: **Aus**

Werteliste:

- **Beides**: Verwendet „Bereinigen“ und „Schärfen“.
- **Bereinigen**: Entfernt zufälliges Rauschen, das z. B. durch Kamerabilder oder bei schlechten Scanergebnissen entsteht.
- **Schärfen**: Verbessert die Schärfe der Kanten im Bild (z. B. bei komprimierten Bildern).
- **Keine**: Verwendet weder „Bereinigen“ noch „Schärfen“.

##### Kontrast verbessern?

Einige Bilder können einen schlechten Kontrast aufweisen, z. B. durch grauen Text auf hellgrauem Hintergrund. Dies erschwert die Analyse und Interpretation eines Texts. In solchen Fällen ist es empfehlenswert, den lokalen Kontrast zu erhöhen.

- Standardwert: **Nein**
- Werteliste: {**Ja**, **Nein**}

##### Text Rotation

In manchen Fällen kann der Text in einem Dokument gedreht sein. Mit der Funktion „Auto“ dreht **EMMA** den Text selbstständig, sodass er ausgelesen werden kann.

- Standardwert: **Aus**
- Werteliste: {**Aus**, **Auto**}

##### Texttyp

Um die Textsuche und die gefundenen Ergebnisse zu optimieren, kann eine Schriftart ausgewählt werden, die dem vorliegenden Text ähnlich ist. Die ausgewählte Schriftart wird in der Beispielbox angezeigt.

- Standardwert: **Default**
- Werteliste: {**Default**, **Gotisch**, **Nadeldrucker,** **Bankscheck(CMC7)**, **Bankscheck(E13B)**, **Kreditkarte(OCR A)**, **Maschinell(OCR B)**, **Quittung, Schreibmaschine}**

#### Sprachen

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719474364765.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719474364765.png)

Der Tab ***Sprachen*** ist nur dann verfügbar, wenn im Tab ***Find Eigenschaften*** als Gegenstand „Text“ oder „RegEx“ ausgewählt wurde. Unter Sprache kann die Sprache ausgewählt werden, nach der **EMMA** im vorliegenden Fall suchen soll.

Wähle die Sprachen, die extrahiert werden sollen. Die verfügbaren Sprachen in **Emma Studio** sind abhängig vom gebuchten Paket.

Die ausgewählten Sprachen legen fest, welches Alphabet die Zeichenerkennung beim Abgleich verwendet. Bei Bedarf können auch mehrere Sprachen ausgewählt werden, z. B. „Deutsch“ und „Zahlen“ zum Lesen eines gemischten Textes wie: „Wir haben 15 Ereignisse gezählt.“

Die folgenden Sprachen stehen zur Auswahl:

Chinesisch/Taiwanesisch, Englisch, Französisch, Deutsch, Griechisch, Italienisch, Norwegisch, Portugiesisch, Russisch, Slowenisch, Kroatisch, Spanisch, Schwedisch, Türkisch, Zahlen, Ganzzahl, Dezimalzahl, Römische Zahl, Englische Zahlwörter, Währungen, Datum, Zeit 12h/24h Format, Zeit 24h Format

#### Tab „Ergebnisauswahl“

[![filteroption findenschritt.PNG](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/filteroption-findenschritt.PNG)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/filteroption-findenschritt.PNG)

##### Reihenfolge

Wählt die Reihenfolge aus, in der die Suchergebnisse nummeriert werden sollen. Wenn z. B. von oben nach unten ausgewählt wird, erhält der oberste Treffer die Nummer eins. Die folgenden Optionen stehen zur Auswahl:

- **Höchstes:** Ordnet die Treffer nach ihrer Punktzahl, wobei den Treffern mit der höchsten Punktzahl die kleinste Nummer zugewiesen wird.
- **Nächstes:** Ordnet die Treffer nach ihrer Entfernung zu einer bestimmten X- und Y-Koordinate, wobei die nächstgelegenen Treffer die kleinste Nummer erhalten.
- **Zufällig:** Ordnet die Treffer zufällig an.
- **Oben nach unten:** Ordnet die Treffer nach ihrem Abstand vom oberen Bildschirmrand an. Die Treffer, die dem oberen Rand am nächsten sind, erhalten dabei die kleinste Nummer.
- **Unten nach oben:** Ordnet die Treffer nach ihrem Abstand vom unteren Bildschirmrand an. Die Treffer, die dem unteren Rand am nächsten sind, erhalten dabei die kleinste Nummer.
- **Links nach rechts:** Ordnet die Treffer nach ihrem Abstand vom linken Bildschirmrand an. Die Treffer, die dem linken Rand am nächsten sind, erhalten dabei die kleinste Nummer.
- **Rechts nach links:** Ordnet die Treffer nach ihrem Abstand vom rechten Bildschirmrand an. Die Treffer, die dem rechten Rand am nächsten sind, erhalten dabei die kleinste Nummer.

##### Treffer Nr.

Die Nummer der Treffer, die als primäres Ergebnis und Schrittausgabe verwendet wird. Wenn dieser Wert auf „2“ gesetzt und dann von oben nach unten ausgewählt wird, gibt der Schritt den zweiten Treffer von oben als ausgewähltes Ergebnis zurück. Wird ein negativer Wert eingegeben, wird die Suchreihenfolge umgekehrt.

##### Filter

Entfernt Treffer aus der Auswahl, die nicht mit den angegebenen Kriterien übereinstimmen. Wenn z. B. „Links von“ ausgewählt wird, werden nur Treffer links vom eingegebenen Punkt berücksichtigt. Die folgenden Optionen stehen zur Auswahl:

- **Darunter:** Wählt alle Treffer unterhalb einer ausgewählten Y-Koordinate aus.
- **Darüber:** Wählt alle Treffer oberhalb einer ausgewählten Y-Koordinate aus.
- **Links von:** Wählt alle Treffer links von einer ausgewählten X-Koordinate aus.
- **Rechts von:** Wählt alle Treffer rechts von einer ausgewählten X-Koordinate aus.
- **In der Reihe von:** Wählt alle Treffer aus, die sich in derselben Reihe wir die ausgewählte X-Koordinate befinden.
- **In der Spalte von:** Wählt alle Treffer aus, die sich in derselben Spalte wie die ausgewählte Y-Koordinate befinden.

#### Tab „Zu suchendes Objekt“

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719474514852.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719474514852.png)

Über den Tab **Zu suchendes Objekt** ist es möglich, im Bereich ***Sehen*** nach einem Bild zu suchen und es über seine eigene ID in das Feld Objektnummer im Tab **Find Eigenschaften** zu übertragen.

##### Name

Suche nach einem Objekt anhand seines Namens.

##### Tag

Einschränkung der Suchergebnisse über Tags, die beim Anlegen von Objekten definiert werden können.

# Finden & Klicken

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719490434190.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719490434190.png) *Abbildung 62 – Sensor – Prozessschritt **Finden &amp; Klicken***

Der Prozessschritt ***Finden &amp; Klicken*** ergänzt den Prozessschritt ***Finden*** um einen einfachen Linksklick, der von **EMMA** nach erfolgreicher Suche auf dem gefundenen Objekt ausgeführt wird. Die Eingabefelder sind identisch mit denen des Prozessschritts ***Finden***. Wenn ein Objekt gesucht wurde, wird der Klick genau an der Position des Fadenkreuzes ausgeführt, das bei der Objekterstellung definiert werden kann. Wurde ein Text gesucht, ist die Klickposition entweder die Mitte des ersten gefundenen Worts oder (bei Definition einer Zeichengruppe via RegEx) die Mitte der ersten Zeichengruppe.

# Lesen

Mithilfe des Prozessschritts ***Lesen*** kann **EMMA** einen Text oder Bildausschnitt des Bildschirms, aus einer Datei oder von anderen Quellen lesen. Nach Auswahl des Quelldokuments definiert man dazu den Bereich, aus dem der Text gelesen werden soll. Das erfolgt über die Eingabefelder **Referenz X**, **Referenz Y**, **Höhe** und **Breite** sowie optional **Versatz X** und **Versatz Y**. **EMMA** liefert dann je nach eingestelltem Gegenstand („Text“/„Objekt“) zu der gewählten Position einen Text oder ein Bild als Rückgabewert. Das Ergebnis des Prozessschritts ***Lesen*** kann zur weiteren Verarbeitung in die Zwischenablage kopiert werden.

### Eingabefelder

#### Eigenschaften

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719487613591.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719487613591.png) *Abbildung 57 – Prozessschritt **Lesen***

##### Gegenstand

Hier kann zwischen „Text“, „Text-Field“ und „Objekt“ gewählt werden. Abhängig von der getroffenen Auswahl verändern sich die möglichen Eingabefelder. Der Tab **Shape Konfiguration** erscheint nach Auswahl des Gegenstands „Objekt“ und der Tab **Text Eigenschaften** nach Auswahl des Gegenstands „Text“. Der Unterschied zwischen Text und Text-Field besteht darin, dass Text-Field nur den Text des ausgewählten Felds ausgibt, während die Texterkennung den gesamten Bildschirm untersucht, um präziser arbeiten zu können (z. B. im Hinblick auf die ausgewählte Sprache). Wenn Objekt ausgewählt ist, liest der Prozessschritt ***Lesen*** den angegebenen Bildbereich und gibt ein neues Objekt als Ergebnisfeld zurück.

##### Warte vor Start (ms)

Die Wartezeit ab der Beendigung des vorhergehenden Prozessschritts bis der Schritt ***Lesen*** beginnen soll. Der Sinn hinter dieser Option ist, eventuell auftretende Animationen oder die Ladezeit einer Website zu berücksichtigen, um das Suchergebnis nicht zu verfälschen.

##### Timeout (ms)

Die maximale Zeit, die **EMMA** mit der Texterkennung verbringt, ehe die Ergebnisse ausgegeben werden.

##### Referenz X/Y

Der Referenzpunkt in X- bzw. Y-Richtung für den zu lesenden Bereich. Als Eingabetyp stehen „Konstanter Wert“, „Ergebnisfeld“ und „Variable“ zur Verfügung.

- **Konstanter Wert**: Entfernung des Mittelpunkts des zu lesenden Bereichs vom Nullpunkt in Pixeln oder Millimetern (abhängig vom gewählten Gerät).
- **Ergebnisfeld**: Hier wird die Ergebniskoordinate eines vorhergehenden Prozessschritts verwendet. Als Eingabe können die X- und Y- Koordinate unterschiedlicher vorhergehender Prozessschritte gewählt werden.
- **Variable** (Dezimalzahl)

##### Breite/Höhe

Breite/Höhe des zu lesenden Bereichs. Als Eingabetyp stehen „Konstanter Wert“, „Ergebnisfeld“ und „Variable“ (Dezimalzahl) zur Verfügung.

##### Versatz X/Y

An dieser Stelle kann festgelegt werden, um welchen Wert vom Referenzpunkt abgewichen werden soll (Verschiebung der Koordinate). Als Eingabetyp stehen „Konstanter Wert“, „Ergebnisfeld“ und „Variable“ (Dezimalzahl) zur Verfügung.

##### In Zwischenablage

Optional kann festgelegt werden, ob der gelesene Text bzw. das Objekt in die Zwischenablage kopiert werden sollen.

#### Tab „Shape Konfiguration“

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719488120890.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719488120890.png)

*Abbildung 58 – Sensor – Prozessschritt **Lesen** – Tab „Shape Konfiguration“*

Dieser Tab wird angezeigt, wenn unter **Eigenschaften** als Gegenstand „Objekt“ gewählt wurde (siehe Kapitel 4.5.1 für Erläuterungen zu den Kontrasteinstellungen).

##### Obere Tiefenschärfe

Höchster Kontrastwert des Objekts in den Suchbildern.

- Standardwert: **200**
- Werteliste: {0 bis **1000**}

##### Untere Tiefenschärfe

Niedrigster Kontrastwert des Objekts in den Suchbildern.

- Standardwert: **50**
- Werteliste: {0 bis **1000**}

##### Min. Übereinstimmung

Minimaler Kontrastanteil in den Suchbildern.

- Standardwert: **2.0**
- Werteliste: {**0,0** bis **100,0**}

#### Tab „Text Eigenschaften“

Wenn **EMMA** mit den Standardeinstellungen den Text nicht ausreichend genau auslesen konnte, können die Einstellungen im Tab **Text Eigenschaften** für diesen speziellen Fall angepasst werden.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719488349086.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719488349086.png)

*Abbildung 59 – Sensor – Prozessschritt **Lesen** – Tab „Text Eigenschaften“*

##### Profil

Hier wird das Hauptprofil für die OCR-Textumwandlung definiert. Es gibt fünf verschiedene Profile.

Standardwert: **Default**

Werteliste:

- **Default**: Diese Einstellung ist für Dokumente mit einer einfachen Struktur vorgesehen.
- **None**: Dokumentenanalyseverfahren wie Farb- und Schriftanalyse werden übersprungen. Diese Option funktioniert vor allem bei Quelldokumenten mit nur wenigen oder kleinen Bildern.
- **Text**: Diese Option gibt der Texterkennung Vorrang vor der Kantenerkennung.
- **Table**: Diese Einstellung bewirkt, dass **EMMA** versucht, Tabellen anstelle von einfachen Kanten zu finden (Kästchenbildung).
- **ForceTables**: Diese Option geht noch einen Schritt weiter und zwingt **EMMA**, alle möglichen Tabellenstrukturen zu erkennen, auch solche mit asymmetrischem Layout und verbundenen Zellen.

##### Modus

Standardwert: **Default**

Werteliste:

- **Default**: Diese Option ist der Textextraktionsmodus für die folgenden Standardbedingungen: 
    - Mindesttextgröße von 10 pt
    - Durchschnittlicher Kontrast von 50 %
    - Tabellen – unter der Voraussetzung, dass sie eine klare und erkennbare Struktur haben (z. B. mit langen Kanten)
    - keine komplexen Strukturen wie verschlungene Tabellen
- **Fast**: In diesem Modus wird eine grobe Bildanalyse durchgeführt, d. h. es wird zunächst zwischen Bereichen mit Text und Bereichen mit Bildern unterschieden. Auf Grundlage dieser Unterscheidung wird die optische Zeichenerkennung (OCR) nur in den als Textbereiche erkannten Abschnitten durchgeführt.
- **Accurate**: Dieses Verfahren erfordert eine deutlich höhere Rechenleistung und kann für schwierige Fälle eingesetzt werden, in denen die Buchstabenerkennung mit anderen Modi nicht die erwarteten Ergebnisse liefert. Außerdem ermöglicht dieser Modus die Erkennung von Text in Bildern und auf bildähnlichen Hintergründen.
- **Field**: Dieser Modus wird empfohlen, wenn der Suchbereich sehr textlastig ist und keine Ränder hat, da alles als Text behandelt wird.

##### Mit neuer Auflösung

Diese Funktion passt den dpi-Wert des Bildes an, sodass auch Bilder mit kleinen Schriftarten verwendet werden können. Es gibt drei kategorische Optionen (0, 1 und 2) sowie ein dpi-Spektrum zur Auswahl.

Standardwert: **2**

- 0: Keine Anpassung
- **1**: Automatische Anpassung – Die Berechnung wird durchgeführt und der optimale Wert wird einmal festgelegt und bleibt bei jeder weiteren Ablesung konstant.
- **2**: Dynamische Anpassung – Jede Berechnung liefert einen neuen optimalen Wert.
- **50–3200**: In diesem Bereich kann ein exakter Wert für die Neuskalierung eingegeben werden.

##### Zoom

Bei einem anderen Zoomwert als 1 wird die Bildquelle vor der Anwendung einer optischen Zeichenerkennung um den angegebenen Faktor verändert. Dadurch kann z. B. die Gesamtgröße der Buchstaben erhöht werden. Zoom = 2.0 vergrößert das Bild beispielsweise auf die doppelte Breite und Höhe.

Standardwert: **1.0**

##### Bildverbesserung für die Textsuche

Bei dieser Einstellung geht es um Helligkeits- oder Farbabweichungen, die nicht von der Abbildung selbst stammen, sondern von elektronischen Quellen wie Scannern oder Kameras („Bereinigen“), die körnig aussehende Bilder verursachen können. Die Einstellung „Schärfen“ glättet und schärft durch Komprimierung der betroffenen Bilder.

Standardwert: **Aus**

Werteliste:

- **Beides**: Verwendet „Bereinigen“ und „Schärfen“.
- **Bereinigen**: Entfernt zufälliges Rauschen, das z. B. durch Kamerabilder oder bei schlechten Scanergebnissen entsteht.
- **Schärfen**: Verbessert die Schärfe der Kanten im Bild (z. B. bei komprimierten Bildern)
- **Keine**: Verwendet weder „Bereinigen“ noch „Schärfen“.

##### Kontrast verbessern?

Einige Bilder können einen schlechten Kontrast aufweisen, z. B. durch grauen Text auf hellgrauem Hintergrund. Dies erschwert die Analyse und Interpretation eines Texts. In solchen Fällen ist es empfehlenswert, den lokalen Kontrast zu erhöhen.

Standardwert: **Nein**

Werteliste: {**Ja**, **Nein**}

##### Text Rotation

In manchen Fällen kann der Text in einem Dokument gedreht sein. Mit der Funktion „Auto“ dreht **EMMA** den Text selbstständig, sodass er ausgelesen werden kann.

Standardwert: **Aus**

Werteliste: {**Aus**, **Auto**}

##### Validierungsmuster

Das Validierungsmuster legt fest, was ein gültiges Leseergebnis sein kann. Enthält der gelesene Text dieses nicht, endet der Prozessschritt mit einem Fehler. Das Validierungsmuster wird mittels RegEx beschrieben (wie im Prozessschritt ***Finden***) – z.B. führt die Angabe von „yes|no“ zu einem Fehler, wenn ein anderes Wort gelesen wird. Das Validierungsmuster unterstützt **EMMA** auch bei der Erkennung der richtigen Zeichen. Wenn z. B. für eine IBAN-Nummer das Validierungsmuster „\\w\\w \\d\\d \\d\\d\\d \\d\\d\\d \\d\\d\\d \\d\\d\\d \\d\\d \\d\\d \\d\\d“ angegeben wurde, erkennt das **EMMA** vorrangig Ziffern an Stellen, für die ein \\d angegeben wurde. Schließlich kann auch das Ergebnis des Prozessschritts ***Lesen*** in diesem Feld angepasst werden. Dies erfolgt in gleicher Weise, wie dies im RegEx-Feld des Prozessschritts ***Finden*** der Fall ist.

##### Texttyp

Um die Textsuche und die gefundenen Ergebnisse zu optimieren, kann eine Schriftart ausgewählt werden, die dem vorliegenden Text ähnlich ist. Die ausgewählte Schriftart wird in der Beispielbox angezeigt.

Standardwert: **Default**

Werteliste: {**Default**, **Gotisch**, **Nadeldrucker,** **Bankscheck(CMC7)**, **Bankscheck(E13B)**, **Kreditkarte(OCR A)**, **Maschinell(OCR B)**, **Quittung**, **Schreibmaschine**}

#### Tab „Sprachen“

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719488952279.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719488952279.png)

*Abbildung 60 – Sensor – Prozessschritt **Lesen** – Tab „Sprachen“*

Alle Parameter dieses Abschnitts funktionieren auf die gleiche Weise wie im Prozessschritt ***Finden*** beschrieben, jedoch mit der Ausnahme, dass E-Mail, Adresse (UK), Adresse (US), Adresse (FR) und Adresse (DE) zusätzlich auswählbar sind, wenn man in den Eigenschaften "Text-Field" als Gegenstand wählt.

#### Tab „Quelldokument“  


In diesem Abschnitt kann die Quelle des Dokuments festgelegt werden. Zur Auswahl stehen die Erfassung von Inhalten direkt vom Bildschirm sowie der Import aus einer Datei. Bei Auswahl der Option „Datei“ gibst du bitte den entsprechenden Dateipfad und die gewünschte Seite an.

# Formular lesen

Der Schritt ***Formular lesen*** nimmt einen Verweis auf ein Dokument auf und extrahiert daraus Informationen auf Grundlage einer vorkonfigurierten Dokumentvorlage. Die Hintergrundinformationen dazu sind unter *[Lesen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/lesen-jNv "Lesen (Wahrnehmung UI)")* zu finden.

Der Vorteil des Schritts ***Formular lesen*** besteht darin, dass das Eingabedokument in eine Dokumentvorlage umgewandelt werden kann, sodass die Felder des Eingabeformulars unabhängig von Skalierung und Drehung immer korrekt mit den entsprechenden Feldern der Dokumentvorlage übereinstimmen. Dies ermöglicht eine wesentlich genauere und schnellere Analyse von Dokumenten.

### Überblick über die Erstellung von Dokumentvorlagen

1. Das Eingabedokument wird unabhängig von seiner Art in ein standardisiertes Bild umgewandelt.
2. Das standardisierte Bild wird so transformiert, dass es der Skalierung und der Drehung der Dokumentvorlage entspricht.
3. Die Zeilen und der Text aus der Vorlage werden aus dem transformierten Eingabedokument entfernt, sodass nur die Teile des Dokuments übrig bleiben, die geändert oder hinzugefügt wurden.
4. Das bereinigte Dokument wird in Abschnitte unterteilt, die von der Eingabemaske vorgegeben sind.
5. Aus jedem der Abschnitte des bereinigten Dokuments wird dann der Text extrahiert.

### Best Practices und wichtige Hinweise

- Das Auslesen funktioniert nicht gut bei Dokumenten, die um mehr als 30 Grad in eine Richtung gedreht sind.
- Da die Zeilen und der Text aus der Vorlage aus dem gescannten Dokument entfernt werden, ist es sinnvoll, die extrahierten Abschnitte des Dokuments größer als die Eingaben des Formulars zu machen, da Benutzer häufig Formulare auch außerhalb des abgegrenzten Bereichs beschriften.
- Die extrahierten Daten lassen sich am besten mit einem Input-Schritt weiterverarbeiten und zuordnen.


### Eingabefelder

#### Form ID

Die ID der zu verwendenden Dokumentvorlage. Zur Erstellung einer neuen Dokumentvorlage sollte das Document Repository verwendet werden.

#### Input File

Die Datei, die von dem Schritt gelesen werden soll. Es kann sich entweder um eine PDF- oder eine Bilddatei handeln (JPEG, Bitmap, PNG).

#### Page to read

Gibt für mehrseitige Dokumente an, welche Seite analysiert werden soll. Bei Nicht-PDF-Dateien (z. B. JPG oder PNG) wird dieser Wert ignoriert, da Bildformate grundsätzlich keine mehrseitige Struktur unterstützen.

# Hören

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719489995791.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719489995791.png) *Abbildung 61 – Sensor – Prozessschritt **Hören***

Der Prozessschritt ***Hören*** dient der Feststellung, ob zum gegebenen Zeitpunkt ein Ton abgespielt wird. Hierzu wird der Ton innerhalb eines definierten Zeitraums analysiert. Anhand der definierten Parameter wird entschieden, ob dieser Ton Gültigkeit besitzt.

### Eingabefelder

#### Mindest-Lautstärke (1–100)

Der Ton ist gültig, wenn der hier angegebene Schwellenwert einmalig überschritten wird.

ODER

#### Durchschn. Lautstärke (1–100)

Die Messung des Tons gilt als gültig, wenn der angegebene Durchschnittswert überschritten wird.

**Hinweis**: Der Durchschnittswert fällt in der Regel eher gering aus, da er durch eine Abtastrate ermittelt wird. Leise Abschnitte während der Messung können den Durchschnittswert deutlich beeinflussen.

#### Min. Messdauer (ms)

Mindestdauer der Messung für die Berechnung des Durchschnittswerts (in Millisekunden).

#### Timeout (ms)

Zeitspanne, nach deren Ablauf die Messung als fehlgeschlagen abgebrochen wird.

#### Warte vor Start (ms)

Wartezeit vor Beginn der Messung. Dieser Wert wird verwendet, um eventuelle Störgeräusche nach dem vorherigen Prozessschritt abzuwarten, damit das Ergebnis nicht verfälscht wird.

# Klicken

Dieser Prozessschritt führt einen Mausklick auf dem PC aus.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719490671551.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719490671551.png) *Abbildung 64 – Prozessschritt **Klicken***

### Eingabefelder

#### X/Y Koordinate

Die X- bzw. Y-Koordinate (horizontal bzw. vertikal) für den Klick. Der 0-Punkt befindet sich in der oberen linken Bildschirmecke, somit sind alle Werte positiv. Die Maßeinheit für die Werte ist Pixel.

#### Versatz X/Y Koordinate

Gelegentlich ist es notwendig, neben ein gefundenes Objekt zu klicken. Der Versatz ermöglicht die Verschiebung der aus einem referenzierten Prozessschritt übernommenen Koordinate. Die Werte sind in Pixel. Positive Werte verschieben die Koordinate nach rechts (X) bzw. unten (Y) (siehe Bezugspunkt), negative Werte in die entgegengesetzte Richtung.

#### Dauer (ms)

Hier wird die Wartezeit festgelegt, bis die Maustaste nach dem Klicken losgelassen wird.

#### Doppelklick?

Über diese Option kann festgelegt werden, ob ein Doppelklick ausgeführt werden soll.

#### Rechtsklick?

Über diese Option kann festgelegt werden, ob anstelle der linken die rechte Maustaste geklickt werden soll.

#### Nur MouseOver?

Mit dieser Option wird der Cursor nur an die entsprechende Position gesetzt, um einen Mouseover-Effekt zu erzeugen. In diesem Fall wird kein Klick ausgeführt und die Optionen „Doppelklick?“ sowie „Rechtsklick?“ werden ignoriert.

# Ziehen

Der Prozessschritt ***Ziehen*** dient dazu, Objekte auf dem Bildschirm anzuklicken, zu verschieben und nach Erreichen des Zielpunkts loszulassen.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719491394235.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719491394235.png)  
*Abbildung 65 – Prozessschritt **Ziehen***

### Eingabefelder

#### Start X/Y Koordinate

Die X- bzw. Y-Koordinate (horizontal bzw. vertikal), an der die Maustaste geklickt werden soll. Der 0-Punkt befindet sich oben links, somit sind die Werte positiv. Die Maßeinheit für die Werte ist Pixel.

#### Start X/Y Versatz

Ermöglicht die Verschiebung der Koordinate aus einem referenzierten Prozessschritt. Die Werte sind in Pixeln angegeben. Positive Werte verschieben die Koordinate nach rechts (X) bzw. unten (Y) (siehe Referenzpunkt).

#### Ende X/Y Koordinate

Die X- oder Y-Koordinate (horizontal oder vertikal), an der die Maustaste losgelassen werden soll. Die Eingabeoptionen sind identisch mit denen bei **Start X/Y-Koordinate**.

#### Ende X/Y Versatz

Die X- oder Y-Koordinate (horizontal oder vertikal), an der die Maustaste losgelassen werden soll – bezogen auf die Eingabe bei **Start X/Y Versatz**. Die Eingabeoptionen sind identisch mit denen bei **Start X/Y-Koordinate**.

# Scrollen

Mithilfe des Prozessschritts ***Scrollen*** ist es möglich, in unterschiedlichen Anwendungen auf einer Seite nach oben und unten sowie nach rechts und links zu scrollen.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719491661253.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719491661253.png)  
*Abbildung 66 – Prozessschritt **Scrollen***

### Eingabefelder

#### Gegenstand

Es kann zwischen „Klick“ und „Pixel“ gewählt werden. Damit kann **EMMA** entweder scrollen, wie man es mit der Maus gewohnt ist, oder sich an einer bestimmten Anzahl von Pixeln orientieren.

#### Richtung

Auswahl der Scrollrichtung. Verfügbar sind die Optionen „Links“, „Rechts“, „Hoch“ und „Runter“.

#### Warte vor Start (ms)

Die Wartezeit, bis **EMMA** den Scroll-Vorgang ausführt.

#### Start X/Y Koordinate

Die X- bzw. Y-Koordinate (horizontal bzw. vertikal), an die der Mauszeiger geführt werden soll, um den Scroll-Vorgang zu starten. Der 0-Punkt befindet sich oben links, somit sind die Werte positiv. Die Maßeinheit für die Werte ist Pixel.

#### Schritte

Anzahl der durchzuführenden Scroll-Vorgänge oder Anzahl der Pixel, die gescrollt werden sollen. Dies hängt von der gewählten Option unter Gegenstand ab. Bei Klick ist der Abstand je Scroll-Vorgang systemabhängig. Üblicherweise scrollt Windows drei Zeilen bzw. drei Spalten pro „Scroll-Klick“ des Mausrads.

# Tippen

Mithilfe des Prozessschritts ***Tippen*** lässt sich ein beliebiger Text eingeben. Hierbei ist zu beachten, dass Tastatureingaben wie `Enter` und `TAB` eingegeben werden können. Damit ist es beispielsweise möglich, ein komplettes Formular mit nur einem Prozessschritt ***Tippen*** zu befüllen. Bei fehlerhaften Texten (z. B. falsche Verwendung der geschweiften Klammern) erfolgt bei der Ausführung des Prozessschritts keine Textausgabe.

[![5f7ca51b-e6cd-4628-b9f1-7fe9dcc6f25f.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/5f7ca51b-e6cd-4628-b9f1-7fe9dcc6f25f.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/5f7ca51b-e6cd-4628-b9f1-7fe9dcc6f25f.png)*Abbildung 67 – Prozessschritt **Tippen***

### Eingabefelder

#### Key-basiertes Tippen?

Wenn dieser Wert auf „Ja“ gesetzt ist, wird der Text als eine Reihe von Tastenanschlägen übertragen, d. h. in diesem Modus werden die Zeichen als Tastenereignisse übertragen. Dies ist die flexibelste Methode, da sie nicht nur das Senden von Text, sondern auch beliebige Tastenkombinationen und Mauseingaben wie linke Taste, rechte Taste und mittlere Taste mit Einfach- und Doppelklick unterstützt. Die tastenbasierte Eingabemethode ermöglicht die Steuerung von Anwendungen in einem Remote Desktop oder Citrix-Fenster.

Ist der Wert auf „Nein“ gesetzt, wird der Text als solcher eingegeben und die Sonderzeichen (wie `ENTER` und `TAB`) werden interpretiert und ausgeführt. Damit ist es z. B. möglich, ein Formular mit nur einem Prozessschritt ***Tippen*** auszufüllen.

Einfach gesagt, besteht der Unterschied darin, dass bei aktivierter Option „Key-basiertes Tippen“ ein Text wörtlich durch (virtuelles) Drücken der Tasten eingegeben wird, während bei deaktivierter Funktion („Nein“) ganze Textblöcke wie beim Einfügen aus der Zwischenablage übergeben werden.

#### Text unverändert eingeben

Ist der Wert auf „Ja“ gesetzt, wird der Text ohne Interpretation exakt eingegeben, ohne Sonderzeichen zu interpretieren.

#### Eingabetext

Der zu sendende Text bzw. die zu sendenden Tasteneingaben.

#### Vorschau

Wenn die Vorschaufunktion aktiviert ist, werden vom Benutzer gedrückte Tasten direkt in das Eingabetextfeld übertragen. Dies ist hilfreich, wenn z. B. der Name einer Nicht-Zeichentaste unbekannt ist.

### Anmerkungen

#### Key-basiertes Tippen = Ja

Der Text wird verwendet, um Tastatureingaben und Tastaturkürzel an die aktive Anwendung zu senden. Um ein einzelnes Zeichen einzugeben, wird das Zeichen selbst getippt. Zum Beispiel übergibt man die Zeichenkette `A`, um den Buchstaben `A` darzustellen. Um die Buchstaben `A`, `B` und `C` zu übergeben, muss `ABC` als Text eingegeben werden.

Das Pluszeichen `+`, der Zirkumflex `^`, das Prozentzeichen `%`, die Tilde `~` und die Klammern `( )` haben eine besondere Bedeutung. Um eines dieser Zeichen einzugeben, muss es in geschweifte Klammern `{ }` eingeschlossen werden. Um beispielsweise das Pluszeichen `+` einzugeben, muss `{+}` eingetippt werden. Mithilfe der Schreibweise `{{}` und`{}}` können geschweifte Klammern eingegeben werden. Eckige Klammern `[ ]` haben keine besondere Bedeutung, müssen jedoch in geschweifte Klammern eingeschlossen werden.

<p class="callout warning">**Achtung**: Wenn die zu steuernde Anwendung für den internationalen Einsatz mit unterschiedlichen Tastaturen vorgesehen ist, kann es zu unvorhersehbaren Ergebnissen kommen. Aus diesem Grund müssen die Prozesse mit der entsprechenden Tastaturbelegung ausgeführt werden.</p>

Mit den Codes aus Tabelle 9 können Tasten eingegeben werden, die Aktionen anstelle von Zeichen darstellen, die möglicherweise nicht angezeigt werden.

#### Automatische Vorschläge von **EMMA**

Durch das Eintippen von `{` macht **EMMA** automatisch Vorschläge für die Eingabe. Durch Eingabe von `{CV:` können die bereits definierten Variablen ausgewählt werden und durch Eingabe von `{SR:` die bereits vorhandenen Prozessschritte. Nach Auswahl und Eingabe eines weiteren Doppelpunkts (z. B. `{SR:001 - Find:`) ist es möglich, eines der folgenden Felder bezüglich der Prozessschritte auszuwählen: Anzahl, Ausgeführt, Ergebnis Index, Farbpunktzahl, Gefundener Text, ID Nächster Step, Nächster Step, Laufzeit, Seitennummer, Skaliert, Score, Breite, Höhe, Links, Rechts, Oben, Unten, Rotation, X, Y. Der Wert des entsprechenden Felds wird in diesem Fall mit Type eingegeben. Wenn eine Variable ausgewählt wird, wird der darin gespeicherte Inhalt eingegeben – außer bei gespeicherten Passwörtern. Diese werde nicht angezeigt.

### Spezielle Eingaben (Codes) für den Prozessschritt ***Tippen***

In der folgenden Tabelle sind alle speziellen Eingaben aufgeführt.

<table id="bkmrk-taste-eingabewert-%28c" style="width: 100%; height: 928.594px;"><thead><tr style="height: 29.7017px;"><th style="width: 12.8694%; height: 29.7017px;">**Taste**</th><th style="width: 29.9094%; height: 29.7017px;">**Eingabewert (Code)**</th><th style="width: 57.1973%; height: 29.7017px;">**Beschreibung**</th></tr></thead><tbody><tr style="height: 46.5057px;"><td style="width: 12.8694%; height: 46.5057px;">BACKSPACE\*</td><td style="width: 29.9094%; height: 46.5057px;">{BACKSPACE}, {BACK}, {BS}, oder {BKSP}</td><td style="width: 57.1973%; height: 46.5057px;">Entfernt das Zeichen links von der Cursorposition</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">PAUSE\*</td><td style="width: 29.9094%; height: 29.7017px;">{BREAK} oder {CANCEL}</td><td style="width: 57.1973%; height: 29.7017px;">Unterbricht die Ausführung des aktiven Programms</td></tr><tr style="height: 46.5057px;"><td style="width: 12.8694%; height: 46.5057px;">CAPSLOCK\*</td><td style="width: 29.9094%; height: 46.5057px;">{CAPSLOCK} oder {CAPITAL}</td><td style="width: 57.1973%; height: 46.5057px;">Stellt auf Schreibweise mit Großbuchstaben um, bis die Taste erneut gedrückt wird</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">ENTF\*</td><td style="width: 29.9094%; height: 29.7017px;">{DELETE} oder {DEL}</td><td style="width: 57.1973%; height: 29.7017px;">Entfernt das Zeichen rechts von der Cursorposition</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">RUNTER\*</td><td style="width: 29.9094%; height: 29.7017px;">{DOWN}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor auf die nächste Zeile nach unten</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">ENDE\*</td><td style="width: 29.9094%; height: 29.7017px;">{END}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor an das Ende der Zeile</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">ENTER\*</td><td style="width: 29.9094%; height: 29.7017px;">{ENTER}, {RETURN} oder ~</td><td style="width: 57.1973%; height: 29.7017px;">Sendet ein Formular, betätigt die Schaltfläche OK oder Senden</td></tr><tr style="height: 46.5057px;"><td style="width: 12.8694%; height: 46.5057px;">ESC\*</td><td style="width: 29.9094%; height: 46.5057px;">{ESCAPE} oder {ESC}</td><td style="width: 57.1973%; height: 46.5057px;">Wird üblicherweise verwendet, um ein Formular oder Programm zu beenden</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">HELP\*</td><td style="width: 29.9094%; height: 29.7017px;">{HELP}</td><td style="width: 57.1973%; height: 29.7017px;">Ruft den Hilfetext auf</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">POS1\*</td><td style="width: 29.9094%; height: 29.7017px;">{HOME}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor an den Anfang der Zeile</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">EINFG\*</td><td style="width: 29.9094%; height: 29.7017px;">{INSERT} oder {INS}</td><td style="width: 57.1973%; height: 29.7017px;">Schaltet zwischen Einfüge- und Überschreibmodus um</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">LINKS\*</td><td style="width: 29.9094%; height: 29.7017px;">{LEFT}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor um ein Zeichen nach links</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">NUM\*</td><td style="width: 29.9094%; height: 29.7017px;">NUMLOCK}</td><td style="width: 57.1973%; height: 29.7017px;">Aktiviert die Zifferntastatur</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">BILD RUNTER\*</td><td style="width: 29.9094%; height: 29.7017px;">{PGDN} oder {NEXT}</td><td style="width: 57.1973%; height: 29.7017px;">Blättert ein mehrseitiges Dokument eine Seite nach unten</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">BILD HOCH\*</td><td style="width: 29.9094%; height: 29.7017px;">{PGUP} oder {PRIOR}</td><td style="width: 57.1973%; height: 29.7017px;">Blättert ein mehrseitiges Dokument eine Seite nach oben</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">RECHTS\*</td><td style="width: 29.9094%; height: 29.7017px;">{RIGHT}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor um ein Zeichen nach rechts</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">ROLLEN\*</td><td style="width: 29.9094%; height: 29.7017px;">{SCROLLLOCK} oder {SCROLL}</td><td style="width: 57.1973%; height: 29.7017px;">Aktiviert das Blättern der Seiten über den Mauszeiger</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">TAB\*</td><td style="width: 29.9094%; height: 29.7017px;">{TAB}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor auf die nächste Tabulatorposition nach rechts</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">HOCH\*</td><td style="width: 29.9094%; height: 29.7017px;">{UP}</td><td style="width: 57.1973%; height: 29.7017px;">Bewegt den Cursor um eine Zeile nach oben</td></tr><tr style="height: 29.7301px;"><td style="width: 12.8694%; height: 29.7301px;">F1 ... F16\*</td><td style="width: 29.9094%; height: 29.7301px;">{F1} … {F16}</td><td style="width: 57.1973%; height: 29.7301px;">Funktionstasten `F1` bis `F16`</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">SHIFT</td><td style="width: 29.9094%; height: 29.7017px;">{SHIFT}, {LSHIFT}, {RSHIFT} oder +</td><td style="width: 57.1973%; height: 29.7017px;">Nur die rechte oder die linke Umschalttaste wird gedrückt</td></tr><tr style="height: 46.5057px;"><td style="width: 12.8694%; height: 46.5057px;">STRG</td><td style="width: 29.9094%; height: 46.5057px;">{CONTROL} oder {CTRL}, {LCONTROL}, {RCONTROL\]</td><td style="width: 57.1973%; height: 46.5057px;">Steuerungstaste</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">ALTERNATE</td><td style="width: 29.9094%; height: 29.7017px;">{ALT} ,{MENU} oder %</td><td style="width: 57.1973%; height: 29.7017px;">Alternate-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">LEERTASTE</td><td style="width: 29.9094%; height: 29.7017px;">{SPACE} oder ' '</td><td style="width: 57.1973%; height: 29.7017px;">Leertaste</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">L-WINDOWS</td><td style="width: 29.9094%; height: 29.7017px;">{WIN} oder {LWIN}</td><td style="width: 57.1973%; height: 29.7017px;">Linke Windows-Taste – Startet das Windows Startmenü</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">R-WINDOWS</td><td style="width: 29.9094%; height: 29.7017px;">{RWIN}</td><td style="width: 57.1973%; height: 29.7017px;">Rechte Windows-Taste – Öffnet das Kontextmenü</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">APPS</td><td style="width: 29.9094%; height: 29.7017px;">{APPS}</td><td style="width: 57.1973%; height: 29.7017px;">Apps-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 12.8694%; height: 29.7017px;">SNAPSHOT</td><td style="width: 29.9094%; height: 29.7017px;">{SNAPSHOT}</td><td style="width: 57.1973%; height: 29.7017px;">Schnappschuss des aktuellen Bildschirms aufnehmen</td></tr></tbody></table>

### Modifikationstasten verwenden

Wenn einer der Codes aus der folgenden Tabelle vor die geschweiften Klammern gesetzt wird, bleibt die entsprechende Taste zur Eingabe des Inhalts der Klammern gedrückt. Die Abkürzungen für Sonderzeichen (`+`, `^` und `%`) funktionieren nur, wenn die Option **Key-basiertes Tippen?** auf „Nein“ gesetzt ist.

<table id="bkmrk-taste-eingabewert-sh"><thead><tr><th>**Taste**</th><th>**Eingabewert**</th></tr></thead><tbody><tr><td>SHIFT-TASTE `SHIFT`</td><td>`+` oder `{SHIFT}`</td></tr><tr><td>STEUERUNGSTASTE `STRG`</td><td>`^` oder `{CTRL}`</td></tr><tr><td>ALT-TASTE `ALT`</td><td>`%` oder `{ALT}`</td></tr><tr><td>WIN-TASTE `Win`</td><td>`#` oder `{WIN}`</td></tr><tr><td>ENTER-TASTE `↵`</td><td>`~` oder `{ENTER}`</td></tr></tbody></table>

Um festzulegen, dass eine beliebige Kombination von `SHIFT`-, `STRG`- und `ALT`-Taste gedrückt gehalten werden soll, während anschließend andere Tasten gedrückt werden, muss der Code für diese Tasten in Klammern eingeschlossen werden.

#### Beispiele für die Verwendung von Modifikationstasten

- `+(EC)` oder `{SHIFT}(EC)`: `SHIFT` wird gedrückt gehalten, während die Buchstaben `E` und `C` (nacheinander) gedrückt werden (Ausgabe: EC)
- `+EC`: `SHIFT` gedrückt halten, während der Buchstabe `E` gedrückt wird, `SHIFT` loslassen und den Buchstaben `C` drücken (Ausgabe: Ec)
- `{CTRL}c`: `Steuerung` wird gedrückt (und gehalten), anschließend die Taste `C` gedrückt (und losgelassen) und abschließend die `Steuerung`-Taste losgelassen (Kopieren-Funktion)

### Tasten wiederholt drücken

Wiederholungen können durch folgende Eingabe in das Formular erzeugt werden: { } oder ( ).

#### Beispiele

- `{LEFT 42}`: Die LINKS-Taste wird 42 Mal gedrückt.
- `{h 10}`: Der Buchstabe h wird 10 Mal gedrückt – mit dem Ergebnis „hhhhhhhhhh“.
- `( . 10)`: Die Folge von Leerzeichen und Punkt wird 10 Mal gesendet – mit dem Ergebnis: „ . . . . . . . . . .“
- `EINGABE~`: Es wird „Eingabe“ eingegeben und anschließend die ENTER-Taste gedrückt.

In seltenen Fällen kann das Senden von Tasten für die empfangende Anwendung zu schnell sein. In diesem Fall sollte ein längeres Tastendruckintervall (in Millisekunden) als Zahl in geschweiften Klammern angegeben werden. Dieses kann zwischen beliebigen anderen Tasten platziert werden.

#### Beispiele für Verzögerungen zwischen wiederholt gedrückten Tasten:

`Test{TAB}{300}Test2{0}{TAB}`: Dies wird die Zeichen `Test` + die Funktionstaste `TAB` schnell senden und dann 300 ms warten, ehe `Test2` gesendet wird. Anschließend wird aufgrund der Wartezeit von 0 ms die `TAB`-Taste schnell nach der Ziffer `2` von `Test2` gedrückt. Wenn eine Taste gedrückt und direkt wieder losgelassen werden soll, können die Zeichen `{}` nach dem entsprechenden Befehl eingegeben werden. Beispiel: `{STRG}{}`: Drücken und Loslassen der `STRG`-Taste.

### Senden von Mausereignissen

Der Prozessschritt ***Tippen*** unterstützt auch das Senden von Mausereignissen (wie aus dem Schritt ***Klicken***). Hierzu werden die folgenden Codes verwendet:

<table id="bkmrk-taste-eingabewert-%28c-1"><thead><tr><th>**Taste**</th><th>**Eingabewert (Code)**</th><th>**Beschreibung**</th></tr></thead><tbody><tr><td>Linksklick</td><td>`{CLICK}` oder `{LCLICK}`</td><td>Verwendet für die Auswahl oder Aktivierung von Tasten</td></tr><tr><td>Rechtsklick</td><td>`{RCLICK}`</td><td>Verwendet zum Öffnen des Kontextmenüs</td></tr><tr><td>Doppelklick links</td><td>`{DCLICK}` oder `{LDCLICK}`</td><td>Verwendet für die Aktivierung</td></tr><tr><td>Doppelklick rechts</td><td>`{RDCLICK}`</td><td>Spezielle Aktion</td></tr></tbody></table>

*Tabelle 11 – Maustastenkombinationen für **Tippen***

Für das Ereignis ***Klicken*** können drei zusätzliche Parameter in runden Klammern angegeben werden, z. B.: `{CLICK(100,200,500)}`. Diese Argumente müssen durch ein Komma getrennt und in der unten aufgeführten Reihenfolge angeordnet werden:

1. X-Position (oder Offset); Voreinstellung: +0 (aktuelle Position des Mauszeigers)  
    Eine Zahl ohne Plus- oder Minuszeichen als Präfix definiert eine feste Position, während eine Zahl mit vorangestelltem Plus- oder Minuszeichen einen Offset von der Koordinate X = 0 beschreibt.
2. Y-Position (oder Offset); Voreinstellung: +0 (aktuelle Position des Mauszeigers)  
    Eine Zahl ohne Plus- oder Minuszeichen als Präfix definiert eine feste Position, während eine Zahl mit vorangestelltem Plus- oder Minuszeichen einen Offset von der Koordinate Y = 0 beschreibt.
3. Dauer vor dem Start (in Millisekunden); Voreinstellung: 300 ms  
    Dauer zwischen den Eingabewerten; Voreinstellung: 0 ms  
    Die Dauer, für die die Taste gedrückt gehalten werden soll.

Beispiele:

- `{CLICK}`: Drücke die linke Maustaste beim Nullpunkt X = 0 / Y = 0.
- `{CLICK(,+100)}`: Siehe Beispiel 1, aber klicke 100 Pixel unterhalb der Koordinate Y = 0.
- `{CLICK(+50)}`: Siehe Beispiel 1, aber klicke 50 Pixel rechts von der Koordinate X = 0.
- `{CLICK(+50,-100)}`: Siehe voriges Beispiel, aber klicke 50 Pixel rechts und 100 Pixel oberhalb des Nullpunkts.
- `{CLICK(+50,-100, 300)}`: Siehe oben, und halte die linke Maustaste für 300 ms gedrückt.

Die Maustasten können mit den Tastaturtasten auf die folgende Art kombiniert werden:

- `{SHIFT}{CLICK}`: Halte die `Shift`-Taste, während die linke Maustaste beim Nullpunkt geklickt wird.
- `{SHIFT}{CLICK(,+100)}`: Siehe oben, aber klicke 100 Pixel unterhalb der Koordinate Y = 0.

Die folgende Tabelle zeigt die symbolischen Namen der Konstanten für Maus- oder Tastaturäquivalente, die vom System verwendet werden, wenn die Option **Key-basiertes Tippen?** aktiviert ist. Diese Liste erweitert die bisher in diesem Kapitel vorgestellten Abkürzungen.

<table id="bkmrk-key-name-description" style="width: 100%; height: 3411.11px;"><thead><tr style="height: 29.7017px;"><th style="width: 21.5695%; height: 29.7017px;">**Key Name**</th><th style="width: 78.4196%; height: 29.7017px;">**Description**</th></tr></thead><tbody><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LBUTTON</td><td style="width: 78.4196%; height: 29.7017px;">Linke Maustaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RBUTTON</td><td style="width: 78.4196%; height: 29.7017px;">Rechte Maustaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CANCEL</td><td style="width: 78.4196%; height: 29.7017px;">Control-break Verarbeitung</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MBUTTON</td><td style="width: 78.4196%; height: 29.7017px;">Mittlere Maustaste (Drei-Tasten-Maus)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">XBUTTON1</td><td style="width: 78.4196%; height: 29.7017px;">X1-Maustaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">XBUTTON2</td><td style="width: 78.4196%; height: 29.7017px;">X2-Maustaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BACK</td><td style="width: 78.4196%; height: 29.7017px;">BACKSPACE-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">TAB</td><td style="width: 78.4196%; height: 29.7017px;">TAB-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CLEAR</td><td style="width: 78.4196%; height: 29.7017px;">CLEAR-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SHIFT</td><td style="width: 78.4196%; height: 29.7017px;">SHIFT-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CONTROL</td><td style="width: 78.4196%; height: 29.7017px;">STRG-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MENU</td><td style="width: 78.4196%; height: 29.7017px;">ALT-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PAUSE</td><td style="width: 78.4196%; height: 29.7017px;">PAUSE-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CAPITAL</td><td style="width: 78.4196%; height: 29.7017px;">CAPSLOCK-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">KANA</td><td style="width: 78.4196%; height: 29.7017px;">IME Kana</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">HANGUEL</td><td style="width: 78.4196%; height: 29.7017px;">IME Hanguel (auf Kompatibilität geprüft; verwende HANGUL)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">HANGUL</td><td style="width: 78.4196%; height: 29.7017px;">IME Hangul</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">IME\_ON</td><td style="width: 78.4196%; height: 29.7017px;">IME AN</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">JUNJA</td><td style="width: 78.4196%; height: 29.7017px;">IME Junja</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">FINAL</td><td style="width: 78.4196%; height: 29.7017px;">IME Final</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">HANJA</td><td style="width: 78.4196%; height: 29.7017px;">IME Hanja</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">KANJI</td><td style="width: 78.4196%; height: 29.7017px;">IME Kanji</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">IME\_OFF</td><td style="width: 78.4196%; height: 29.7017px;">IME AUS</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">ESCAPE</td><td style="width: 78.4196%; height: 29.7017px;">ESC-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CONVERT</td><td style="width: 78.4196%; height: 29.7017px;">IME convert</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">NONCONVERT</td><td style="width: 78.4196%; height: 29.7017px;">IME nonconvert</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">ACCEPT</td><td style="width: 78.4196%; height: 29.7017px;">IME accept</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MODECHANGE</td><td style="width: 78.4196%; height: 29.7017px;">IME-Modusänderungsanfrage</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SPACE</td><td style="width: 78.4196%; height: 29.7017px;">Leertaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PRIOR</td><td style="width: 78.4196%; height: 29.7017px;">Bild-hoch-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">NEXT</td><td style="width: 78.4196%; height: 29.7017px;">Bild-runter-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">END</td><td style="width: 78.4196%; height: 29.7017px;">END-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">HOME</td><td style="width: 78.4196%; height: 29.7017px;">HOME-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LEFT</td><td style="width: 78.4196%; height: 29.7017px;">Pfeiltaste nach links</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">UP</td><td style="width: 78.4196%; height: 29.7017px;">Pfeiltaste nach oben</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RIGHT</td><td style="width: 78.4196%; height: 29.7017px;">Pfeiltaste nach rechts</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">DOWN</td><td style="width: 78.4196%; height: 29.7017px;">Pfeiltaste nach unten</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SELECT</td><td style="width: 78.4196%; height: 29.7017px;">SELECT-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PRINT</td><td style="width: 78.4196%; height: 29.7017px;">Drucken-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">EXECUTE</td><td style="width: 78.4196%; height: 29.7017px;">EXECUTE-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SNAPSHOT</td><td style="width: 78.4196%; height: 29.7017px;">PRINT-SCREEN-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">INSERT</td><td style="width: 78.4196%; height: 29.7017px;">INS-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">DELETE</td><td style="width: 78.4196%; height: 29.7017px;">DEL-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">HELP</td><td style="width: 78.4196%; height: 29.7017px;">HELP-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LWIN</td><td style="width: 78.4196%; height: 29.7017px;">Linke Windows-Taste (Natural Keyboard)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RWIN</td><td style="width: 78.4196%; height: 29.7017px;">Rechte Windows-Taste (Natural Keyboard)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">APPS</td><td style="width: 78.4196%; height: 29.7017px;">Applications-Taste (Natural Keyboard)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SLEEP</td><td style="width: 78.4196%; height: 29.7017px;">Computer-Sleep-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">NUMPAD0-9</td><td style="width: 78.4196%; height: 29.7017px;">Zifferntasten 0–9</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MULTIPLY</td><td style="width: 78.4196%; height: 29.7017px;">Multiplizieren-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">ADD</td><td style="width: 78.4196%; height: 29.7017px;">Add-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SEPARATOR</td><td style="width: 78.4196%; height: 29.7017px;">Separator-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SUBTRACT</td><td style="width: 78.4196%; height: 29.7017px;">Subtraktion-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">DECIMAL</td><td style="width: 78.4196%; height: 29.7017px;">Dezimal-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">DIVIDE</td><td style="width: 78.4196%; height: 29.7017px;">Teilen-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">F1-24</td><td style="width: 78.4196%; height: 29.7017px;">F1–24-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">NUMLOCK</td><td style="width: 78.4196%; height: 29.7017px;">NUM-LOCK-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">SCROLL</td><td style="width: 78.4196%; height: 29.7017px;">SCROLL-LOCK-Taste (96 OEM specific)</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LSHIFT</td><td style="width: 78.4196%; height: 29.7017px;">Linke SHIFT-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RSHIFT</td><td style="width: 78.4196%; height: 29.7017px;">Rechte SHIFT-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LCONTROL</td><td style="width: 78.4196%; height: 29.7017px;">Linke Steuerungstaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RCONTROL</td><td style="width: 78.4196%; height: 29.7017px;">Rechte Steuerungstaste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LMENU</td><td style="width: 78.4196%; height: 29.7017px;">Linke MENU-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">RMENU</td><td style="width: 78.4196%; height: 29.7017px;">Rechte MENU-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_BACK</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Back-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_FORWARD</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Forward-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_REFRESH</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Refresh-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_STOP</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Stop-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_SEARCH</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Search-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_FAVORITES</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Favorites-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">BROWSER\_HOME</td><td style="width: 78.4196%; height: 29.7017px;">BROWSER-Start-and-Home-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">VOLUME\_MUTE</td><td style="width: 78.4196%; height: 29.7017px;">Lautstärke-Stumm-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">VOLUME\_DOWN</td><td style="width: 78.4196%; height: 29.7017px;">Lautstärke-runter-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">VOLUME\_UP</td><td style="width: 78.4196%; height: 29.7017px;">Lautstärke-hoch-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MEDIA\_NEXT\_TRACK</td><td style="width: 78.4196%; height: 29.7017px;">Nächster-Titel-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MEDIA\_PREV\_TRACK</td><td style="width: 78.4196%; height: 29.7017px;">Vorheriger-Titel-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MEDIA\_STOP</td><td style="width: 78.4196%; height: 29.7017px;">Stop-Media-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">MEDIA\_PLAY\_PAUSE</td><td style="width: 78.4196%; height: 29.7017px;">Play/Pause-Media-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LAUNCH\_MAIL</td><td style="width: 78.4196%; height: 29.7017px;">Start-Mail-Taste</td></tr><tr style="height: 31.3778px;"><td style="width: 21.5695%; height: 31.3778px;">LAUNCH\_MEDIA\_SELECT</td><td style="width: 78.4196%; height: 31.3778px;">Select-Media-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LAUNCH\_APP1</td><td style="width: 78.4196%; height: 29.7017px;">Start-Application-1-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">LAUNCH\_APP2</td><td style="width: 78.4196%; height: 29.7017px;">Start-Application-2-Taste</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_1</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚;:‘ verwendet.</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_PLUS</td><td style="width: 78.4196%; height: 29.7017px;">Für alle Länder/Regionen: ‚+‘-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_COMMA</td><td style="width: 78.4196%; height: 29.7017px;">Für alle Länder/Regionen: ‚,‘-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_MINUS</td><td style="width: 78.4196%; height: 29.7017px;">Für alle Länder/Regionen: ‚-‘-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_PERIOD</td><td style="width: 78.4196%; height: 29.7017px;">Für alle Länder/Regionen: ‚.‘-Taste</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_2</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚‘/?‘ verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_3</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚`~‘ verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_4</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚\[{‘ verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_5</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚|‘ verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_6</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste ‚\]}‘ verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_7</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Bei der US-Standardtastatur wird die Taste für einfache und doppelte Anführungszeichen verwendet.</td></tr><tr style="height: 46.5057px;"><td style="width: 21.5695%; height: 46.5057px;">OEM\_8</td><td style="width: 78.4196%; height: 46.5057px;">Wird für verschiedene Zeichen verwendet; kann je nach Tastatur variieren.   
Reserviert -&gt; OEM-spezifisch</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_102</td><td style="width: 78.4196%; height: 29.7017px;">Entweder die spitze Klammer oder die Backslash-Taste auf der RT 102-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">Keyboard-E4</td><td style="width: 78.4196%; height: 29.7017px;">OEM-spezifisch</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PROCESSKEY</td><td style="width: 78.4196%; height: 29.7017px;">IME PROCESS; OEM-spezifisch</td></tr><tr style="height: 96.9176px;"><td style="width: 21.5695%; height: 96.9176px;">PACKET</td><td style="width: 78.4196%; height: 96.9176px;">Wird verwendet, um Unicode-Zeichen wie Tastenanschläge zu übergeben.   
Der PAKET-Schlüssel ist das Low-Word eines 32-Bit-Werts eines virtuellen Schlüssels, der für Eingabemethoden verwendet wird, die nicht über die Tastatur erfolgen.   
Weitere Informationen sind in den Bemerkungen zu KEYBDINPUT, SENDINPUT, WM\_KEYDOWN und WM\_KEYUP zu finden.</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">ATTN</td><td style="width: 78.4196%; height: 29.7017px;">Attn-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">CRSEL</td><td style="width: 78.4196%; height: 29.7017px;">CrSel-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">EXSEL</td><td style="width: 78.4196%; height: 29.7017px;">ExSel-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">EREOF</td><td style="width: 78.4196%; height: 29.7017px;">Erase-EOF-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PLAY</td><td style="width: 78.4196%; height: 29.7017px;">Play-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">ZOOM</td><td style="width: 78.4196%; height: 29.7017px;">Zoom-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">NONAME</td><td style="width: 78.4196%; height: 29.7017px;">Reserviert</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">PA1</td><td style="width: 78.4196%; height: 29.7017px;">PA1-Taste</td></tr><tr style="height: 29.7017px;"><td style="width: 21.5695%; height: 29.7017px;">OEM\_CLEAR</td><td style="width: 78.4196%; height: 29.7017px;">Clear-Taste</td></tr></tbody></table>

*Tabelle 12 – Symbolische Konstantennamen für Maus- oder Tastaturäquivalente*

# Sprechen

Mithilfe des Prozessschritts ***Sprechen*** kann ein Ton gesendet werden. Es ist möglich, eine bereits aufgenommene Wave-Datei zu verwenden oder einen Text einzugeben, der von der Text-to-Speech-Komponente des Computers vorgelesen wird.

Beim Erstellen eines Prozesses ist der Schritt ***Sprechen*** ein hilfreiches Werkzeug, um Informationen akustisch wiederzugeben. Viele Prozesse in **EMMA** verwenden diesen Schritt, um Inhalte über eine definierte Stimme hörbar zu generieren. Das Verständnis der Funktionsweise des Prozessschritts ***Sprechen*** ist entscheidend für alle Prozesse, bei denen Ton eine Rolle spielt.

Es gibt mehrere Quellen, die der Schritt ***Sprechen*** nutzen kann. Bei der textbasierten Quelle wird der eingegebene Text durch eine vorher konfigurierte synthetische Stimme gesprochen. Die Auswahl der Stimme erfolgt über die Einstellungen im Schritt ***Sprechen**.*

Wenn als Quelle eine Wave-Datei verwendet wird, wird die entsprechende Audiodatei direkt abgespielt. In diesem Fall erfolgt keine synthetische Sprachgenerierung, sondern eine exakte Wiedergabe der hinterlegten Audiodatei.

Für beide Varianten – gesprochener Text oder Wave-Datei – muss die Quelle vorab definiert und korrekt verknüpft sein.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719498341472.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719498341472.png)  
*Abbildung 68 – Prozessschritt **Sprechen***

### Eingabefelder

#### Warte vor Start (ms)

Die Wartezeit ab der Beendigung des vorhergehenden Prozessschritts bis der Schritt ***Sprechen*** beginnen soll. Der Sinn hinter dieser Option ist, eventuell auftretende Animationen oder die Ladezeit einer Homepage zu berücksichtigen, um das Suchergebnis nicht zu verfälschen.

#### Audio Quelle

Hier können „Gespeicherte Sounds“ (siehe auch Kapitel 4.6) und „Vorlesen“ als Quelle ausgewählt werden.

##### Vorlesen

Bei Auswahl der Quelle „Vorlesen“ stehen die folgenden Felder zur Verfügung:

- **Text zum Vorlesen:** Eingabe des Texts, der vorgelesen werden soll.
- **Stimme:** Auswahl der Stimme, mit welcher der Text vorgelesen werden soll. Um die Anzahl der auswählbaren Stimmen zu erhöhen, müssen die entsprechenden Vorlesen-Systemstimmen auf allen Computern installiert werden, auf denen **EMMA Studio** eingerichtet wurde.

##### Gespeicherte Sounds

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719498678590.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719498678590.png)  
*Abbildung 69 – Prozessschritt **Sprechen** 2*

Bei Auswahl der Quelle „Gespeicherte Sounds“ stehen die folgenden Felder zur Verfügung:

- **Name**: Suche nach Sounds anhand ihres Namens.
- **Sound Tag**: Einschränkung der Suchergebnisse durch spezifische **Tags**, die bei der Erstellung von Sounds definiert werden können.

# GenAI

#### Was ist der Prozessschritt GenAI?

Der Prozessschritt ***GenAI*** ist ein eigenständiger Prozessschritt in **EMMA** **Studio**, mit dem die in **EMMA** **Cortex Admin** erstellten Skills ausgeführt werden können. Er bildet die Brücke zwischen der deterministischen Prozessautomatisierung von **EMMA** **Studio** und der intelligenten, flexiblen Verarbeitung durch generative KI.

Die Konfiguration und Erstellung von Skills in **EMMA** **Cortex** ist der Anleitung im eigenen Handbuch von **EMMA** **Cortex** zu entnehmen.

#### Voraussetzungen

Bevor der Prozessschritt ***GenAI*** verwendet werden kann, ist sicherzustellen, dass:

<div id="bkmrk-das-add-on-emma-cort">- Das Add-On **EMMA Cortex** installiert und konfiguriert ist
- Der **EMMA Cortex** **Service** läuft
- Mindestens ein Skill in **EMMA Cortex Admin** erstellt wurde
- Dein Benutzer die "Skill"-Berechtigung hat
- Die erforderlichen Lizenzen aktiviert sind (1900 AI Step, 1901 **EMMA Cortex Service**, 1902 **EMMA Cortex Admi**n)
- **EMMA** **Cortex** ist aufpreispflichtig – Für Preisinformationen kontaktiere uns gerne.

</div>[![image-png-Mar-02-2026-12-44-21-7704-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/image-png-mar-02-2026-12-44-21-7704-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/image-png-mar-02-2026-12-44-21-7704-pm.webp)

#### Schritt 1: Skill auswählen

Nach dem Hinzufügen des Prozessschritts ***GenAI*** erfolgt die Konfiguration:

- Prozessschritt ***GenAI*** im Workflow auswählen. Eigenschaftenfenster öffnet sich.
- Im Eigenschaftenfenster das Feld "Skill" auswählen.
- Auf die Dropdown-Liste klicken. Gewünschten Skill aus der Liste auswählen.
- In der Dropdown-Liste erscheinen alle Skills, die in **EMMA** Cortex Admin erstellt wurden. Name und Beschreibung unterstützen bei der Identifikation des passenden Skills.

#### Schritt 2: Input-Felder konfigurieren

Nach Auswahl eines Skills erscheinen automatisch die Input-Felder im Eigenschaftenfenster. Diese Felder entsprechen den Input-Variablen, die beim Erstellen des Skills definiert wurden.  
Die Werte entsprechend den an das LLM zu übergebenden Daten einsetzen. Im Beispiel wird im Feld "Mail" ein Mailtext über ein Ergebnisfeld oder eine Variable übergeben und der Wert Anhang über eine Boolean Variable.

[![image-png-Jan-31-2026-04-54-41-6514-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/39simage-png-jan-31-2026-04-54-41-6514-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/39simage-png-jan-31-2026-04-54-41-6514-pm.webp)[![image-png-Jan-31-2026-04-56-59-5626-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/tViimage-png-jan-31-2026-04-56-59-5626-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/tViimage-png-jan-31-2026-04-56-59-5626-pm.webp)

#### Schritt 3: CSV-Export aktivieren (optional)

Der Prozessschritt ***GenAI*** bietet eine Funktion zum automatischen Speichern der Ergebnisse.

CSV-Export aktivieren:

- Im Eigenschaftenfenster zur Option "Save to CSV file" wechseln.
- Wert auf "Ja" setzen.
- Die Ausgabe des Skills wird automatisch als CSV-Datei gespeichert.
- Speicherort: %AppData%\\OTTRobotics\*\*EMMA\*\* Studio\\SkillsOutput
- Der Dateiname wird automatisch mit Zeitstempel generiert.
- Die CSV-Datei enthält alle Output-Felder des Skills sowie der Zurückgegebenen Daten des LLMs.

#### Schritt 4: Prozess ausführen

Nach der Konfiguration des Prozessschritts ***GenAI***: Prozess speichern.

- Prozess ausführen (manuell über das Reagenzglas oder im Gesamtprozess).
- Der Prozessschritt ***GenAI*** sendet die Daten an **EMMA** **Cortex**.
- **EMMA** **Cortex** verarbeitet die Anfrage mit dem konfigurierten KI-Modell.
- Ergebnisse werden zurück an **EMMA** **Studio** gesendet.
- Output-Felder stehen als Variablen für nachfolgende Schritte zur Verfügung.

Hinweis: Die Verarbeitungszeit hängt vom verwendeten Modell und der Komplexität der Aufgabe ab. Cloud-Modelle sind meist schneller, lokale Modelle bieten dafür mehr Datenschutz.

##### Schritt 5: Ergebnisse weiterverarbeiten

Nach der Ausführung des Prozessschritts ***GenAI*** stehen die Output-Felder Tabelle zur Verfügung. Diese kann in nachfolgenden Schritten verwendet werden. Die einfachste Methode zur Weiterverwendung erfolgt über den Import Schritt. Dabei im Import Schritt das Quelldokument "***GenAI* *Step***" auswählen.

[![image-png-Jan-31-2026-05-08-28-1174-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/image-png-jan-31-2026-05-08-28-1174-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/image-png-jan-31-2026-05-08-28-1174-pm.webp)

Anschließend den Prozessschritt ***GenAI*** und die Daten dazu auswählen. Der Import erfolgt immer in der gleichen Reihenfolge, wie die Anordnung im **EMMA** Cortex im Output angelegt wurde.

[![image-png-Jan-31-2026-05-10-24-9471-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/image-png-jan-31-2026-05-10-24-9471-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/image-png-jan-31-2026-05-10-24-9471-pm.webp)

[![image-png-Jan-31-2026-05-12-18-5825-PM.webp](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/image-png-jan-31-2026-05-12-18-5825-pm.webp)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/image-png-jan-31-2026-05-12-18-5825-pm.webp)

Die Nutzung des Ergebnisfeldes aus dem Prozessschritt ***GenAI*** gibt folgende Ausgabe:

`document Type;customer Name;postal Code;country;client No;due Date;invoice No;total;amount Positions;invoice Date;terms of paymentinvoice;unknown;85356;unknown;001;14.05.2021;2021026;€ 14.875,00;2;14.04.2021;30`

Über eine Schleife können die Daten nun weiterverarbeitet werden.

# Export

Mit dem Prozessschritt ***Export*** können Daten zur Laufzeit in eine XLSX- oder CSV-Datei geschrieben werden. Dabei werden die Daten als unformatierter Text exportiert.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719555466222.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719555466222.png)  
*Abbildung 72 – Prozessschritt **Export***

### Eingabefelder

#### Gegenstand

An dieser Stelle wird festgelegt, in welchen Teil der Datei die Informationen exportiert werden sollen. Momentan wird nur der Export in eine einzelne Zelle unterstützt.

#### Datei

Name der Datei (inkl. Dateipfad), in die die Daten exportiert werden sollen.

#### Tabelle

Die Nummer des Arbeitsblatts in der Excel-Datei, mit dem **EMMA Studio** in der entsprechenden Datei arbeiten soll.

#### Trennzeichen

Angabe des Trennzeichens. Bei CSV-Dateien ist dies üblicherweise ein Komma „,“ oder Semikolon „;“.

#### Erste Zeile ignorieren

Wird dieser Wert auf „Ja“ gesetzt, wird die erste Zeile in der Datei übersprungen, da sich in dieser z. B. die Tabellenüberschriften befinden.

#### Spalte

Die Spalte, in die ein Wert exportiert werden soll.

#### Zeile

Die Zeile, in die ein Wert exportiert werden soll.

#### Wert

An dieser Stelle wird der zu exportierende Wert festgelegt.

# Import

Mit dem Prozessschritt ***Import*** können Daten aus XLSX- und CSV-Dateien importiert werden.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719499011003.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719499011003.png)  
*Abbildung 71 – Prozessschritt **Import***

### Eingabefelder

#### Gegenstand

An dieser Stelle wird festgelegt, welche Informationen importiert werden sollen:

- **Zelle**: Ein einzelner Wert
- **Zeile:** Werte aus einer Zeile, beginnend ab **Spalte** bis einschließlich **Letzte Spalte**
- **Spalte:** Werte aus Spalte, beginnend ab **Zeile** bis einschließlich **Letzte Zeile**
- **Ganze Zeile**: Alle Werte aus der angegebenen Zeile
- **Ganze Spalte**: Alle Werte aus der angegebenen Spalte

<p class="callout info">**ACHTUNG:** Formatierte, aber leere Felder, die nicht mit Informationen befüllt sind, werden nicht übernommen, sofern sie am Ende einer Zeile oder Spalte stehen.</p>

#### Datei

Name der Datei (inkl. Dateipfad), aus der die Daten importiert werden sollen.

#### Tabelle

Wenn unter Datei eine Excel-Datei (.XLS, .XLSX, .XLSM) angegeben wurde, wird an dieser Stelle die Nummer des Arbeitsblatts in der Excel-Datei definiert.

#### Trennzeichen

Wenn unter Datei eine CSV-Datei angegeben wurde, wird hier das Trennzeichen angegeben. Bei CSV-Dateien ist dies üblicherweise ein Komma „,“ oder Semikolon „;“.

#### Erste Zeile ignorieren

Wird dieser Wert auf „Ja“ gesetzt, wird die erste Zeile in der Datei übersprungen. Diese Option wird häufig verwendet, um die Tabellenüberschriften vom Import auszuschließen.

#### Spalte

Die Spalte, aus der ein Wert oder die im Ganzen importiert werden soll.

#### Zeile

Die Zeile, aus der ein Wert oder die im Ganzen importiert werden soll.

#### Timeout (ms)

Die maximale Zeit, die **EMMA** für den Import eines Werts benötigt, falls sich die Datei ändert oder während des Imports durch ein anderes Programm blockiert wird.

# Befehl

Dieser Schritttyp führt eine beliebige Anweisung in der Befehlszeile aus. Er kann verwendet werden, um externe Programme, Dateien oder URLs (wie https://www.wianco.com) zu starten. Der Schritt kann auf die Beendigung des gestarteten Programms warten oder nach dem Start enden, sodass der **EMMA**-Prozess weiterläuft, während das gestartete Programm weiterhin aktiv ist.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1718983463606.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1718983463606.png) *Abbildung 45 – Hilfsschritt – Prozessschritt „Befehl“*

### Eingabefelder

#### Arbeitsverzeichnis

Gibt das Verzeichnis an, in dem der Befehl ausgeführt werden soll. Beispiel: C:\\Program Files\\Google\\Chrome\\Application

#### Dateiname

Gibt das auszuführende Programm oder Skript an, das gestartet werden soll. Dieses muss unter dem Systempfad abgelegt oder relativ zum Arbeitsverzeichnis aufrufbar sein. Beispiel: chrome.exe

#### Argumente

Zusätzliche Eingaben, die nach dem Programmnamen übergeben werden, z. B. eine Datei, URL oder bestimmte Startparameter.

- Beispiel 1: Chrome mit URL öffnen: https://www.wianco.com
- Beispiel 2: Python-Skript im Testmodus starten: main.py --mode test
- Beispiel 3: Excel mit Datei öffnen: C:\\Users\\EMMA\\Documents\\Tabelle.xlsx

#### Versteckt?

Legt fest, ob der Befehl im Hintergrund ausgeführt wird (ohne sichtbares Fenster).

Diese Option kann aktiviert werden, wenn keine Benutzeroberfläche angezeigt werden soll.

#### Ende abwarten?

Legt fest, ob **EMMA** auf das gestartete Programm wartet oder sofort mit dem nächsten Schritt fortfährt.

- **Ja:** **EMMA** pausiert, bis das Programm beendet ist. Beispiel: Excel wird geöffnet; **EMMA** läuft erst weiter, nachdem Excel geschlossen wurde.
- **Nein:** **EMMA** startet das Programm und läuft sofort weiter. Das Programm bleibt im Hintergrund aktiv.

#### Capture Output?

Wenn **Ende abwarten?** aktiviert ist, kann man hier festlegen, ob und welche Konsolenausgaben des gestarteten Programms als „gefundener Text“ übernommen werden sollen. Mögliche Optionen sind:

- **No:** Es wird keine Ausgabe übernommen.
- **Output:** Es wird nur die Standardausgabe übernommen.
- **Error:** Es werden nur Fehlermeldungen übernommen.
- **Both:** Es werden beide Ausgaben (Output + Error) übernommen.

# Dateihandhabung

Der Prozessschritt ***Dateihandhabung*** hilft bei der Verwaltung und Auswahl von Dateien.

[![2f508fd4-3349-4910-b1e1-218567739500.png](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/scaled-1680-/2f508fd4-3349-4910-b1e1-218567739500.png)](http://da-doku.ottrobotics.de/uploads/images/gallery/2026-03/2f508fd4-3349-4910-b1e1-218567739500.png)*Abbildung 73 – Prozessschritt **Dateihandhabung***

### Eingabefelder

#### Gegenstand

Mit dem Prozessschritt ***Dateihandhabung*** können die folgenden Aufgaben erfüllt werden, die im Eingabefeld Gegenstand auswählbar sind:

- **Datei Name:** Gibt den Namen der Datei im Feld „Gefundener Text“ und die Anzahl der Dateien des Ergebnisses basierend auf den ausgewählten Kriterien zurück.
- **Datei öffnen:** Öffnet die angegebene Datei mit der im Betriebssystem definierten Standardanwendung.
- **Datei kopieren:** Kopiert eine definierte Datei in ein anderes Verzeichnis. Die Datei kann während des Kopiervorgangs umbenannt werden.
- **Datei verschieben:** Verschiebt die Datei von einem Verzeichnis in ein anderes. Auch hier ist eine Umbenennung der Datei möglich.
- **Datei löschen:** Entfernt die angegebene Datei aus dem Pfad.
- **Verzeichnis Name:** Gibt den vollständigen Ordnerpfad ohne Dateiname/-endung zurück.
- **Verzeichnis öffnen:** Öffnet das angegebene Verzeichnis (analog zu „Datei öffnen“).
- **Verzeichnis verschieben:** Verschiebt den Ordner in ein Zielverzeichnis.
- **Verzeichnis zippen:** Der angegebene Ordner wird in eine Zip-Datei umgewandelt.

#### Quelle

Legt das Verzeichnis fest, in dem sich die Datei befindet. Es wird automatisch gesetzt, wenn der Dateiname im Dialog „Datei öffnen“ ausgewählt wird.

#### Dateiname

Eine bestimmte Datei kann direkt ausgewählt oder mit einem Muster beschrieben werden. Es können Muster wie `.*` für jeden Dateityp gewählt werden.

Wenn z. B. alle Namen von PDF-Dateien gesucht werden sollen, kann man dies durch Eingabe von `*.pdf` in das Feld Dateiname erreichen.

Wenn Muster verwendet werden, können mehrere Dateien gefunden werden. Der Schritt ***Dateihandhabung*** nutzt in diesem Fall immer die erste Datei entsprechend der angegebenen Sortierung und Positionsangabe.

#### Sortierung

Wenn das Muster mehr als ein Ergebnis liefert, werden die Ergebnisse nach der gewählten Sortierreihenfolge sortiert: Name, Änderungsdatum und Größe in aufsteigender und absteigender Reihenfolge.

#### Position

Bestimmt die Position der ausgewählten Datei in der Ergebnisliste auf der Grundlage von Muster und Sortierreihenfolge.

#### Ziel

(Diese Option ist verfügbar, wenn unter Gegenstand „Datei kopieren“, „Datei verschieben“ oder „Verzeichnis zippen“ ausgewählt wurde.)  
Gibt das Zielverzeichnis an, in das die ausgewählte Datei kopiert bzw. verschoben oder das Verzeichnis gezippt werden soll.

#### Überschreiben

(Diese Option ist verfügbar, wenn unter Gegenstand „Datei kopieren“, „Datei verschieben“, „Verzeichnis verschieben“ oder „Verzeichnis zippen“ ausgewählt wurde.)  
Hier kann festgelegt werden, ob die Datei überschrieben werden soll, wenn die Datei im Zielverzeichnis bereits existiert.

#### Neuer Dateiname

(Diese Option ist verfügbar, wenn unter Gegenstand „Datei kopieren“, „Datei verschieben“ oder „Verzeichnis zippen“ ausgewählt wurde.)  
Hier kann ein neuer Dateiname definiert werden, wenn der Name der kopierten bzw. verschobenen Datei geändert werden muss. Wenn in diesem Feld kein Eintrag gemacht wird, wird der alte Dateiname beibehalten.

# E-Mail-Versand

Der Schritt **E-Mail-Versand** ermöglicht es, E-Mails mit konfigurierbarem Inhalt an eine Gruppe von angegebenen Empfängern zu senden. Um den Prozessschritt **E-Mail-Versand** zu verwenden, muss der SMTP-Server (Simple Mail Transfer Protocol) in der globalen Konfiguration von **EMMA** (**EMMA Configuration**) eingerichtet sein.

[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1718984766037.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1718984766037.png) *Abbildung 47 – Hilfsmittel – Prozessschritt „E-Mail-Versand“*

### Eingabefelder

#### Mail an

(analog auch **CC** und **BCC**): Hier wird die E-Mail-Adresse eingetragen, an die die E-Mail gesendet werden soll. Mehrere Adressen müssen durch „;“ getrennt werden.

#### Betreff

Betreff der E-Mail.

#### Anhang

Anhang der E-Mail.

#### Mail Text

Der Text, der per E-Mail gesendet werden soll. Das Referenzieren von Variablen und Ergebnisfeldern kann wie im Schritt [Tippen](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/tippen) erfolgen.

# Schleife

Wenn im Prozessablauf ein oder mehrere Schritte mehrfach ausgeführt werden sollen, kann der Schritt **Schleife** verwendet werden, um die Anzahl der Wiederholungen zu steuern. Bei Verwendung dieses Schritts muss die maximale Anzahl der Wiederholungen festgelegt werden, um Endlosschleifen zu verhindern.

![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-schleife.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-schleife.png) *Abbildung 43 – Hilfsmittel – Prozessschritt „Schleife“*

### Eingabefelder

#### Maximale Anzahl Loops

Maximale Anzahl der Wiederholungen.

#### Bei Max zurücksetzen

Setzt die Zählung der Schleife zurück, wenn die maximale Anzahl der Durchgänge erreicht ist.

Dies ist hilfreich beim Auslesen einer Excel-Datei: Der Zähler wird nach Erreichen eines bestimmten Zeilenwerts zurückgesetzt, bevor die Werte aus der nächsten Spalte gelesen werden.

#### Vor Start zurücksetzen

Setzt den Zähler auf 0 zurück, wenn der Wert „Ja“ gesetzt wird.

Wenn eine Schleife vor dem Erreichen des Maximalwerts beendet wird und nach dem Beenden wieder aufgerufen werden kann, kann eine Variable vom Typ „Boolean“ als Indikator dafür verwendet werden, dass die Schleife wieder bei 0 zu zählen beginnt.

### Zu beachten:

- Es ist möglich, die Schleife bei einem beliebigen Schritt innerhalb der Schleife zu verlassen, ohne die maximale Anzahl der Wiederholungen zu erreichen. In diesem Fall wird die Schleife als „nicht erfolgreich“ protokolliert.
- Eine Schleife wird als erfolgreich protokolliert, wenn sie die maximale Anzahl von Wiederholungen erreicht hat.
- In den Verzweigungsbedingungen muss „Falsch“ für den Nachfolgeschritt innerhalb der Schleife und „Wahr“ für den Nachfolgeschritt außerhalb der Schleife gesetzt werden, um nach Erreichen der maximalen Anzahl von Schleifenwiederholungen ausgewählt zu werden.

# Verschachtelter Prozess

Mit einem **verschachtelten Prozess** kann ein vordefinierter Prozess in einen anderen Prozess integriert werden. Dadurch lassen sich wiederkehrende Abläufe zentral definieren und mehrfach verwenden. Die Variablen werden über den Schritt an den verschachtelten Prozess weitergegeben. Auch die Übergabe von Passwörtern in den aufgerufenen Prozess ist möglich.

[![verchachtelter_prozess_eigenschaften.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/verchachtelter-prozess-eigenschaften.png)](http://192.168.5.129/uploads/images/gallery/2025-06/verchachtelter-prozess-eigenschaften.png) *Abbildung 46 – Hilfsmittel – Prozessschritt „verschachtelter Prozess“*

In den Eigenschaften lässt sich entweder die **ID** des Prozesses direkt angeben oder der gewünschte Prozess kann über den Tab ***Auswahl des verschachtelten Prozesses*** nach Namen ausgewählt werden. Das Feld **ID** wird rot hinterlegt, wenn der Prozess mit der angegebenen ID nicht geladen werden kann oder kein Prozess ausgewählt wurde, etwa wenn `-1` im Feld eingetragen ist.

Nach Auswahl eines verschachtelten Prozesses werden dessen Variablen im unteren Teil des Eigenschaftenfensters angezeigt. Es werden nur Variablen gelistet, deren Schnittstelle auf `Eingehend`, `Ausgehend` oder `Ein/Aus` eingestellt ist und die somit für den aufrufenden Prozess sichtbar sind.

Die Variablen sind namentlich zugeordnet. Eine farbliche Markierung zeigt die Richtung an, in die die Variable übertragen wird.

[![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1706796327489.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1706796327489.png)  
*Abbildung 47 – Verschachtelter Prozess: farbliche Markierung der Variablen*

- **Grün:** Übertragung vom Hauptprozess an den Unterprozess
- **Gelb:** Übertragung vom Unterprozess an den Hauptprozess
- **Rot:** Übertragung zum Unterprozess und zurück

**Hinweis:** Der Variablenfluss gilt ausschließlich zwischen dem Hauptprozess und dem verschachtelten Prozess.

[![prozess_oeffnen.png](http://192.168.5.129/uploads/images/gallery/2025-06/scaled-1680-/prozess-oeffnen.png)](http://192.168.5.129/uploads/images/gallery/2025-06/prozess-oeffnen.png)

Nach der ersten Ausführung des Schritts erscheint im Ergebnisfenster der Button ***Prozess öffnen***, sobald der Schritt markiert wird. Über diesen Button lässt sich der zugehörige verschachtelte Prozess direkt öffnen.

Wurde unter **Verschachtelter Prozess ID** kein Prozess ausgewählt, wird der Schritt grau hinterlegt. Kann der Schritt aus anderen Gründen nicht ausgeführt werden, wird er rot hervorgehoben.

# Entscheidung

Der Entscheidungsschritt lässt eine beliebige Anzahl von Regeln zur Verzweigung innerhalb eines Prozesses zu. Wenn eine zuvor definierte Bedingung zutrifft, wird die dafür angelegte Verzweigung bei der Ausführung des Prozesses ausgewählt. Wenn mehrere Bedingungen zutreffen, wird die erste der definierten Verzweigungen ausgeführt.

![](http://192.168.5.129/uploads/images/gallery/2024-06/screenshot-2024-06-21-172057.png)

Die Entscheidung kann über die folgenden Parameter festgelegt werden:

### Eingabefelder

#### Verzweigungsbedingungen

Im Gegensatz zu anderen Schritttypen kann hier nur der Typ definiert werden, nach dem die Regeln ausgewertet werden. Es stehen die Typen **Boolean**, **Ganzzahl**, **Dezimalzahl**, **Text** und **Datum&amp;Uhrzeit** zur Verfügung. Der Typ bestimmt die zur Auswahl stehenden Relationen für die Entscheidungsregeln. So sind für den Typ **Boolean** nur die Relationen gleich „=“ und ungleich „!=“ verfügbar, während z. B. für den Typ **Text** zusätzlich auch „Beinhaltet“, „Startet mit“ und „Endet mit“ auswählbar sind.

#### Neue Regel hinzufügen

Hier kann eine neue Regel bzw. Zeile hinzugefügt werden.

#### Regel(n) entfernen

Die ausgewählten Regeln bzw. Zeilen werden entfernt.

#### Regelfenster

Die Regeln bestehen immer aus einem **linken** und einem **rechten Wert** und der **Relation**. Die beiden Werte werden durch die in der Spalte **Relation** eingetragene Operation verbunden.

- Ist das Ergebnis „falsch“, wird die nächste Regel ausgewertet.
- Ist das Ergebnis „wahr“, wird der festgelegte Folgeschritt anschließend ausgeführt und alle folgenden Regeln werden dann nicht mehr ausgewertet.

Nach dem Hinzufügen einer neuen Entscheidungsregel kann per Rechtsklick auf das Feld **Linker Wert** oder **Rechter Wert** ein Untermenü zur Auswahl der zu prüfenden Werte geöffnet werden. Hier steht jeweils ein **Konstanter Wert**, eine **Variable** oder ein **Ergebnisfeld** zur Auswahl.

#### Relation

Übersicht über die auswählbaren Relationen abhängig vom gewählten Typ:

<table id="bkmrk-relation-%C2%A0-%C2%A0-%C2%A0-%C2%A0-boo" style="width: 100%; height: 381.037px;"><thead><tr style="height: 46.5057px;"><th align="center" style="width: 8.93825%; height: 46.5057px;">**Relation** </th><th align="center" style="width: 7.74648%; height: 46.5057px;">**Boolean** </th><th align="center" style="width: 8.81907%; height: 46.5057px;">**Ganzzahl**</th><th align="center" style="width: 8.46154%; height: 46.5057px;">**Dezimal-zahl**</th><th align="center" style="width: 8.58149%; height: 46.5057px;">**Datum&amp;Uhrzeit**</th><th align="center" style="width: 6.43476%; height: 46.5057px;">**Text** </th><th align="left" style="width: 51.0076%; height: 46.5057px;">**Beschreibung**</th></tr></thead><tbody><tr style="height: 46.5057px;"><td align="center" style="width: 8.93825%; height: 46.5057px;">=</td><td align="center" style="width: 7.74648%; height: 46.5057px;">x</td><td align="center" style="width: 8.81907%; height: 46.5057px;">x</td><td align="center" style="width: 8.46154%; height: 46.5057px;">x</td><td align="center" style="width: 8.58149%; height: 46.5057px;">x</td><td align="center" style="width: 6.43476%; height: 46.5057px;">x</td><td align="left" style="width: 51.0076%; height: 46.5057px;">wahr, wenn linker und rechter Wert gleich sind; bei Typ Text müssen alle Zeichen übereinstimmen</td></tr><tr style="height: 29.7017px;"><td align="center" style="width: 8.93825%; height: 29.7017px;">!=</td><td align="center" style="width: 7.74648%; height: 29.7017px;">x</td><td align="center" style="width: 8.81907%; height: 29.7017px;">x</td><td align="center" style="width: 8.46154%; height: 29.7017px;">x</td><td align="center" style="width: 8.58149%; height: 29.7017px;">x</td><td align="center" style="width: 6.43476%; height: 29.7017px;">x</td><td align="left" style="width: 51.0076%; height: 29.7017px;">wahr, wenn linker und rechter Wert ungleich sind</td></tr><tr style="height: 29.7017px;"><td align="center" style="width: 8.93825%; height: 29.7017px;">&lt;</td><td align="center" style="width: 7.74648%; height: 29.7017px;"> </td><td align="center" style="width: 8.81907%; height: 29.7017px;">x</td><td align="center" style="width: 8.46154%; height: 29.7017px;">x</td><td align="center" style="width: 8.58149%; height: 29.7017px;">x</td><td align="center" style="width: 6.43476%; height: 29.7017px;"> </td><td align="left" style="width: 51.0076%; height: 29.7017px;">wahr, wenn der linke Wert kleiner als der rechte Wert ist</td></tr><tr style="height: 29.7017px;"><td align="center" style="width: 8.93825%; height: 29.7017px;">&lt;=</td><td align="center" style="width: 7.74648%; height: 29.7017px;"> </td><td align="center" style="width: 8.81907%; height: 29.7017px;">x</td><td align="center" style="width: 8.46154%; height: 29.7017px;">x</td><td align="center" style="width: 8.58149%; height: 29.7017px;">x</td><td align="center" style="width: 6.43476%; height: 29.7017px;"> </td><td align="left" style="width: 51.0076%; height: 29.7017px;">wahr, wenn der linke Wert kleiner oder gleich dem rechten Wert ist</td></tr><tr style="height: 29.7017px;"><td align="center" style="width: 8.93825%; height: 29.7017px;">&gt;</td><td align="center" style="width: 7.74648%; height: 29.7017px;"> </td><td align="center" style="width: 8.81907%; height: 29.7017px;">x</td><td align="center" style="width: 8.46154%; height: 29.7017px;">x</td><td align="center" style="width: 8.58149%; height: 29.7017px;">x</td><td align="center" style="width: 6.43476%; height: 29.7017px;"> </td><td align="left" style="width: 51.0076%; height: 29.7017px;">wahr, wenn der linke Wert größer als der rechte Wert ist</td></tr><tr style="height: 29.7017px;"><td align="center" style="width: 8.93825%; height: 29.7017px;">&gt;=</td><td align="center" style="width: 7.74648%; height: 29.7017px;"> </td><td align="center" style="width: 8.81907%; height: 29.7017px;">x</td><td align="center" style="width: 8.46154%; height: 29.7017px;">x</td><td align="center" style="width: 8.58149%; height: 29.7017px;">x</td><td align="center" style="width: 6.43476%; height: 29.7017px;"> </td><td align="left" style="width: 51.0076%; height: 29.7017px;">wahr, wenn der linke Wert größer oder gleich dem rechten Wert ist</td></tr><tr style="height: 46.5057px;"><td align="center" style="width: 8.93825%; height: 46.5057px;">Beinhaltet</td><td align="center" style="width: 7.74648%; height: 46.5057px;"> </td><td align="center" style="width: 8.81907%; height: 46.5057px;"> </td><td align="center" style="width: 8.46154%; height: 46.5057px;"> </td><td align="center" style="width: 8.58149%; height: 46.5057px;"> </td><td align="center" style="width: 6.43476%; height: 46.5057px;">x</td><td align="left" style="width: 51.0076%; height: 46.5057px;">wahr, wenn der Text im rechten Wert im Text des linken Werts enthalten ist</td></tr><tr style="height: 46.5057px;"><td align="center" style="width: 8.93825%; height: 46.5057px;">Startet mit</td><td align="center" style="width: 7.74648%; height: 46.5057px;"> </td><td align="center" style="width: 8.81907%; height: 46.5057px;"> </td><td align="center" style="width: 8.46154%; height: 46.5057px;"> </td><td align="center" style="width: 8.58149%; height: 46.5057px;"> </td><td align="center" style="width: 6.43476%; height: 46.5057px;">x</td><td align="left" style="width: 51.0076%; height: 46.5057px;">wahr, wenn der Text des linken Werts mit dem Text des rechten Werts beginnt</td></tr><tr style="height: 46.5057px;"><td align="center" style="width: 8.93825%; height: 46.5057px;">Endet mit</td><td align="center" style="width: 7.74648%; height: 46.5057px;"> </td><td align="center" style="width: 8.81907%; height: 46.5057px;"> </td><td align="center" style="width: 8.46154%; height: 46.5057px;"> </td><td align="center" style="width: 8.58149%; height: 46.5057px;"> </td><td align="center" style="width: 6.43476%; height: 46.5057px;">x</td><td align="left" style="width: 51.0076%; height: 46.5057px;">wahr, wenn der Text des linken Werts mit dem Text des rechten Werts endet</td></tr></tbody></table>

<p class="callout info">Wir empfehlen, als letzte Regel eine Regel zu erstellen, die immer zutrifft: beispielsweise 1 = 1. So wird verhindert, dass der Prozess abbricht.</p>

# Warten

Bei einigen Prozessen ist es erforderlich, der Anwendung an bestimmten Punkten während des Laufs etwas Zeit für bestimmte Aktionen zu geben oder auf eine Bestätigung oder Eingabe des Benutzers zu warten. Dieser Schritttyp ermöglicht es dem System, dies zu realisieren.

[![240621 Warten.png](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/240621-warten.png)](http://192.168.5.129/uploads/images/gallery/2024-06/240621-warten.png) *Abbildung 42 – Hilfsmittel – Prozessschritt „Warten“*

### Eingabefelder

#### Gegenstand

Worauf soll gewartet werden: Zeit, Bestätigung oder Eingabe.

- **Zeit:** Der Prozess wird mit dem nächsten Prozessschritt fortgesetzt, sobald die Zeit für den Timeout abgelaufen ist.
- **Bestätigung:** Es öffnet sich ein Bestätigungsfenster und der Prozess wird mit dem nächsten Prozessschritt fortgesetzt, sobald die Zeit für den Timeout abgelaufen ist oder ein Benutzer die Meldung bestätigt hat.
- **Eingabe:** Es wird ein Eingabefenster geöffnet und der Prozess wird mit dem nächsten Prozessschritt fortgesetzt, sobald die Zeit für den Timeout abgelaufen ist oder ein Benutzer die Eingabe bestätigt hat.

#### Timeout (ms)

Dauer der Wartezeit in Millisekunden. Bei Auswahl der Optionen **Bestätigung** oder **Eingabe** wird der Schritt nach Ablauf der Zeit mit dem Status „nicht erfolgreich“ abgebrochen, sofern vorher keine Bestätigung oder Eingabe durch einen Benutzer erfolgt ist. Wird der Wert auf 0 gesetzt, wird die Zeitüberschreitung nicht berücksichtigt und im Eingabefenster ist zwingend eine Benutzeraktion erforderlich.

#### Meldung

Bei Bestätigung und Eingabe wird ein Eingabefenster mit der entsprechenden Meldung angezeigt.  
Die ersten 50 Zeichen des Kommentars werden dabei als Überschrift des Eingabefensters verwendet.

# Erfolg

Mithilfe des Prozessschritts ***Erfolg*** wird ein Prozess beendet. Jeder Prozess benötigt einen Prozessschritt ***Erfolg***, da ein Prozess andernfalls als abgebrochen beendet wird. Der Prozessschritt ***Erfolg*** bildet damit das Ende eines Prozesses, so wie der Prozessschritt ***Start*** den Anfang eines Prozesses darstellt.

# Erweiterte Konfigurationsoptionen

Erweiterte Textspezifikation für die Schritte ***Finden**,* **Lesen** und ***Formular lesen***

Bei den oben genannten Prozessschritten kann eine Feinabstimmung des OCR-Prozesses erreicht werden, indem nicht nur ein RegEx im entsprechenden Feld angegeben wird, sondern auch sogenannte erweiterte Konfigurationsoptionen hinzugefügt werden.

- Jede Option muss von geschweiften Klammern **{...}** umgeben sein.
- Es können mehrere Optionen hintereinander angegeben werden.
- Da diese Optionen auch viele Standardparameter überschreiben können, ist dies besonders nützlich, wenn eine programmatische Anpassung der Einstellungen erforderlich ist.

<p class="callout info">**Hinweise:**  
• Viele dieser Optionen überschreiben die Standardparameter des Schritts – praktisch für eine programmatische Anpassung.  
• Für Dezimalzahlen muss ein Punkt verwendet werden (z. B. `0.5`), kein Komma.</p>

#### Verfügbare Optionen:

---

- **FO:** Find Options \[ CaseSensitive | WholeWord | RemoveNoise | EnhanceContrast | Resolution | Invert | MinScore | PageRotation | ReduceNoise | EqualizeBrightness \]
- **PROFILE:** definiert den TextExtractionMode \[ Default, Fast, Accurate, Field \]
- **<span lang="FR" style="mso-ansi-language: FR;">MODE:</span>**<span lang="FR" style="mso-ansi-language: FR;"> definiert TextEnhancements \[ None, Default, Text, Table, ForceTables \]</span>
- **UP:** lädt ein ABBYY-Benutzerprofil aus dem cfg-Verzeichnis
- **TEXTFILEMARKINGTYPE oder TFMT:** definiert Markierungen von Text- oder Zeichenfeldern (z. B. Rahmen, Kästchen)
- **TEXTLANGUAGE oder TL:** legt die Sprache(n) fest, mit denen die OCR-Ergebnisse abgeglichen werden
- **TEXTTYPES oder TT:** legt die Schriftarten/Texttypen fest, die bei der Zeichenerkennung berücksichtigt werden
- **FILE:** Datei, aus der die OCR-Extraktion erfolgen soll
- **PAGES:** OCR-Extraktion nur aus bestimmten Seiten der Quelldatei
- **DICTIONARY oder DICT:** Wörterbuchdatei mit einer Liste von Begriffen, die zusätzlich erkannt werden sollen

---

##### **1. Find Options – FO**

{FO:&lt;Option&gt;=&lt;Wert&gt;}

**Optionen:**

- CaseSensitive = \[ TRUE | FALSE \]
- WholeWord = \[ TRUE | FALSE \]
- RemoveNoise = \[ TRUE | FALSE \]
- EnhanceContrast = \[ TRUE | FALSE \]
- Resolution = \[ 0 | 1 | &lt;50–400&gt; \]
- Invert = \[ TRUE | FALSE \]
- Zoom = \[ 1 | &lt;0.1–4.0&gt; \]
- MinScore = \[ 0–1.0 \]
- PageRotation = \[ OFF | AUTO \]
- <span lang="EN-US" style="mso-ansi-language: EN-US;">NoiseReduction = \[ NONE | JPEG | ISO | BOTH \]</span>
- EqualizeBrightness = \[ TRUE | FALSE \]

**Beispiele:**

- {FO:CaseSensitive=False} → Groß-/Kleinschreibung wird ignoriert
- {FO:MinScore=0.5} → alle Texte mit einer OCR-Confidence &lt; 0.5 werden entfernt

##### **2. TextExtractionMode – PROFILE**  



{PROFILE:\[Default | Fast | Accurate | Field\]}

**Beispiel:**  
{PROFILE:Fast} → Text wird im „Fast“-Modus gefunden

##### **3. TextEnhancements – MODE**  


<span lang="FR" style="mso-ansi-language: FR;">{MODE:\[None | Default | Text | Table | ForceTables\]}</span>

**Beispiel:**  
{MODE:Table} → OCR wird für Tabellenerkennung optimiert

##### **4. User Profile – UP**  


{UP:&lt;Dateiname&gt;}

**Beispiel:**  
{UP:read.up} → User Profile read.up wird aus dem config-Verzeichnis geladen.

Da die Optionen in der Profildatei viele Abhängigkeiten haben, bitte nur vom Kundensupport bereitgestellte Profile verwenden.

> \[RecognizerParams\]
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">; TextLanguage = English</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">; LowResolutionMode = false</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;"> </span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">\[PageAnalysisParams\]</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">; AggressiveTableDetection = true</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">DetectPictures = true</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">DetectTables = true</span>
> 
> <span lang="EN-US" style="mso-ansi-language: EN-US;">DetectText = true</span>
> 
> EnableExhaustiveAnalysisMode = true

##### **5. TEXTFILEMARKINGTYPE – TFMT** 

{TFMT:\[SimpleText | UnderlinedText | TextInFrame | GrayBoxes | CharBoxSeries | SimpleComb | CombInFrame | PartitionedFrame\]}

**Beispiel:**  
{TFMT:UnderlinedText} → Unterstreichungen unter Zeichen werden ignoriert

##### **6. TEXTLANGUAGE – TL**

{TL:&lt;Sprache1, Sprache2, ...&gt;}

**Beispiel:**  
{TL:German, English} → deutsche und englische Wörterbücher werden verwendet

##### **7. TEXTTYPES – TT** 

{TT:\[Normal | Typewriter | Matrix | Index | Handprinted | OCR\_A | OCR\_B | MICR\_E13B | MICR\_CMC7 | Gothic | Receipt\]}

**Beispiel:**  
{TT:Matrix, Receipt} → Matrix- oder Receipt-Schriften werden erkannt

##### **8. FILE**  


{FILE:&lt;Dateipfad&gt;}

**Beispiel:**  
{FILE:C:\\Users\\tom\\Documents\\fünfzehn bis vierundzwanzig.png}

##### **9. PAGES**  


{PAGES:&lt;Definition&gt;}

Unterstützte Syntax (wie in Druckdialogen):

- {Page:5} → nur Seite 5
- {Page:3-7} → Seiten 3 bis 7
- {Page:2,5,9} → Seiten 2, 5 und 9

##### **10. DICTIONARY – DICT** 

{DICT:&lt;Dateipfad&gt;}

**Beispiel:**  
{DICT:classifications.txt} → Wörter aus classifications.txt werden geladen und die Standardwörterbücher damit ergänzt.

# Gruppieren

Durch das Gruppieren von Prozessschritten wird die Struktur des Ablaufdiagramms verbessert und somit die Lesbarkeit und das Verständnis komplexer Arbeitsabläufe erleichtert.

Gruppierte Schritte werden in einem farblich hinterlegten Kasten dargestellt. Der Name der Gruppe erscheint zentriert am unteren Rand des Kastens.

[![GroupVisualizazion.png](http://192.168.5.129/uploads/images/gallery/2024-05/scaled-1680-/groupvisualizazion.png)](http://192.168.5.129/uploads/images/gallery/2024-05/groupvisualizazion.png)

### Voraussetzungen

Bevor eine Gruppe erstellt werden kann, muss mindestens ein Schritt ausgewählt werden.  
Es gibt zwei Möglichkeiten, mehrere Schritte auszuwählen:

- Rahmenauswahl:  
    Die STRG-Taste gedrückt halten und mit der linken Maustaste einen Rahmen um die gewünschten Schritte ziehen.
- Einzelauswahl:  
    Die SHIFT-Taste gedrückt halten und mit der linken Maustaste nacheinander auf die gewünschten Schritte klicken, um sie zur Auswahl hinzuzufügen.

#### Gruppe erstellen

1. Die gewünschten Schritte wie oben beschrieben auswählen.
2. Mit der rechten Maustaste auf einen ausgewählten Schritt klicken, um das Kontextmenü zu öffnen.
3. Die Option **Gruppe erstellen** auswählen.

#### Gruppe löschen

Es gibt drei Möglichkeiten, eine Gruppe zu löschen:

1. - Mit dem Radiergummi-Werkzeug:  
        Das Radiergummi-Symbol im linken Werkzeugmenü auswählen und anschließend in den Gruppenkasten klicken.
    - Über das Kontextmenü  
        Mit der rechten Maustaste in den Gruppenkasten klicken und die Option **Löschen** aus dem Kontextmenü auswählen.
    - Mit der Entfernen-Taste (DEL)  
        Einmal mit der linken Maustaste in den Gruppenkasten klicken, um die Gruppe auszuwählen. Anschließend die ENTF-Taste auf der Tastatur drücken.

### Eingabefelder

#### Color

Eine der drei verfügbaren Farben **Orange**, **Grün** oder **Blau** auswählen, um die Gruppe visuell hervorzuheben.

#### Group Name

Hier den gewünschten Namen der Gruppe eingeben.  
Standardmäßig wird der Name `Gruppe` verwendet.  
Der Name wird mittig unter dem farblich hinterlegten Gruppenkasten angezeigt.

#### Comment

In diesem optionalen Feld kann eine Anmerkung zum Zweck oder zur Bedeutung der Gruppe hinzugefügt werden.  
Dies ist besonders hilfreich für die Dokumentation und die Zusammenarbeit im Team.

# Prozessgruppe

Prozesse können in Prozessgruppen gruppiert und nacheinander ausgeführt werden. Ein Prozess kann beliebig oft in einer Prozessgruppe vorkommen. Die orangefarbene Doppellinie in der Mitte kann vertikal verschoben werden, um die beiden Bildbereiche links und rechts zu vergrößern bzw. zu verkleinern.

[![Prozessgruppe.png](http://192.168.5.129/uploads/images/gallery/2025-07/scaled-1680-/prozessgruppe.png)](http://192.168.5.129/uploads/images/gallery/2025-07/prozessgruppe.png) *Abbildung 74 – Prozessgruppe*

Der Benutzer kann den Namen und die Beschreibung einer Prozessgruppe frei wählen.

Wird die Option `Prozessgruppe anhalten, wenn ein Prozess fehlschlägt` aktiviert, wird die Ausführung der gesamten Prozessgruppe automatisch abgebrochen, sobald einer der Prozesse fehlschlägt. Diese Option ist sinnvoll, wenn die Prozesse so voneinander abhängen, dass ein Fehler in einem Prozess eine sinnvolle Weiterführung der aktuellen Prozessgruppe unmöglich macht.

Bei der Verwendung von Variablen in einem Prozess können diese von der Prozessgruppe oder der Queue vorbelegt werden. So ist es auf Ebene der Prozessgruppen oder Queues beispielsweise möglich, User Credentials mithilfe von Variablen zuzuweisen. Dazu werden in der Prozessgruppe Variablen mit demselben Namen wie im Prozess angelegt und ein anderer Wert zugewiesen. Dadurch werden die Variablen des Prozesses überschrieben, wenn die Prozessgruppe oder Queue ausgeführt wird.

### Prozessgruppensteuerung

#### Neu [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139661324.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139661324.png)

Öffnet einen Tab mit einer neuen Prozessgruppe.

#### Öffnen [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139667837.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139667837.png)

Zeigt die Übersicht aller in der Datenbank gespeicherten und für den Benutzer verfügbaren Prozessgruppen an, um eine in der Vergangenheit gespeicherte Prozessgruppe auswählen und öffnen zu können.

#### Speichern [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139674621.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139674621.png)

Speichert die Prozessgruppe und überschreibt die bestehende Gruppe, sofern notwendig. Nach dem Speichern kann die Prozessgruppe gesperrt werden. Andernfalls können andere Benutzer keine Änderungen an der Prozessgruppe vornehmen.

#### Hilfe [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139679422.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139679422.png)

Öffnet das **EMMA Studio Benutzerhandbuch**.

#### Starten [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139702605.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139702605.png)

Startet den Durchlauf einer Prozessgruppe, beginnend mit dem ersten Prozess.

#### Folgende [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139835150.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139835150.png)

Startet den Durchlauf einer Prozessgruppe, beginnend bei dem markierten Prozess, und führt nur die folgenden Prozesse aus.

#### Stop [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139844638.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139844638.png)

Beendet den Durchlauf der Prozessgruppe zum Ende des aktuell laufenden Prozesses.

#### (Ent)Sperren [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139852853.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139852853.png)

Sperrt bzw. entsperrt die Prozessgruppe für die Bearbeitung auf Basis des Benutzernamens. Die einzelnen Prozessgruppen lassen sich im gesperrten Zustand anzeigen, jedoch nicht bearbeiten.

#### Minimiert [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139861948.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139861948.png)

Ist diese Option nicht aktiviert, bleibt **EMMA Studio** im Vordergrund, wenn eine Prozessgruppe ausgeführt wird. Andernfalls minimiert sich **EMMA Studio** selbst, während eine Prozessgruppe ausgeführt wird.

#### Zurücksetzen [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707139870029.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707139870029.png)

Setzt den letzten Lauf zurück (Status, Variablen).

# Plan

Pläne dienen zur automatischen Ausführung von Prozessen. Zu diesem Zweck müssen die Prozesse in Prozessgruppen organisiert werden. Die Startzeit bestimmt, wann die automatisierte Durchführung der Prozessgruppen beginnt.

 [![](http://192.168.5.129/uploads/images/gallery/2024-02/scaled-1680-/image-1707743352094.png)](http://192.168.5.129/uploads/images/gallery/2024-02/image-1707743352094.png)

### Eingabefelder

#### Start

Datum und Uhrzeit, wann der Plan starten soll.

#### Plan Name

Name des Plans

#### Beschreibung

Beschreibung des Plans

#### Wiederholungen

Geplante Wiederholungen des Plans

#### Variablen

Variablen, die in allen Prozessgruppen benutzt werden sollen

#### E-Mail

Bei Ereignissen von Prozessen, Prozessgruppen und Plänen kann eine E-Mail-Benachrichtigung versendet werden.   
Zur Verwendung dieser Funktion muss in **EMMA Configuration** unter **Global Values** der E-Mail-Server konfiguriert werden.

#### Auswahl der **EMMA**-Instanzen

Auswahl, auf welcher **EMMA**-Instanz (Installation/Server) der Plan ausgeführt werden soll.  
Der Unterschied in der Auswahl zwischen „All“ und einzelner Instanzen besteht darin, dass „All“ auch nachträglich installierte **EMMA**-Instanzen einschließt.

Werden mehrere **EMMA**-Instanzen ausgewählt, wird der Plan von der ersten **EMMA**-Instanz ausgeführt, die zum Startzeitpunkt frei ist.  
Diese dient zur Sicherung gegen den Ausfall einer **EMMA**-Instanz bei gleichzeitiger Erhöhung der Verfügbarkeit freier **EMMA**-Instanzen.

<p class="callout info">**ACHTUNG:**  
Die Variablen der Prozessgruppe oder der Queue werden bei deren Start mit den unter ***Plan*** angegebenen Werten überschrieben (so wie auch die Variablen des Prozesses mit denen der Prozessgruppe oder Queue überschrieben werden). Hierbei ist zu beachten, dass die Variablen denselben Namen wie in der Prozessgruppe oder Queue (bzw. im Prozess) haben müssen. Wenn ein Wert einer Variable von einem Plan zu einem Prozess übergeben werden soll, muss diese Variable auch in der entsprechenden Prozessgruppe oder Queue deklariert sein.  
</p>

## Wiederholungen

Bei Klick auf den Button ***Wiederholungen*** öffnet sich die Eingabemaske zur Definition der Wiederholungen:  
[![](http://192.168.5.129/uploads/images/gallery/2024-06/scaled-1680-/image-1719571951531.png)](http://192.168.5.129/uploads/images/gallery/2024-06/image-1719571951531.png)

### Eingabefelder

#### Serienmuster

Festlegung der Anzahl der Wiederholungen. Ein Plan kann zu beliebig wiederkehrenden Zeitpunkten starten – alle x Minuten, Stunden, Tage oder auch Jahre.

#### Wochentage

Die Wochentage, an denen der Plan ausgeführt wird. Fällt die Ausführung des Plans auf einen nicht markierten Wochentag, wird dieser Durchlauf ausgelassen.

#### Seriendauer

Legt fest, wie oft der Plan laufen soll. Hier wird entweder die Anzahl der Wiederholungen angegeben (der erste Durchlauf wird durch die eingestellte Startzeit des Plans bestimmt) oder der Endzeitpunkt definiert.

- **Endet nach**: Mit dieser Option wird festgelegt, dass die Wiederholung nach der angegebenen Anzahl beendet wird. So wird der Zeitpunkt der letzten Ausführung eingeschränkt durch: `Startzeitpunkt + ("Serienmuster" * (Anzahl der Ausführungen - 1)).` Hier ist also darauf zu achten, dass das Serienmuster nicht zu klein gewählt wird, da sonst nicht alle Wiederholungen durchgeführt werden können.
- **Endet am:** Mit dieser Option wird der letztmögliche Startzeitpunkt festgelegt.

# Reports

Die Ergebnisse der in einem Plan enthaltenen Prozesse werden nach jeder Ausführung automatisch in einem Report protokolliert.

Über das Menü ***Datei → Report*** wird die interaktive Reportanzeige geöffnet.

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-07/scaled-1680-/pJHimage.png)](http://192.168.5.129/uploads/images/gallery/2024-07/pJHimage.png)

   
*Abbildung 82 – Reports – Interaktiv*

In dieser Anzeige nimmt der Detailgrad der Bearbeitungsfelder von links nach rechts zu. Oben links wird das Zeitfenster ausgewählt, um nur Reports anzuzeigen, die in einem bestimmten Zeitraum erstellt wurden.  
Darunter werden alle Pläne geladen, die in diesem Zeitraum ausgeführt wurden. Wenn man eine der Zeilen auswählt, werden alle zugehörigen Pläne, Prozessgruppen und Prozesse dieser Ausführung angezeigt.

Zusätzlich kann nach Plänen anhand ihres Namens, der Hardware, auf der sie ausgeführt wurden, sowie anhand des zugehörigen Projekts und der Umgebung gesucht werden.

Wird eine der Prozessgruppen ausgewählt, erscheinen im dritten Bereich die zugehörigen Prozesse. Erfolgreich abgeschlossene Pläne, Prozessgruppen und Prozesse werden dabei grün angezeigt, übersprungene gelb und fehlgeschlagene rot.

Die Details des ausgewählten Prozesses werden rechts neben dem Report angezeigt: Beschreibung, erwartetes Ergebnis, Referenz sowie die im Prozess verwendeten Variablen. Darunter werden alle Prozessschritte in der Reihenfolge aufgelistet, in der sie von **EMMA** verarbeitet wurden. Schritte in Schleifen erscheinen dabei mehrfach in der tatsächlichen Ausführungsreihenfolge.

Mit den Pfeiltasten der Tastatur oder Mausklicks kann zwischen den Feldern navigiert werden, in denen `Ausgeführt` und `Nächster Schritt gefunden` hervorgehoben sind. Nur die Kombination beider Felder zeigt an, ob ein Prozessschritt erfolgreich abgeschlossen wurde.

Prozesse können aus dieser Ansicht heraus per Doppelklick auf die `SchrittID` zusammen mit den zugehörigen Ergebnissen im Prozesseditor geöffnet werden.

Die Größe der einzelnen Tabellenbereiche kann durch vertikales oder horizontales Verschieben der orangefarbenen Trennlinien angepasst werden. Zusätzlich lassen sich die Einträge in der Tabelle durch einen Klick auf die jeweilige Spaltenüberschrift nach dem Wert dieser Spalte sortieren.

Beispiel:

Ein Prozessschritt vom Typ ***Schleife*** liefert nur dann `Ausgeführt` = `True`, wenn die maximale Anzahl an Durchläufen erreicht wurde. Solange bei einem Schritt `Ausgeführt` = `False` steht, aber `Nächster Schritt gefunden` = `True` ist, wird der Prozess fortgesetzt. Der Schritt ***Erfolg*** ist der einzige Prozessschritt, bei dem bei einem erfolgreichen Abschluss `Nächster Schritt gefunden` = `False` auftreten darf*.*

Wird auf der rechten Seite eine gesamte Zeile eines Prozessschritts ausgewählt, erscheint unten rechts das zugehörige Beweisbild, das während der Ausführung erstellt wurde. Bei dem Prozessschritt **[Hören](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/horen "Hören")** kann der aufgezeichnete Ton durch Doppelklick auf die entsprechende Zeile abgespielt werden. Beweisbilder können per Doppelklick vergrößert oder verkleinert werden.

## Reportfilter und -abfragen

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-07/scaled-1680-/yztimage.png)](http://192.168.5.129/uploads/images/gallery/2024-07/yztimage.png)

Der obere Bereich der Reportanzeige dient zur Filterung und Abfrage der Reports anhand der gewählten Parameter.

Bei jeder Änderung an den Filterparametern werden die Ergebnisse automatisch aktualisiert. Änderungen an den Abfrageparametern hingegen werden erst bei Klick auf den Button **Anwenden** übernommen.

### Reportabfragen

#### Von/Bis

Bestimmt das Zeitfenster der Ausführung der Pläne, zu denen Reports geladen werden sollen.

#### Projekt

Legt fest, aus welchem Projekt die Reports stammen. Bei Auswahl von „Any“ werden alle Projekte berücksichtigt, auf die der Benutzer Zugriff hat.

#### Umgebung

Bestimmt, aus welcher Umgebung die Reports stammen. Bei Auswahl von „Any“ werden alle Umgebungen berücksichtigt, auf die der Benutzer Zugriff hat.


### Filter

#### Name

Zeigt alle Reports an, deren zugehöriger Planname den Suchbegriff enthält.

#### Hardware

Zeigt alle Reports an, die auf einer bestimmten Hardware (bzw. **EMMA**-Instanz) ausgeführt wurden.

#### Status

Filtert Reports nach Abschlussstatus: „Erfolg“, „Fehler“ oder „Verworfen“.  
Eine Mehrfachauswahl ist möglich, indem während der Auswahl die SHIFT-Taste gedrückt wird.


#### Pläne je Seite:

Legt fest, wie viele Reports pro Seite angezeigt werden.  
Die Anzeige ist seitenbasiert: Wird das Ende einer Seite erreicht, wird automatisch die nächste (bzw. vorherige) Seite geladen.

<p class="callout info">**ACHTUNG:**  
Wenn sehr viele Reports auf einer Seite geladen werden, kann dies aufgrund der großen Datenmenge zu längeren Ladezeiten führen.  
</p>

### Prozessschritttabelle

In dieser Tabelle werden alle ausgeführten Prozessschritte chronologisch zusammen mit ihren Ergebnissen aufgelistet. Sie enthält folgende Spalten:

#### Startzeit

Datum und Uhrzeit, wann der Prozess gestartet wurde.

#### Typ

Art des Prozessschritts.

#### SchrittID

Ursprüngliche ID des Prozesses im Ablaufdiagramm. Wird ein Schritt mehrfach ausgeführt (z. B. innerhalb einer Schleife), erscheint er auch mehrfach in der Tabelle.

<p class="callout info">Bei einem Doppelklick auf das Feld **SchrittID** eines Prozessschritts wird der Prozess mit seinen Reportdaten in den Graph-Editor geladen und ausgewählt.</p>

#### Ausgeführt

Gibt an, ob der Prozessschritt erfolgreich ausgeführt wurde.

#### Nächster Schritt gefunden

Gibt an, ob für die im Prozessschritt definierte Verzweigungsbedingung und das Ergebnis von `Ausgeführt` ein nachfolgender Schritt gefunden wurde.

#### Score

Wahrscheinlichkeit des Ergebnisses, falls vorhanden. (0 &lt; Score &lt; 1)

#### Farbwert

Faktor für die Farbübereinstimmung, falls vorhanden. (0 &lt; Farbe &lt; 1)

#### Anzahl 

Anzahl der Treffer, falls vorhanden.

#### Laufzeit

Zeit in Millisekunden, die für die Ausführung benötigt wurde.

#### X/Y

X- bzw. Y-Koordinate des Ergebnisses, falls vorhanden.

#### Kommentar

Kommentare, die zu diesem Prozessschritt hinterlegt wurden. Sie dienen dem besseren Verständnis des Ablaufs.

#### Gefundener Text

Falls die Texterkennung aktiviert ist (z. B. bei den Schritten **[Finden](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/finden "Finden Schritt")** und **[Lesen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/lesen "Lesen Schritt")**), wird hier der erkannte Text angezeigt.  
Auch Schritte wie [I**mport**](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/import "Import Schritt"), **[Export](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/export "Export Schritt")** oder **[Formular lesen](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/formular-lesen "Formular lesen Schritt")** liefern hier ihre Ergebnisse.  
Bei Schritten wie **[Start](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/start "Start Schritt")** oder **[Schleife](http://da-doku.ottrobotics.de/books/emma-studio-27-benutzerhandbuch/page/schleife "Schleife Schritt")** wird hingegen kein Text angezeigt, da diese keinen erkannten Text erzeugen.

## PDF-Export

Es besteht die Möglichkeit, eine druckbare Version des Reports zu erstellen. Über den Button ***Report*** mit dem Druckersymbol in der oberen Menüleiste wird die Generierung dieses Reports im PDF-Format gestartet. Dabei kann ausgewählt werden, welche Teile des Reports aufgenommen werden sollen. Zudem können Berichtsbilder generiert werden, die zusätzlich in Unterordnern gespeichert werden.

[![image.png](http://192.168.5.129/uploads/images/gallery/2024-07/scaled-1680-/tvtimage.png)](http://192.168.5.129/uploads/images/gallery/2024-07/tvtimage.png)

Der druckbare Report wird in vier unterschiedlichen Detailgraden erstellt:

- Plan Ansicht
- Prozessgruppen Ansicht
- Prozess Ansicht
- Bilder

Beim Export des Reports wird ein Ordner erstellt, dessen Name das Ausführungsdatum, die interne Report-ID, die Laufzeit in Minuten sowie die ID des ausgeführten Plans enthält. Die erzeugte PDF-Datei trägt denselben Namen wie der Ordner, in dem sie gespeichert wird.

<p class="callout info">Da Reports mit Bildern sehr groß werden können, lässt sich der Export auf eine einzelne Prozessgruppe oder einen bestimmten Prozess beschränken. Hierzu wählt man das gewünschte Element im Reportbaum aus, bevor der Export gestartet wird. In diesem Fall wird der Report nur für das gewählte Element und dessen abhängige Prozesse erzeugt.</p>

### Plan Ansicht

Direkt nach dem Deckblatt wird der ausgeführte Plan angezeigt. Dargestellt werden der Name, die ID der **EMMA**-Instanz, auf der der Plan ausgeführt wurde, der Start- und Endzeitpunkt, die Anzahl der enthaltenen Prozessgruppen und Prozesse sowie die Zahl der erfolgreichen und fehlgeschlagenen Prozesse. Zusätzlich werden erfolgreiche und fehlgeschlagene Prozesse in einem Tortendiagramm visualisiert.

### Prozessgruppen Ansicht

Es folgt die Ansicht der einzelnen Prozessgruppen in chronologischer Reihenfolge. Hier lässt sich einsehen, welche Prozesse innerhalb einer Prozessgruppe erfolgreich abgeschlossen wurden und welche fehlgeschlagen sind.

### Prozess Ansicht

In dieser Ansicht werden die Prozesse in chronologischer Reihenfolge dargestellt, inklusive aller Prozessschritte und benutzten Variablen.  
Aus Gründen der Übersichtlichkeit und zur Optimierung der Dateigröße sind während der Ausführung erstellte Bilder hier nicht enthalten.

### Bilder

Wenn beim Export die Option `Bilder` gewählt wurde, werden diese nach folgendem Schema benannt und zusätzlich zur PDF-Datei in Unterordnern abgelegt:

Hauptordner: &lt;Startdatum und -uhrzeit des Plans&gt;\_Plan\_&lt;Nr. des Plans&gt;\_Report\_&lt;ID des Reports&gt;

Beispiel: Der Report von Plan-Nr. 18 mit Start am 16.07.2024 um 01:47:04 Uhr und der Report ID = 57727 wird im folgenden Hauptordner abgelegt: 2024-07-16\_014704\_Plan\_18\_Report\_57727.

Für die Bilder wird je Prozess ein eigener Unterordner mit folgendem Namensschema erstellt:

&lt;Startdatum und -uhrzeit des Prozesses&gt;\_Plan\_&lt;Nr. des Plans&gt;\_Prozess\_&lt;ID des Prozesses&gt;\_Bilder

Beispiel: Für Prozess-Nr. 289, der in Plan 18 am 16.07.2024 um 13:47:05 Uhr ausgeführt wurde, werden die Bilder in folgendem Verzeichnis gespeichert: 2024-07-16\_134705\_Plan\_18\_Prozess\_289\_Bilder

<p class="callout info">Exportierte Bilder können sensible Informationen enthalten und sollten daher mit entsprechender Sorgfalt behandelt werden.</p>

# Fehlerbehebung in EMMA Studio

### Ereignisprotokollierung

In **EMMA Studio** (wie auch in anderen **EMMA**-Anwendungen) wird eine umfassende Logdatei erstellt. In dieser Datei werden alle durchgeführten Schritte und Ereignisse während der Nutzung der Software protokolliert.

Die Logdatei befindet sich im folgenden Ordner:  
*%AppData%\\OTTRobotics\\Emma Studio\\Log*  
Die Benennung erfolgt nach dem jeweiligen Datum, z. B. 20241207.log

Nachfolgend ein Beispielausschnitt aus einer **EMMA Studio**-Logdatei:

> 22-03-2025 00:06:51.730: Information: --------------------------------------------------------------------------------------------------;  
> 22-03-2025 00:06:51.730: Information: Starting Emma Studio Version: 2.7.1.229-Fri 02/21/2025 ;  
> 22-03-2025 00:06:52.339: Information: The provided command to excute a schedule is not recognized.;  
> 22-03-2025 00:07:48.578: Information: SetConnectionInformation Server: emma-vmdb.test.emma,58495 DB: RegTestDB\_v2.8 User: EmmaStudio DomainAccount: False;

Ein Eintrag in einer Logdatei besteht aus folgenden Informationen:

1. Zeitstempel – Zeitpunkt, zu dem das Ereignis erfasst wurde
2. LogLevelString: Schweregrad des Ereignisses:  
    
    - Information: Normales Ereignis während des Betriebs, kein Fehler
    - Warnung: Unerwartetes Ereignis, das die Funktion nicht blockiert
    - Kritisch: Schwerwiegendes Ereignis, das zu einem Fehler oder Systemabbruch führen kann
3. Statusmeldung: Textliche Zusammenfassung des Ereignisses mit Details zum Prozess und zu den verarbeiteten Daten. Je nach Ereignistyp kann die Meldung Informationen wie die Prozess-ID, Schritt-ID usw. enthalten.

### Log-Historie

Die meisten Logeinträge können direkt in der Benutzeroberfläche von **EMMA Studio** eingesehen werden:

- Über das Menü ***Hilfe* → *Status***
- Durch Klick auf die orangefarbene Statuszeile unten in der Editoransicht (Prozess/Prozessgruppe/Zeitplan)

Die Statusansicht im Menü ***Hilfe*** zeigt allgemeine Meldungen der Kategorien „Warnung“ und „Kritisch“, die nicht direkt zur Prozessausführung gehören. Diese Einträge sind mit dem Prozessnamen „SystemLog“ gekennzeichnet.

Die Statusansicht in einem Editor (z. B. Prozesseditor) zeigt zusätzlich alle Meldungen, die sich auf den jeweiligen Prozess, die Prozessgruppe oder den Zeitplan beziehen – inklusive der Sub-Prozesse. Auch hier werden alle kritischen Systemmeldungen sowie Warnungen aus dem SystemLog angezeigt.

[![Status_fenster_deu.png](http://192.168.5.129/uploads/images/gallery/2025-07/scaled-1680-/udGstatus-fenster-deu.png)](http://192.168.5.129/uploads/images/gallery/2025-07/udGstatus-fenster-deu.png)

Das Statusfenster ist ein verschiebbares und in der Größe anpassbares Pop-up-Fenster.  
Per Doppelklick kann das Fenster auf Vollbild vergrößert oder auf die ursprüngliche Größe zurückgesetzt werden.

Der enthaltene Text kann über die Zwischenablage (Copy and Paste) kopiert werden.

Während das Fenster geöffnet ist, kann **EMMA Studio** nicht verwendet werden. Erst nach Schließen des Fensters über das rote X ist die Anwendung wieder bedienbar.

Weiterführende Informationen (z. B. PDF-Export etc.) sind im Abschnitt [Reports](http://192.168.5.129/books/emma-studio-27-benutzerhandbuch/page/reports "Abschnitt Reports") in diesem Benutzerhandbuch zu finden.

### Fehlerbehebung

Wenn Probleme auftreten oder nachverfolgt werden soll, was **EMMA Studio** ausgeführt hat, dient die Log-Historie als erster Anhaltspunkt.

Reicht die Anzeige in der Statusansicht nicht aus, empfiehlt es sich, die Logdatei über den Windows-Explorer in einem Texteditor zu öffnen. Dort sind oft weiterführende Details enthalten.

Bei Unsicherheiten zu einzelnen Meldungen empfehlen wir, Kontakt mit dem zuständigen Experten in Ihrem Unternehmen aufzunehmen oder eine Supportanfrage direkt bei WIANCO zu stellen – idealerweise mit der betreffenden Logdatei.

# Einstellungen



# Shortcuts

In **EMMA Studio** sind Shortcuts bereits voreingestellt, lassen sich aber nach den eigenen Bedürfnissen und Vorlieben anpassen. Dies ist unter ***Einstellungen → Shortcuts*** möglich.

Standardmäßig sind die Shortcuts wie folgt definiert:

<table border="1" id="bkmrk-aktion-tastenkombina" style="font-family: Jost, sans-serif; font-size: 14px; width: 100%; height: 1102.49px;"><colgroup><col style="width: 50%;"></col><col style="width: 50%;"></col></colgroup><thead><tr style="height: 29.7969px;"><td style="height: 29.7969px;">**Aktion**</td><td style="height: 29.7969px;">**Tastenkombination**</td></tr></thead><tbody><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Speichern</td><td style="height: 29.7969px;">{CONTROL} + {S}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Öffnen</td><td style="height: 29.7969px;">{CONTROL} + {O}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Hilfe</td><td style="height: 29.7969px;">{F1}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Starten</td><td style="height: 29.7969px;">{CONTROL} + {R}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Rückgängig machen</td><td style="height: 29.7969px;">{CONTROL} + {Z}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Wiederholen</td><td style="height: 29.7969px;">{CONTROL} + {Y}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Löschen</td><td style="height: 29.7969px;">{DELETE}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Ausführung pausieren</td><td style="height: 29.7969px;">{CONTROL} + {SHIFT} + {F1}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Prozess durchsuchen</td><td style="height: 29.7969px;">{CONTROL} + {F}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Find Next (Nächsten)</td><td style="height: 29.7969px;">{F3}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Find Previous </td><td style="height: 29.7969px;">{SHIFT} + {F3}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Schließen</td><td style="height: 29.7969px;">{CONTROL} + {F4}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Kopieren</td><td style="height: 29.7969px;">{CONTROL} + {C}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Einfügen</td><td style="height: 29.7969px;">{CONTROL} + {V}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Neu </td><td style="height: 29.7969px;">{CONTROL} + {N}</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Warteschlange löschen</td><td style="height: 29.7969px;">{CONTROL} + {DELETE}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Reload EMMA Configuration </td><td style="height: 29.7969px;">{CONTROL} + {R}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Modus wechseln</td><td style="height: 29.7969px;">{CONTROL} + {M}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Cursor zurücksetzen</td><td style="height: 29.7969px;">{ESCAPE}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Löschwerkzeug auswählen</td><td style="height: 29.7969px;">{D}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Bearbeitungswerkzeug auswählen</td><td style="height: 29.7969px;">{E}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Grünen Verbindungspfeil auswählen</td><td style="height: 29.7969px;">{T}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Roten Verbindungspfeil auswählen</td><td style="height: 29.7969px;">{F}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Breakpoint Tool</td><td style="height: 29.7969px;">{B}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Schritt deaktivieren auswählen</td><td style="height: 29.7969px;">{I}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Finden-Schritt Auswählen</td><td style="height: 29.7969px;">{MENU} + {F}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Lesen-Schritt auswählen </td><td style="height: 29.7969px;">{MENU} + {R}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Hören-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {G}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Finden-und-Klicken-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {A}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Klick-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {C}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Ziehen-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {D}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Scrollen-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {S}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Tippen-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {T}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Sprechen-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {K}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Export-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {E}

</td></tr><tr style="height: 29.7969px;"><td style="height: 29.7969px;">Import-Schritt auswählen</td><td style="height: 29.7969px;">{MENU} + {I}

</td></tr><tr><td>Befehl-Schritt auswählen</td><td>{MENU} + {M}

</td></tr><tr><td>Datei-Operation-Schritt auswählen</td><td>{MENU} + {O}

</td></tr><tr><td>E-Mail-Versand-Schritt auswählen</td><td>{MENU} + {J}

</td></tr><tr><td>Schleife-Schritt auswählen</td><td>{MENU} + {L}

</td></tr><tr><td>Verschachtelter-Prozess-Schritt auswählen</td><td>{MENU} + {N}

</td></tr><tr><td>Entscheidung-Schritt auswählen</td><td>{MENU} + {Y}

</td></tr><tr><td>Warten-Schritt auswählen</td><td>{MENU} + {W}

</td></tr><tr><td>Erfolg-Schritt auswählen</td><td>{MENU} + {X}

</td></tr><tr><td>Klassifizierungsschritt auswählen</td><td>{MENU} + {U}

</td></tr><tr><td>Formular lesen auswählen</td><td>{MENU} + {B}

</td></tr></tbody></table>