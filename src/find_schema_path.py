import os
import collada

# Finde den Pfad zur schema-1.4.1.xml Datei
schema_path = os.path.join(os.path.dirname(collada.__file__), 'resources', 'schema-1.4.1.xml')
print("Pfad zur schema-1.4.1.xml Datei:", schema_path)
