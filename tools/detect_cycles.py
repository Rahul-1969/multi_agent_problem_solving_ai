"""
Lightweight import graph builder and cycle detector for project modules.
Writes detected cycles to stdout.
"""
import ast
import os
from collections import defaultdict, deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXCLUDE_DIRS = {'.venv', 'node_modules', 'dist', '__pycache__'}
TOP_PACKAGES = set()

# Collect python files and module names
py_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip excluded dirs
    parts = set(dirpath.split(os.sep))
    if parts & EXCLUDE_DIRS:
        continue
    for f in filenames:
        if not f.endswith('.py'):
            continue
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, ROOT)
        mod = rel[:-3].replace(os.sep, '.')
        if mod.endswith('.__init__'):
            mod = mod[:-9]
        py_files.append((full, mod))
        top = mod.split('.')[0]
        TOP_PACKAGES.add(top)

# Parse imports
graph = defaultdict(set)
modules_set = {mod for _, mod in py_files}

for full, mod in py_files:
    try:
        with open(full, 'r', encoding='utf-8') as fh:
            tree = ast.parse(fh.read(), filename=full)
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                # consider top-level package if in repo
                if any(name == m or name.startswith(m + '.') for m in modules_set) or name.split('.')[0] in TOP_PACKAGES:
                    graph[mod].add(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            level = node.level
            if level and (module is None or module.startswith('.')):
                # resolve relative import to absolute module
                base_parts = mod.split('.')[:-level]
                if module:
                    rel_parts = module.split('.')
                    base_parts += rel_parts
                target = '.'.join(base_parts) if base_parts else module
            else:
                target = module
            if target:
                # only include if target belongs to project top packages
                if target in modules_set or target.split('.')[0] in TOP_PACKAGES:
                    graph[mod].add(target)

# Normalize edges: keep only edges that map to modules in project (or top packages)
norm_graph = defaultdict(set)
for src, targets in graph.items():
    for t in targets:
        # try to map t to a known module by prefix
        if t in modules_set:
            norm_graph[src].add(t)
        else:
            # if t is a package prefix in modules_set, add all matching modules
            for m in modules_set:
                if m == t or m.startswith(t + '.'):
                    norm_graph[src].add(m)

# Detect cycles via DFS
visited = {}
stack = []
cycles = set()

def dfs(node, path):
    visited[node] = 1
    path.append(node)
    for nbr in norm_graph.get(node, []):
        if nbr not in visited:
            dfs(nbr, path)
        elif visited.get(nbr) == 1:
            # found a cycle
            try:
                idx = path.index(nbr)
                cycle = tuple(path[idx:])
                cycles.add(cycle)
            except ValueError:
                pass
    path.pop()
    visited[node] = 2

for m in sorted(modules_set):
    if m not in visited:
        dfs(m, [])

if not cycles:
    print('No import cycles detected')
else:
    print('Detected cycles:')
    for c in sorted(cycles):
        print(' -> '.join(c))

# Print brief graph summary
print('\nGraph summary:')
for src in sorted(norm_graph):
    print(f"{src} -> {', '.join(sorted(norm_graph[src])[:5])}{'...' if len(norm_graph[src])>5 else ''}")
