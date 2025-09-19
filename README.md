# lesbos
goboscript package manager

## Installation
Clone the repo:
```bash
git clone https://github.com/Belu-cat/lesbos
cd lesbos
```
Then, create and activate virtual env:
```bash
python -m venv .env
. .env/bin/activate
```
Now, install requirements:
```bash
pip install -r requirements.txt
```
Finally, build and install:
```bash
pip install .
```

## Usage
The help menu will show you most information, though some of it is misleading.

### new
Creates a new project.

Usage:
```bash
python -m lesbosgs new [name]
```

Can take:
- ``--force-remake``
- ``--lib`` (``-l``)

### add
Adds a package to the dependencies of the project in the current working directory.

Usage:
```bash
python -m lesbosgs add [--source (-s)/--name (-n)] [package url/package name] [-v/--version] [version]
```

### lock
Installs all dependencies.

Usage:
```bash
python -m lesbosgs lock
```

### build
Builds the project in the current working directory.

Usage:
```bash
python -m lesbosgs build
```

Can take:
- ``--no-lock``

### pack
Packs the current project into the library format, if it is a library, into lesbos/packed.

Usage:
```bash
python -m lesbosgs pack
```
