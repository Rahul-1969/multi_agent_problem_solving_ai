import sys, os, traceback, importlib, inspect
ROOT = os.path.abspath(r'e:\multi_agent_ai')
sys.path.insert(0, ROOT)
from pydantic import BaseModel

models_dir = os.path.join(ROOT, 'backend', 'models')
modules = []
for dirpath, dirnames, filenames in os.walk(models_dir):
    for f in filenames:
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
            mod = rel[:-3].replace(os.sep, '.')
            modules.append(mod)

errors = []
print('Checking modules:', modules)
for mod in modules:
    try:
        m = importlib.import_module(mod)
    except Exception as e:
        tb = traceback.format_exc()
        errors.append((mod, 'import', str(e), tb))
        continue
    for name, obj in inspect.getmembers(m, inspect.isclass):
        if issubclass(obj, BaseModel) and obj is not BaseModel:
            fullname = f"{mod}.{name}"
            try:
                # generate schema
                schema = obj.model_json_schema()
                print(f"OK: {fullname}")
            except Exception as e:
                tb = traceback.format_exc()
                errors.append((fullname, 'schema', str(e), tb))

print('\nSummary:')
if not errors:
    print('All Pydantic models validated successfully.')
else:
    print(f'{len(errors)} errors:')
    for item in errors:
        print('-', item[0], item[1], item[2])
        # print trace for first few
        print(item[3])
