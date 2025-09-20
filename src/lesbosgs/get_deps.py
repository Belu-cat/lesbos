import requests
import urllib.parse
import tomllib
import zipfile
import io
import pathlib
import os
from sys import stderr

class InvalidDependency(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def join_url(*args):
    out = ""
    for x in args:
        out = urllib.parse.urljoin(out.rstrip("/")+"/", x)
    return out

def resolve_dep(dep: dict [str, str], fmtstr: str) -> str:
    if dep.get("source"):
        return join_url(dep["source"], dep["version"])
    elif dep.get("name"):
        return fmtstr.format(dep["name"]+"/"+dep["version"])
    else:
        raise InvalidDependency(f"Dependency does not have enough parameters")

def get_from_url(base: str, file: str):
    r = requests.get(join_url(base, file))
    r.raise_for_status()
    return r

def get_package(dep: dict [str, str], fmtstr: str):
    dep = resolve_dep(dep, fmtstr)
    package_meta = tomllib.loads(get_from_url(dep, "package.toml").text)
    project_meta = tomllib.loads(get_from_url(dep, "lesbos.toml").text)
    _package_zip = get_from_url(dep, "package.zip").content
    _package_zip = io.BytesIO(_package_zip)
    package_zip = zipfile.ZipFile(_package_zip, 'r')
    return package_meta, project_meta, package_zip

def get_feature(name: str, features: list):
    for x in features:
        if x["name"] == name:
            return x["files"]
    raise Exception(f"Could not find feature: `{name}`")

def install_package(dep: dict [str, str], sourcefmt: str, direc: pathlib.Path):
    package_meta, project_meta, package_zip = get_package(dep, sourcefmt)
    print(f"Getting package: {package_meta["name"]} v{package_meta["version"]}")
    try:
        included_files = get_feature("core", package_meta["features"])
    except Exception as e:
        print(e, file=stderr)
        included_files = []
    if dep.get("features"):
        for feat in dep["features"]:
            included_files += get_feature(feat, package_meta["features"])
    packdir = direc / package_meta["name"] / package_meta["version"]
    included_files = list(set(included_files))
    os.makedirs(packdir, exist_ok=True)
    for x in included_files:
        if os.path.exists(packdir / x):
            continue
        with open(packdir / x, 'wb') as f:
            os.makedirs(os.path.dirname(packdir / x), exist_ok=True)
            f.write(package_zip.read(x))
    if project_meta["deps"]:
        print("Recursively getting inferred dependencies...")
        install_packages(project_meta["deps"], sourcefmt, direc)

def install_packages(deps: list, sourcefmt: str, direc: pathlib.Path):
    for dep in deps:
        try:
            install_package(dep, sourcefmt, direc)
        except InvalidDependency as e:
            print(f"InvalidDependency: {e}", file=stderr)