import subprocess


def run_cmd(cmd) -> str | None:
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        print((p.stderr or 'command failed').strip())
        return None
    return p.stdout


def check_snapshot(snapshot):
    stdout = run_cmd(['zfs', 'destroy', '-nrvp', snapshot])
    if not stdout:
        return
    for line in stdout.splitlines():
        if line.startswith('reclaim'):
            free_size = int(line.removeprefix('reclaim').strip())
            free_size /= 1024 * 1024 * 1024
            free_size = round(free_size, 2)
            print(snapshot, free_size, 'G')


def main():
    stdout = run_cmd(['zfs', 'list', '-H', '-t', 'snapshot', '-r', '-o', 'name'])
    if not stdout:
        return
    for line in stdout.splitlines():
        if '/' in line:
            continue
        check_snapshot(line.strip())


if __name__ == '__main__':
    main()
