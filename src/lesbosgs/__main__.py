import argparse, pathlib
from . import clicmd as cmds

def main():
    parser = argparse.ArgumentParser(
        prog='lesbos',
        description='goboscript package manager',
    )
    parser.add_argument("subcommand")
    parser.add_argument("project_name", type=str, nargs="?", help="The project name that subcommand will be acting on (optional)")
    parser.add_argument("-s", "--source", type=str, help="The source url from which to install the package.")
    parser.add_argument("-n", "--name", type=str, help="The package name, to be installed from the default package source.")
    parser.add_argument("-l", "--lib", action="store_true", help="Create library")
    parser.add_argument("--force-remake", action="store_true", help="Forcefully remake any files/folder if they already exist")
    parser.add_argument("-v", "--version", type=str, help="The version of the library specified")
    parser.add_argument("--no-lock", action="store_true", help="Disables reinstalling packages")
    args = parser.parse_args()
    if args.source and args.name:
        parser.error("Cannot have both --source and --name")
    if args.subcommand == "new":
        if args.project_name == None:
            parser.error("Must have project_name if subcommad is `new`")
        cmds.new(pathlib.Path(args.project_name), args.lib, args.force_remake)
    elif args.subcommand == "add":
        if args.version == None:
            parser.error("Must have --version if subcommand is `add`")
        if args.source:
            issource = True
            dep = args.source
        elif args.name:
            issource = False
            dep = args.name
        else:
            parser.error("Must have either `--source` or `--name` if subcommand is `add`")
        cmds.add_dep(dep, args.version, issource)
    elif args.subcommand == "build":
        cmds.build(nolock=args.no_lock)
    elif args.subcommand == "lock":
        cmds.lock()
    elif args.subcommand == "pack":
        cmds.pack()
    # https://gitlab.com/goboscript-lesbos/database/-/raw/main/{}

if __name__ == "__main__":
    main()
