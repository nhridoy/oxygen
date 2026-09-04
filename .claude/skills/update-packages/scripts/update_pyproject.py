import concurrent.futures
import json
import pathlib
import re
import sys
import urllib.request


def base_name(req):
    m = re.match(r"([A-Za-z0-9_.\-]+)(\[.*?\])?", req)
    return m.group(1) if m else req


def fetch(name):
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            j = json.load(r)
            return name, j["info"]["version"]
    except Exception:
        return name, None


def main():
    path = pathlib.Path("pyproject.toml")
    text = path.read_text()
    import tomllib

    with open("pyproject.toml", "rb") as f:
        t = tomllib.load(f)
    deps = t["project"]["dependencies"]
    dev_deps = t.get("dependency-groups", {}).get("dev", [])
    all_deps = deps + dev_deps
    names = [base_name(d) for d in all_deps]
    print(f"Fetching latest for {len(names)} packages...")
    versions = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch, n): n for n in names}
        for fut in concurrent.futures.as_completed(futs):
            n, v = fut.result()
            if v:
                versions[n.lower()] = (n, v)
                print(f"  {n}: {v}")
            else:
                print(f"  {n}: failed", file=sys.stderr)

    def repl(m):
        pkg = m.group(1)
        extra = m.group(2) or ""
        key = pkg.lower()
        if key in versions:
            orig, ver = versions[key]
            return f'"{pkg}{extra}>={ver}"'
        return m.group(0)

    new_text = re.sub(r'"([A-Za-z0-9_.\-]+)(\[[^\]]+\])?>=[^"]+"', repl, text)
    if new_text != text:
        path.write_text(new_text)
        print("Updated pyproject.toml")
    else:
        print("No changes to pyproject.toml")
    print("Running uv lock --upgrade...")
    import subprocess

    r = subprocess.run(["uv", "lock", "--upgrade"], capture_output=False)
    if r.returncode != 0:
        print("uv lock failed", file=sys.stderr)
        sys.exit(r.returncode)
    print("Running uv sync --all-groups...")
    r = subprocess.run(["uv", "sync", "--all-groups"], capture_output=False)
    if r.returncode != 0:
        print("uv sync failed", file=sys.stderr)
        sys.exit(r.returncode)
    print("Done. Check with: uv tree --outdated")


if __name__ == "__main__":
    main()
