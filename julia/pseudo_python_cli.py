"""
Pseudo Python command line interface.

It tries to mimic a subset of Python CLI:
https://docs.python.org/3/using/cmdline.html
"""

import argparse
import code
import runpy
import sys
import traceback


def python(module, command, script, args, interactive):
    if command:
        sys.argv[0] = "-c"
    elif script:
        sys.argv[0] = script
    sys.argv[1:] = args

    banner = ""
    try:
        if command:
            scope = {}
            exec(command, scope)
        elif module:
            scope = runpy.run_module(
                module,
                run_name="__main__",
                alter_sys=True)
        elif script == "-":
            source = sys.stdin.read()
            exec(compile(source, "<stdin>", "exec"), scope)
        elif script:
            scope = runpy.run_path(
                script,
                run_name="__main__")
        else:
            interactive = True
            scope = None
            banner = None  # show banner
    except Exception:
        if not interactive:
            raise
        traceback.print_exc()

    if interactive:
        code.interact(banner=banner, local=scope)


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def make_parser(description=__doc__):
    parser = argparse.ArgumentParser(
        prog=None if sys.argv[0] else "python",
        usage="%(prog)s [option] ... [-c cmd | -m mod | script | -] [args]",
        formatter_class=CustomFormatter,
        description=description)

    parser.add_argument(
        "-i", dest="interactive", action="store_true",
        help="""
        inspect interactively after running script.
        """)
    parser.add_argument(
        "--version", "-V", action="version",
        version="Python {0}.{1}.{2}".format(*sys.version_info),
        help="""
        print the Python version number and exit.
        -VV is not supported.
        """)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c", dest="command",
        help="""
        Execute the Python code in COMMAND.
        """)
    group.add_argument(
        "-m", dest="module",
        help="""
        Search sys.path for the named MODULE and execute its contents
        as the __main__ module.
        """)

    parser.add_argument(
        "script", nargs="?",
        help="path to file")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER,
        help="arguments passed to program in sys.argv[1:]")

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = make_parser()
    try:
        ns = parser.parse_args(args)
        python(**vars(ns))
    except SystemExit as err:
        return err.code
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())