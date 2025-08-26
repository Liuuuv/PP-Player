# Alias 'music_player.__init__' en module top-level '__init__'
import importlib, sys
try:
    sys.modules['__init__'] = importlib.import_module('music_player.__init__')
except Exception:
    pass