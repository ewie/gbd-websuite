Server Konfiguration
====================

Die GBD WebSuite betreibt intern mehrere Servermodule:

- das ``web``-Modul, das eingehende Anfragen entgegennimmt und versendet
- das ``mapproxy`` Modul, das den gebündelten MapProxy ausführt und sich um externe Quellen, Caching und Reprojektionen kümmert
- das ``qgis`` Modul, das den gebündelten QGIS Server betreibt und QGIS Projekte und Layer rendert
- das ``spool`` Modul, das den Druck und andere Hintergrundaufgaben übernimmt.

Jedes Modul kann deaktiviert werden, wenn es nicht benötigt wird (z. B. wenn Sie keine QGIS-Projekte verwenden, brauchen Sie den QGIS-Server nicht auszuführen). Sie können auch die Anzahl der Arbeiter (ungefähr, CPU-Kerne) und Threads konfigurieren, die jedes Modul verwenden darf. Standardmäßig sind die Werte ``4`` und ``0``, die optimalen Werte hängen von der Konfiguration Ihres Zielsystems ab.

Für Hochlast-Workflows ist es auch möglich, verschiedene Module auf verschiedenen physikalischen Maschinen zu betreiben. Beispielsweise können Sie eine GWS-Installation einrichten, die nur das Mapproxy-Modul, eine weitere für den QGIS-Server und eine weitere für das Frontend-Web-Modul ausführt. In diesem Fall können Sie für Mapproxy und QGIS in der Web-Konfiguration ``host`` and ``port`` angeben, so dass diese über das Netzwerk abgefragt werden können.

Aufbereitungsserver
-------------------

Das Spoolmodul enthält einen *Monitor*, der das Dateisystem überwacht, die Änderungen in Ihren Projekten und Konfigurationen überprüft und ggf. einen Hot-Reload des Servers durchführt. Sie können Intervalle für diese Prüfungen konfigurieren, es wird empfohlen, das Monitorintervall auf mindestens 30 Sekunden einzustellen, da Dateisystemprüfungen ressourcenintensiv sind.