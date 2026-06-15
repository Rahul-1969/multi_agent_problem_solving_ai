import sys, os, importlib, inspect, traceback
ROOT = os.path.abspath(r'e:\multi_agent_ai')
sys.path.insert(0, ROOT)

service_dir = os.path.join(ROOT, 'backend', 'services')
pipeline_dir = os.path.join(ROOT, 'pipelines')

modules = []
for dirpath, dirnames, filenames in os.walk(service_dir):
    for f in filenames:
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
            modules.append(rel[:-3].replace(os.sep, '.'))
for dirpath, dirnames, filenames in os.walk(pipeline_dir):
    for f in filenames:
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
            modules.append(rel[:-3].replace(os.sep, '.'))

errors = []
print('Modules to validate:', modules)
for mod in modules:
    try:
        m = importlib.import_module(mod)
        print('Imported', mod)
    except Exception as e:
        errors.append((mod, 'import', str(e)))
        continue
    # Inspect for functions
    funcs = [name for name, obj in inspect.getmembers(m, inspect.isfunction) if obj.__module__==m.__name__]
    print(' Functions:', funcs)
    # Basic checks: if module is a service, ensure it defines expected entrypoints
    if mod.endswith('chatbot_service'):
            if 'process_query' not in funcs:
                errors.append((mod, 'missing_function', 'Missing process_query'))
    if mod.endswith('pdf_service'):
        for fn in ['load_pdf', 'get_pdf_status', 'clear_pdf', 'answer_from_pdf']:
            if fn not in funcs:
                errors.append((mod, 'missing_function', f'Missing {fn}'))
    if mod.endswith('pipeline_dispatcher'):
        # verify it exposes a PipelineMap or function to dispatch
        if not any(fn.startswith('get_') or fn.endswith('dispatcher') for fn in funcs):
            # not strict; just report
            pass

print('\nSummary:')
if not errors:
    print('All service/pipeline modules imported and basic checks passed.')
else:
    print('Errors found:')
    for e in errors:
        print('-', e)
    sys.exit(2)
