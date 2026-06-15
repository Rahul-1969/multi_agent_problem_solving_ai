import sys, os, importlib, traceback
root = os.path.abspath(r'e:\multi_agent_ai')
sys.path.insert(0, root)
errors = []
modules = []
for dirpath, dirnames, filenames in os.walk(root):
    # skip virtualenv, node_modules, dist, hidden files, and __pycache__
    if any(p in dirpath for p in ['.venv', 'node_modules', 'dist', '__pycache__']):
        continue
    for f in filenames:
        if not f.endswith('.py') or f.startswith('.'):
            continue
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, root)
        mod = rel[:-3].replace(os.sep, '.')
        if mod.endswith('.__init__'):
            mod = mod[:-9]
        if mod.startswith('.'):
            continue
        modules.append(mod)
modules = sorted(set(modules))
print('Modules to try:', len(modules))
for m in modules:
    try:
        importlib.import_module(m)
    except Exception as e:
        tb = traceback.format_exc()
        errors.append((m, type(e).__name__, str(e).split('\n')[-1], tb))
print('\nErrors:')
for m, etype, msg, tb in errors:
    print(f"- {m}: {etype}: {msg}")
print('\nSummary: total modules', len(modules), 'errors', len(errors))
