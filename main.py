#!/usr/bin/env python3
import subprocess

HEADER = ['NAME', 'STATE', 'READ', 'WRITE', 'CKSUM']


def print_table(rows, right_cols=()):
    rows = [[str(x) for x in r] for r in rows]
    width = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for row in rows:
        print(" ".join(
            (column.rjust(width[i]) if i in right_cols else column.ljust(width[i])) for i, column in enumerate(row)
        ))


def main():
    cmd = ['zpool', 'status']
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        print((p.stderr or 'zpool status failed').strip())
        return

    current_section = ''
    current_pool = ''
    pools = {}
    for line in p.stdout.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith('pool:'):
            current_section = 'pool'
            current_pool = stripped_line.removeprefix('pool:').strip()
            continue
        if stripped_line.startswith('state:'):
            current_section = 'state'
            current_state = stripped_line.removeprefix('state:').strip()
            if current_state.lower() != 'online':
                print(current_pool, current_state)
            continue
        if stripped_line.startswith('status:'):
            current_section = 'status'
            print(current_pool, stripped_line.removeprefix('status:').strip())
            continue
        if stripped_line.startswith('errors:'):
            current_section = 'errors'
            current_errors = stripped_line.removeprefix('errors:').strip()
            if current_errors.lower() != 'no known data errors':
                print(current_pool, current_errors)
            continue
        if stripped_line.startswith('config:'):
            current_section = 'config'
            continue
        if stripped_line.startswith('scan:'):
            current_section = 'scan'
            current_scan = stripped_line.removeprefix('scan:').strip()
            if not current_scan.lower().startswith('scrub repaired 0b'):
                print(current_pool, current_scan)
            continue
        if stripped_line.startswith('action:'):
            current_section = 'action'
            current_action = stripped_line.removeprefix('action:').strip()
            print(current_pool, current_action)
            continue
        if current_section in ('action', 'scan', 'status'):
            print(stripped_line)
            continue
        parts = line.split()
        if parts == HEADER:
            continue
        if current_pool not in pools:
            pools[current_pool] = {}
        level = len(line) - len(line.lstrip())
        if level not in pools[current_pool]:
            pools[current_pool][level] = []
        name = parts[0]
        if level >= 5 or (level >= 3 and current_pool == 'zpcachyos'):
            name = name[-8:]
        pools[current_pool][level].append({
            'name': name,
            'state': parts[1],
            'read': parts[2],
            'write': parts[3],
            'cksum': parts[4],
        })
    print_list = [HEADER]
    for pool, levels in pools.items():
        for level, entries in levels.items():
            for entry in entries:
                print_list.append(list(entry.values()))
    print_table(print_list, right_cols=(2, 3, 4))


if __name__ == "__main__":
    main()
