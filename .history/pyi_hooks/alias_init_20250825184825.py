# Robustly alias 'music_player.__init__' as top-level '__init__' for frozen apps
import importlib, sys, os, importlib.util

def ensure_init_alias():
    if '__init__' in sys.modules:
        return
    # Try regular package import first
    try:
        sys.modules['__init__'] = importlib.import_module('music_player.__init__')
        return
    except Exception:
        pass
    # Fallback: locate __init__.py on disk in common frozen locations
    candidates = []
    base = getattr(sys, '_MEIPASS', None)
    if base:
        candidates.append(os.path.join(base, 'music_player', '__init__.py'))
    # Executable directory
    exe_dir = os.path.dirname(sys.argv[0]) if sys.argv else None
    if exe_dir:
        candidates.append(os.path.join(exe_dir, 'music_player', '__init__.py'))
    # Current working dir
    candidates.append(os.path.join(os.getcwd(), 'music_player', '__init__.py'))

    for path in candidates:
        if path and os.path.exists(path):
            try:
                spec = importlib.util.spec_from_file_location('__init__', path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sys.modules['__init__'] = mod
                return
            except Exception:
                continue

ensure_init_alias()