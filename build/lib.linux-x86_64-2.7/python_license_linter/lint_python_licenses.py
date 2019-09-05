# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import pkg_resources
import re
import requests
import glob
from math import ceil


def get_license_from_info(package):
    pkginfo = package.get_metadata_lines(package.PKG_INFO)
    for line in pkginfo:
        (k, v) = line.split(": ", 1)
        if k == "License":
            return v
    return None


def get_license_from_pypi(package_name):
    try:
        package_info = requests.get(
            "https://pypi.org/pypi/{}/json".format(package_name)
        )
        return package_info.json()["info"]["license"]
    except Exception:
        print(
            "\033[0;33;49m WARNING: Failed to get license info from pypi for package {}".format(
                package_name
            )
        )
        return None


def get_license(package_name):
    try:
        pkg = pkg_resources.require(package_name)[0]
        return get_license_from_info(pkg)
    except Exception:
        return None


def get_valid_requirements(req_path):
    """
    Parses a requirements.txt file and removes all comments
    leaving only the actual requirements
    """
    return [r for r in open(req_path, "r").readlines() if r[0] != "#"]


def get_package_name(x):
    """
    Strips version number and other info leaving only
    the package name to be imported
    """
    return re.search(r"^(\w|-)*", x).group()


def pretty_print_results(pairs):
    style = "\033[0;33;49m "
    tab_size = 4
    max_p0 = max([len(x[0]) for x in pairs])
    p1_x = (ceil(max_p0 / tab_size) + 1) * tab_size

    for pair in pairs:
        print(
            "{}{}{}{}".format(style, pair[0], " " * int(p1_x - len(pair[0])), pair[1])
        )


def main(
    filepath="./**/requirements.txt",
    use_pypi=False,
    grace=0,
    blacklist=["GPL", "AGPL", "LGPL"],
    whitelist=[],
):
    req_file_paths = glob.iglob(filepath)
    requirements = list(
        set(reduce(lambda x, y: x + get_valid_requirements(y), req_file_paths, []))
    )
    packages = [get_package_name(req) for req in requirements]
    licenses = [get_license(package) for package in packages]

    results = zip(packages, licenses)
    package_license_pairs = [r for r in results if r[1] is not None]
    errors = [r for r in results if r[1] is None]

    pypi_fails = []
    if use_pypi:
        pypi_licenses = [(p[0], get_license_from_pypi(p[0])) for p in errors]
        pypi_fails = [p for p in pypi_licenses if p[1] is None]
        package_license_pairs += [p for p in pypi_licenses if p[1] is not None]

    blacklisted_packages = [
        r
        for r in package_license_pairs
        if any([x.lower() in r[1].lower() for x in blacklist])
    ]
    blacklisted_packages = [p for p in blacklisted_packages if p[0] not in whitelist]

    if len(blacklisted_packages) > 0:
        print("\033[1;33;49m WARNING: Packages with blacklisted licenses found")
        pretty_print_results(blacklisted_packages)
    error_count = len(blacklisted_packages) + len(pypi_fails)
    if error_count > grace:
        print(
            "\033[1;31;49m ERROR: Grace ({}) exceeded [ERRORS: {}]".format(
                grace, error_count
            )
        )
        print(
            "\033[0;31;49m ERROR: Found {} blacklisted packages".format(
                len(blacklisted_packages)
            )
        )
        if len(pypi_fails) > 0:
            print(
                "\033[0;31;49m ERROR: Failed to fetch {} package infos from pypi".format(
                    len(pypi_fails)
                )
            )
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath",
        help="matches the given pathname pattern; use to point to requirements.txt files",
        type=str,
    )
    parser.add_argument(
        "--use_pypi",
        help="fetches license data from pypi if package is not found in current python environment",
        dest="use_pypi",
        action="store_true",
    )
    parser.add_argument(
        "--grace",
        help="allows for a number of blacklisted packages to pass before returning an error",
        type=int,
        const=0
    )
    parser.add_argument("--blacklist", nargs="+", type=str)
    parser.add_argument("--whitelist", nargs="+", type=str)
    parser.set_defaults(use_pypi=False)
    args = parser.parse_args()
    _kwargs = {k: v for k, v in args._get_kwargs()}
    exit(main(**_kwargs))
