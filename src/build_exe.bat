@echo off
REM Batch-Datei zum Erstellen einer ausführbaren Datei aus mixamo2sl.py

REM Name des Python-Skripts
set SCRIPT_NAME=mixamo2sl.py

REM Name der ausführbaren Datei
set EXE_NAME=mixamo2sl.exe

REM Pfad zur schema-1.4.1.xml Datei im Programmverzeichnis
set SCHEMA_PATH=schema-1.4.1.xml

REM Pfad zur xsd.xml Datei im Programmverzeichnis
set XSD_PATH=xsd.xml

REM Erstellen der ausführbaren Datei mit pyinstaller
pyinstaller --onefile --add-data "inputbones.ini;." --add-data "outputbones.ini;." --add-data "%SCHEMA_PATH%;collada/resources" --add-data "%XSD_PATH%;collada/resources" %SCRIPT_NAME%

REM Verschieben der erstellten ausführbaren Datei ins aktuelle Verzeichnis
move dist\%EXE_NAME% .

REM Bereinigen der durch PyInstaller erstellten Verzeichnisse und Dateien
rmdir /s /q build
rmdir /s /q dist
del /q %SCRIPT_NAME%.spec

echo Fertig! Die Datei %EXE_NAME% wurde erstellt.
pause
