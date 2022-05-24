from __future__ import annotations

import contextlib
import importlib
import os
import pathlib
import re
import shutil
import sys
from io import StringIO
from typing import Optional

from duty import duty

PACKAGE_NAME = "easy_email_downloader"
REPO_URL = "https://github.com/dtomlinson91/easy-email-downloader"


@duty(post=["export"])
def update_deps(ctx, dry: bool = False):
    """
    Update the dependencies using Poetry.

    Args:
        ctx: The context instance (passed automatically).
        dry (bool, optional) = If True will update the `poetry.lock` without updating the
            dependencies themselves. Defaults to False.

    Example:
        `duty update_deps dry=False`
    """
    dry_run = "--dry-run" if dry else ""
    ctx.run(
        ["poetry", "update", dry_run],
        title=f"Updating poetry deps {dry_run}",
    )


@duty
def test(ctx):
    """
    Run tests using pytest.

    Args:
        ctx: The context instance (passed automatically).
    """
    pytest_results = ctx.run(["pytest", "-v"], pty=True)
    print(pytest_results)


@duty
def coverage(ctx):
    """
    Generate a coverage report and save to XML and HTML.

    Args:
        ctx: The context instance (passed automatically).

    Example:
        `duty coverage`
    """
    ctx.run(["coverage", "run", "--source", PACKAGE_NAME, "-m", "pytest"])
    res = ctx.run(["coverage", "report"], pty=True)
    print(res)
    ctx.run(["coverage", "html"])
    ctx.run(["coverage", "xml"])


@duty
def bump(ctx, version: str = "patch"):
    """
    Bump the version using Poetry and update _version.py.

    Args:
        ctx: The context instance (passed automatically).
        version (str, optional) = poetry version flag. Available options are:
            patch, minor, major, prepatch, preminor, premajor, prerelease.
            See <https://python-poetry.org/docs/cli/#version> Defaults to patch.

    Example:
        `duty bump version=major`
    """
    # bump with poetry
    result = ctx.run(["poetry", "version", version])
    new_version = re.search(r"(?<=to\s)([^\$]*)", result)
    print(new_version.group(0))

    # update _version.py
    version_file = pathlib.Path(PACKAGE_NAME) / "_version.py"
    with version_file.open("w", encoding="utf-8") as version_file:
        version_file.write(
            f'"""Module containing the version of {PACKAGE_NAME}."""\n\n' + f'__version__ = "{new_version.group(0)}"\n'
        )
    print(f"Bumped _version.py to {new_version.group(1)}")


@duty
def build(ctx):
    """
    Build with poetry and extract the setup.py and copy to project root.

    Args:
        ctx: The context instance (passed automatically).

    Example:
        `duty build`
    """

    repo_root = pathlib.Path(".")

    # build with poetry
    result = ctx.run(["poetry", "build"])
    print(result)

    # extract the setup.py from the tar
    extracted_tar = re.search(r"(?:.*)(?:Built\s)(.*)", result)
    tar_file = pathlib.Path(f"./dist/{extracted_tar.group(1)}")
    shutil.unpack_archive(tar_file, tar_file.parents[0])

    # copy setup.py to repo root
    extracted_path = tar_file.parents[0] / os.path.splitext(tar_file.stem)[0]
    setup_py = extracted_path / "setup.py"
    shutil.copyfile(setup_py, (repo_root / "setup.py"))

    # cleanup
    shutil.rmtree(extracted_path)


@duty
def release(ctx, version: str = "patch") -> None:
    """
    Prepare package for a new release.

    Will run bump, build, export. Manual running of publish is required afterwards.

    Args:
        ctx: The context instance (passed automatically).
        version (str): poetry version flag.
            Available options are: patch, minor, major, prepatch, preminor, premajor, prerelease.
            See <https://python-poetry.org/docs/cli/#version>
    """
    print(ctx.run(["duty", "bump", f"version={version}"]))
    ctx.run(["duty", "build"])
    ctx.run(["duty", "export"])
    print(
        "✔ Check generated files. Run `duty changelog planned_release= previous_release=` and `duty publish password=`"
        " when ready to publish."
    )


@duty
def export(ctx):
    """
    Export the dependencies to a requirements.txt file.

    Args:
        ctx: The context instance (passed automatically).

    Example:
        `duty export`
    """
    # requirements_content = ctx.run(
    #     [
    #         "poetry",
    #         "export",
    #         "-f",
    #         "requirements.txt",
    #         "--without-hashes",
    #     ]
    # )
    requirements_dev_content = ctx.run(
        [
            "poetry",
            "export",
            "-f",
            "requirements.txt",
            "--without-hashes",
            "--dev",
        ]
    )

    requirements = pathlib.Path(".") / "requirements.txt"
    # requirements_dev = pathlib.Path(".") / "requirements_dev.txt"

    with requirements.open("w", encoding="utf-8") as req:
        req.write(requirements_dev_content)

    # with requirements_dev.open("w", encoding="utf-8") as req:
    #     req.write(requirements_dev_content)


@duty
def publish(ctx, password: str):
    """
    Publish the package to pypi.org.

    Args:
        ctx: The context instance (passed automatically).
        password (str): pypi.org password.

    Example:
        `duty publish password=$my_password`
    """
    dist_dir = pathlib.Path(".") / "dist"
    rm_result = rm_tree(dist_dir)
    print(rm_result)

    publish_result = ctx.run(["poetry", "publish", "-u", "dtomlinson", "-p", password, "--build"])
    print(publish_result)


@duty(silent=True)
def clean(ctx):
    """
    Delete temporary files.

    Args:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf tests/.pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("rm -rf coverage.xml")
    ctx.run("rm -rf pytest.xml")
    ctx.run("rm -rf htmlcov")
    ctx.run("find . -iname '.coverage*' -not -name .coveragerc | xargs rm -rf")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


@duty
def format(ctx):
    """
    Format code using Black and isort.

    Args:
        ctx: The context instance (passed automatically).
    """
    res = ctx.run(["black", "--line-length=120", PACKAGE_NAME], pty=True, title="Running Black")
    print(res)

    res = ctx.run(["isort", "-l", "120", PACKAGE_NAME])
    print(res)


@duty(pre=["check_code_quality", "check_types", "check_docs", "check_dependencies"])
def check(ctx):
    """
    Check the code quality, check types, check documentation builds and check dependencies for vulnerabilities.

    Args:
        ctx: The context instance (passed automatically).
    """


@duty
def check_code_quality(ctx):
    """
    Check the code quality using prospector.

    Ran as part of `duty check`.

    Args:
        ctx: The context instance (passed automatically).
    """
    ctx.run(["prospector", PACKAGE_NAME], pty=True, title="Checking code quality with prospector")


@duty
def check_types(ctx):
    """
    Check the types using mypy.

    Ran as part of `duty check`.

    Args:
        ctx: The context instance (passed automatically).
    """
    ctx.run(["mypy", PACKAGE_NAME], pty=True, title="Checking types with MyPy")


@duty
def check_docs(ctx):
    """
    Check the documentation builds successfully.

    Ran as part of `duty check`.

    Args:
        ctx: The context instance (passed automatically).
    """
    with contextlib.suppress(FileNotFoundError):
        ctx.run(["mkdocs", "build"], title="Building documentation")


@duty
def check_dependencies(ctx):
    """
    Check dependencies with safety for vulnerabilities.

    Ran as part of `duty check`.

    Args:
        ctx: The context instance (passed automatically).
    """
    with contextlib.suppress(ModuleNotFoundError):
        for module in sys.modules:
            if module.startswith("safety.") or module == "safety":
                del sys.modules[module]

        importlib.invalidate_caches()

        from safety import safety
        from safety.formatter import report
        from safety.util import read_requirements

        requirements = ctx.run(
            "poetry export --dev --without-hashes",
            title="Exporting dependencies as requirements",
            allow_overrides=False,
        )

        def check_vulns():
            packages = list(read_requirements(StringIO(requirements)))
            vulns = safety.check(packages=packages, ignore_ids="41002", key="", db_mirror="", cached=False, proxy={})
            output_report = report(vulns=vulns, full=True, checked_packages=len(packages))
            print(vulns)
            if vulns:
                print(output_report)

        ctx.run(
            check_vulns,
            stdin=requirements,
            title="Checking dependencies",
            pty=True,
        )


@duty
def changelog(ctx, planned_release: Optional[str] = None, previous_release: Optional[str] = None):
    """
    Generate a changelog with git-cliff.

    Args:
        ctx: The context instance (passed automatically).
        planned_release (str, optional): The planned release version. Example: v1.0.2
        previous_release (str, optional): The previous release version. Example: v1.0.1
    """
    generated_changelog: str = ctx.run(["git", "cliff", "-u", "-t", planned_release, "-s", "header"])[:-1]
    if previous_release is not None:
        generated_changelog: list = generated_changelog.splitlines()
        generated_changelog.insert(
            1,
            f"<small>[Compare with {previous_release}]({REPO_URL}/compare/{previous_release}...{planned_release})</small>",
        )
        generated_changelog: str = "\n".join([line for line in generated_changelog]) + "\n"
    new_changelog = []

    changelog_file = pathlib.Path(".") / "CHANGELOG.md"
    with changelog_file.open("r", encoding="utf-8") as changelog_contents:
        all_lines = changelog_contents.readlines()
        for line_string in all_lines:
            regex_string = re.search(r"(<!-- marker -->)", line_string)
            new_changelog.append(line_string)
            if isinstance(regex_string, re.Match):
                new_changelog.append(generated_changelog)
    with changelog_file.open("w", encoding="utf-8") as changelog_contents:
        changelog_contents.writelines(new_changelog)


def rm_tree(directory: pathlib.Path):
    """
    Recursively delete a directory and all its contents.

    Args:
        directory (pathlib.Path): The directory to delete.
    """
    for child in directory.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    directory.rmdir()
