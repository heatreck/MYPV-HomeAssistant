# my-PV for Home Assistant

Eine lokale Home-Assistant-Integration für my-PV-Geräte. Sie liest Laufzeitdaten
über HTTP und nutzt die geschützte Geräte-Schnittstelle über HTTPS für Einstellungen.
Die selbstsignierten Zertifikate der my-PV-Geräte werden dabei bewusst nur für die
lokale Geräteverbindung akzeptiert.

## Unterstützte Geräte und Funktionen

- my-PV-Geräte mit `mypv_dev.jsn` und `data.jsn`
- Wi-Fi Meter (`monitorjson`)
- Auswahl der angelegten Sensoren im Einrichtungsdialog
- Geschützte Setup-Werte mit lokalem Gerätepasswort
- Gerät aktivieren/deaktivieren, Warmwasser-Sollwert und Boost – wenn das jeweilige
  Gerät die entsprechende Funktion bereitstellt

## Installation

### HACS

1. Dieses Repository in HACS als **benutzerdefiniertes Repository** vom Typ
   **Integration** hinzufügen.
2. Die Integration installieren und Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **my-PV** suchen.

### Manuell

Den Ordner `custom_components/mypv` nach
`<HA-Konfigurationsordner>/custom_components/mypv` kopieren und Home Assistant
neu starten.

## Einrichtung

Die IP-Adresse des Geräts eingeben oder den lokalen Scan benutzen. Für neuere
Firmware kann ein Passwort erforderlich sein, um Einstellungen abzurufen oder zu
ändern. Das Passwort wird ausschließlich in der Home-Assistant-Konfiguration
auf der jeweiligen Instanz gespeichert.

## Sicherheit und Zertifikate

my-PV-Geräte verwenden für `https://<geraete-ip>/` typischerweise ein
selbstsigniertes Zertifikat. Die Integration deaktiviert deshalb ausschließlich
bei dieser lokalen HTTPS-Verbindung die Zertifikatsprüfung. Der Zugriff auf die
Geräte-API erfolgt nie über einen Cloud-Dienst.

## Vor dem ersten öffentlichen Release

In `custom_components/mypv/manifest.json` die beiden `CHANGE-ME`-URLs durch die
eigene GitHub-Repository-URL ersetzen und den GitHub-Benutzernamen als
`codeowners` eintragen. Anschließend einen GitHub-Release, z. B. `v1.3.0`,
veröffentlichen.

## Hinweise

Bitte keine Logs, Datenbanken, `.storage`, `secrets.yaml`, Testdaten oder lokale
IP-Adressen in dieses Repository übernehmen. Fehlerberichte sollten Home-Assistant-
und Geräte-Firmware-Version sowie anonymisierte Debug-Logs enthalten.
