import sys
import types
from pathlib import Path

# Ensure /var/task is registered as 'backend' in Lambda environment
_backend_dir = Path(__file__).resolve().parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

if "backend" not in sys.modules:
    _backend_pkg = types.ModuleType("backend")
    _backend_pkg.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = _backend_pkg
