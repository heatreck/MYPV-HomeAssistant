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

1. Einmalig auf der lokalen Nutzeroberfläche des SolThors anmelden und ein Passwort vergeben (Standartpasswort ist der Device-Key)
2. Verschlüsselte Lufzeitdaten im Heimnetz deaktivieren.
3. SolThor im HomeAssitant inrichten

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
