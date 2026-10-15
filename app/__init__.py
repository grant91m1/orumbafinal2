import sys
import os
import importlib.util

# Add top-level dir (parent of app/) to Python path
top_level_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if top_level_dir not in sys.path:
    sys.path.insert(0, top_level_dir)

# Load the top-level app.py module directly to avoid package/module name collision
app_path = os.path.join(top_level_dir, 'app.py')
spec = importlib.util.spec_from_file_location('app_module', app_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules['app_module'] = app_module
spec.loader.exec_module(app_module)
app = app_module.app

__all__ = ['app']

