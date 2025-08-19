# Imports communs pour le module library_tab
import sys
import os

# Ajouter le répertoire parent au path pour permettre les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer tout depuis le __init__.py principal
from __init__ import *