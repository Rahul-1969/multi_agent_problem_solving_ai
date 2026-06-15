import os, sys, traceback
print('cwd=', os.getcwd())
print('sys.path[0]=', sys.path[0])
try:
    import backend.main
    print('backend.main imported OK')
except Exception as e:
    traceback.print_exc()
    print('ERROR:', e)
