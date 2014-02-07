#!/usr/bin/python
import code
import argparse

if __name__ == "__main__":
    # Parsing command line arguments and automating the help message
    # There are two command line argument types: -h show help message;
    # list of relative file paths (wildcards accepted) with the Netflix data.
    # ArgumentParser takes care of incorrectly formatted arguments, and
    # help message.
    parser = argparse.ArgumentParser(description="Parse netflix data files")
    parser.add_argument("files",
                        metavar="mv_*.txt",
                        help="path of a netflix dataset file",
                        nargs="+",
                        type=str
    )
    # fileList is a list of all the file paths passed to the file.
    fileList = parser.parse_args().files
    # Drop user into a shell, with the current environment
    code.interact(local=locals())
