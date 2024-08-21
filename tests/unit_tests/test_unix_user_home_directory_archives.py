import getpass
import os
import stat
import tarfile
from pathlib import Path
from typing import Generator

import pytest
from pytest_mock import MockerFixture  # type: ignore[attr-defined]

from cyberfusion.SyncSupport import PATH_ARCHIVE
from cyberfusion.SyncSupport.exceptions import StorePathNotRelativeError
from cyberfusion.SyncSupport.unix_users import UNIXUserHomeDirectoryArchive


def test_unix_user_home_directory_archive_store_path_absolute(
    dummy_directory: Generator[str, None, None],
) -> None:
    with pytest.raises(
        StorePathNotRelativeError,
    ):
        UNIXUserHomeDirectoryArchive(
            store_path=os.path.join(os.path.sep, dummy_directory),
            exclude_paths=[],
        )


def test_unix_user_home_directory_archive_attributes(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=[],
        archive_path_root_directory=archive_path_root_directory,
    )

    assert unix_user_home_directory_archive.home_directory == Path.home()
    assert unix_user_home_directory_archive.username == getpass.getuser()
    assert unix_user_home_directory_archive.archive_path.startswith(
        f"{archive_path_root_directory}/{unix_user_home_directory_archive.username}/archive-"
    )
    assert unix_user_home_directory_archive.archive_path.endswith(".tar.gz")
    assert (
        unix_user_home_directory_archive.archive_path_root_directory
        == archive_path_root_directory
    )


def test_unix_user_home_directory_archive_create_permissions(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=[],
        archive_path_root_directory=archive_path_root_directory,
    )

    assert not os.path.isfile(unix_user_home_directory_archive.archive_path)

    unix_user_home_directory_archive.create()

    assert os.path.isfile(unix_user_home_directory_archive.archive_path)
    assert (
        stat.S_IMODE(
            os.lstat(unix_user_home_directory_archive.archive_path).st_mode
        )
        == 0o600
    )


def test_unix_user_home_directory_archive_create_contents(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=[],
        archive_path_root_directory=archive_path_root_directory,
    )
    path, _ = unix_user_home_directory_archive.create()

    assert sorted(tarfile.open(path).getnames()) == sorted(
        [
            "subdir/dummy_files",
            "subdir/dummy_files/test1.txt",
            "subdir/dummy_files/test2.txt",
        ]
    )


def test_unix_user_home_directory_archive_create_exclude_paths(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=["subdir/dummy_files/test2.txt"],
        archive_path_root_directory=archive_path_root_directory,
    )
    path, _ = unix_user_home_directory_archive.create()

    assert sorted(tarfile.open(path).getnames()) == sorted(
        ["subdir/dummy_files", "subdir/dummy_files/test1.txt"]
    )


def test_unix_user_home_directory_archive_create_md5_hash(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=[],
        archive_path_root_directory=archive_path_root_directory,
    )
    _, md5_hash = unix_user_home_directory_archive.create()

    assert "==" in md5_hash
