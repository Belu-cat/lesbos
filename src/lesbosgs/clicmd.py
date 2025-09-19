import os, pathlib, tomllib
import toml
import subprocess
import zipfile
from shutil import rmtree

from . import get_deps

def _create_file(file: str, contents: str, forceremake: bool):
    if forceremake:
        m = "w"
    else:
        m = "x"
    with open(file, m) as f:
        f.write(contents)

def _create_folder(name: pathlib.Path, forceremake: bool):
    try:
        os.mkdir(name)
    except FileExistsError:
        if not forceremake:
            raise Exception(f"Error: folder `{name}` already exists\nHelp: Try passing with --force-remake")

def new(name: pathlib.Path, islib: bool, forceremake: bool):
    """
    Creates a new project at the directory in "name"
    Note: The directory in "name" must NOT end in a /, and the directory must NOT already exist
    """
    _create_folder(name, forceremake)

    _create_folder(name / "lesbos", forceremake)

    _create_file(name / "README.md", f"# {name}\n", forceremake)
    print("Created README")

    lesbos_toml = {"options": {},
        "deps": [{}]
    }
    _create_file(name / "lesbos.toml", toml.dumps(lesbos_toml), forceremake)
    print("Created lesbos.toml")

    if islib:
        package_toml = {"name": str(name),
                        "version": "0.1.0",
                        "features": [{"name": "core", "files": ["main.gs"]},]
        }
        _create_file(name / "package.toml", toml.dumps(package_toml), forceremake)
        print("Created package.toml")

        _create_file(name / "main.gs","func hello() {\n\treturn \"Hello, world!\";\n}", forceremake)
    else:
        _create_folder(name / "assets", forceremake)
        _create_file(name / "assets/blank.svg", """<svg
    version="1.1"
    width="0"
    height="0"
    viewBox="0 0 0 0"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
></svg>""", forceremake)
        print("Added assets")

        _create_file(name / "main.gs", """costumes "assets/blank.svg";

onflag {
    say "Hello, world!";
    }
""", forceremake)
        print("Created main.gs")

        _create_file(name / "stage.gs", "costumes \"assets/blank.svg\";\n", forceremake)
        print("Created stage.gs")

        _create_file(name / "goboscript.toml", "", forceremake)
        print("Created goboscript.toml")

def _check_if_project(direc: pathlib.Path):
    return os.path.isfile(direc / "lesbos.toml")

def _check_if_library(direc: pathlib.Path):
    return os.path.isfile(direc / "package.toml") and _check_if_project(direc)

def add_dep(dep: str, ver: str, issource: bool):
    if not _check_if_project(pathlib.Path("./")):
        raise Exception("Could not find either `lesbos.toml` or `goboscript.toml` in folder")
    with open("lesbos.toml", "rb") as f:
        lesbos_config = tomllib.load(f)
    packdata = {}
    if issource:
        packdata["source"] = dep
    else:
        packdata["name"] = dep
    packdata["version"] = ver
    lesbos_config["deps"].append(packdata)
    with open("lesbos.toml", "w") as f:
        toml.dump(lesbos_config, f)

def build(nolock: bool):
    if not _check_if_project(pathlib.Path("./")):
        raise Exception("Could not find either `lesbos.toml` or `goboscript.toml` in folder")
    if not nolock:
        lock()
    subprocess.run(["goboscript", "build"], check=True)

def lock():
    if not _check_if_project(pathlib.Path("./")):
        raise Exception("Could not find either `lesbos.toml` or `goboscript.toml` in folder")
    if os.path.exists("lesbos/deps/"):
        rmtree("lesbos/deps/")
    with open("lesbos.toml", "rb") as f:
        project_meta = tomllib.load(f)
    get_deps.install_packages(project_meta["deps"], sourcefmt="https://gitlab.com/goboscript-lesbos/database/-/raw/main/{}", direc=pathlib.Path("./lesbos/deps/"))

def _starts_with_one_of(item: str, lst: list):
    for x in lst:
        if item.startswith(x):
            return True
    return False

def pack():
    if not _check_if_library(pathlib.Path("./")):
        raise Exception("Is not library!")
    packedpath = pathlib.Path("./") / "lesbos" / "packed"
    if os.path.exists(packedpath):
        rmtree(packedpath)
    os.mkdir(packedpath)
    package_zip = zipfile.ZipFile(packedpath / "package.zip", 'w', zipfile.ZIP_LZMA)
    ALLOWED_NAMES = []
    ALLOWED_FULL_NAMES = ["./lesbos.toml", "./package.toml"]
    ALLOWED_PREFIXES = ["./README", "./DOCS/", "./LICENSE"]
    for root, _, files in os.walk(pathlib.Path("./")):
        for file in files:
            full_name = os.path.join(root, file)
            if file.endswith(".gs") or full_name in ALLOWED_FULL_NAMES or file in ALLOWED_NAMES or _starts_with_one_of(full_name, ALLOWED_PREFIXES):
                package_zip.write(full_name)
    with open("lesbos.toml") as f:
        lesbos_toml = f.read()
    with open(packedpath / "lesbos.toml", "x") as f:
        f.write(lesbos_toml)
    with open("package.toml") as f:
        package_toml = f.read()
    with open(packedpath / "package.toml", "x") as f:
        f.write(package_toml)