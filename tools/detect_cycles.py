"""
Lightweight import graph builder and cycle detector for project modules.
Writes detected cycles to stdout.
"""
import ast
import os
from collections import defaultdict, deque


def _collect_modules(root: str):
    """Walk project tree and collect Python modules."""
    exclude_dirs = {'.venv', 'node_modules', 'dist', '__pycache__'}
    py_files = []
    top_packages = set()

    for dirpath, dirnames, filenames in os.walk(root):
        parts = set(dirpath.split(os.sep))
        if parts & exclude_dirs:
            continue
        for f in filenames:
            if not f.endswith('.py'):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root)
            mod = rel[:-3].replace(os.sep, '.')
            if mod.endswith('.__init__'):
                mod = mod[:-9]
            py_files.append((full, mod))
            top = mod.split('.')[0]
            top_packages.add(top)

    return py_files, top_packages


def _build_import_graph(py_files, top_packages):
    """Parse imports from collected modules and build dependency graph."""
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
                    if any(name == m or name.startswith(m + '.') for m in modules_set) or name.split('.')[0] in top_packages:
                        graph[mod].add(name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                level = node.level
                if level and (module is None or module.startswith('.')):
                    base_parts = mod.split('.')[:-level]
                    if module:
                        rel_parts = module.split('.')
                        base_parts += rel_parts
                    target = '.'.join(base_parts) if base_parts else module
                else:
                    target = module
                if target:
                    if target in modules_set or target.split('.')[0] in top_packages:
                        graph[mod].add(target)

    # Normalize edges
    norm_graph = defaultdict(set)
    for src, targets in graph.items():
        for t in targets:
            if t in modules_set:
                norm_graph[src].add(t)
            else:
                for m in modules_set:
                    if m == t or m.startswith(t + '.'):
                        norm_graph[src].add(m)

    return norm_graph, modules_set


def _find_cycles(norm_graph, modules_set):
    """Detect import cycles via DFS."""
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

    return cycles


def main():
    """Entry point: scan project, build graph, detect cycles, print summary."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    py_files, top_packages = _collect_modules(root)
    norm_graph, modules_set = _build_import_graph(py_files, top_packages)
    cycles = _find_cycles(norm_graph, modules_set)

    if not cycles:
        print('No import cycles detected')
    else:
        print('Detected cycles:')
        for c in sorted(cycles):
            print(' -> '.join(c))

    print('\nGraph summary:')
    for src in sorted(norm_graph):
        print(f"{src} -> {', '.join(sorted(norm_graph[src])[:5])}{'...' if len(norm_graph[src]) > 5 else ''}")


if __name__ == '__main__':
    main()
