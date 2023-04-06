# SPDX-License-Identifier: LGPL-2.1+

from collections.abc import Sequence
from pathlib import Path

from mkosi.backend import MkosiState, add_packages
from mkosi.distributions import DistributionInstaller
from mkosi.distributions.fedora import Repo, invoke_dnf, setup_dnf
from mkosi.log import complete_step


class MageiaInstaller(DistributionInstaller):
    @classmethod
    def filesystem(cls) -> str:
        return "ext4"

    @classmethod
    def install(cls, state: MkosiState) -> None:
        return install_mageia(state)

    @classmethod
    def install_packages(cls, state: MkosiState, packages: Sequence[str]) -> None:
        invoke_dnf(state, "install", packages)

    @classmethod
    def remove_packages(cls, state: MkosiState, packages: Sequence[str]) -> None:
        invoke_dnf(state, "remove", packages)


@complete_step("Installing Mageia…")
def install_mageia(state: MkosiState) -> None:
    release = state.config.release.strip("'")

    if state.config.local_mirror:
        release_url = f"baseurl={state.config.local_mirror}"
        updates_url = None
    elif state.config.mirror:
        baseurl = f"{state.config.mirror}/distrib/{release}/{state.config.architecture}/media/core/"
        release_url = f"baseurl={baseurl}/release/"
        if release == "cauldron":
            updates_url = None
        else:
            updates_url = f"baseurl={baseurl}/updates/"
    else:
        baseurl = f"https://www.mageia.org/mirrorlist/?release={release}&arch={state.config.architecture}&section=core"
        release_url = f"mirrorlist={baseurl}&repo=release"
        if release == "cauldron":
            updates_url = None
        else:
            updates_url = f"mirrorlist={baseurl}&repo=updates"

    gpgpath = Path("/etc/pki/rpm-gpg/RPM-GPG-KEY-Mageia")

    repos = [Repo(f"mageia-{release}", release_url, gpgpath)]
    if updates_url is not None:
        repos += [Repo(f"mageia-{release}-updates", updates_url, gpgpath)]

    setup_dnf(state, repos)

    packages = state.config.packages.copy()
    add_packages(state.config, packages, "filesystem")

    invoke_dnf(state, "install", packages)
