import os
import shutil
from typing import Generator

import pytest
from pytest_mock import MockerFixture  # type: ignore[attr-defined]

from cyberfusion.Common import generate_random_string
from cyberfusion.SyncSupport.unix_users import UNIXUserHomeDirectoryArchive


@pytest.fixture
def archive_path_root_directory() -> Generator[str, None, None]:
    path = os.path.join(os.path.sep, "tmp", generate_random_string().lower())

    os.mkdir(path)

    yield path

    shutil.rmtree(path)


@pytest.fixture
def temporary_path_root_path() -> Generator[str, None, None]:
    path = os.path.join(os.path.sep, "tmp", generate_random_string().lower())

    os.mkdir(path)

    yield path

    shutil.rmtree(path)


@pytest.fixture
def unix_user_home_directory(
    mocker: MockerFixture,
) -> Generator[str, None, None]:
    path = os.path.join(os.path.sep, "tmp", generate_random_string().lower())

    mocker.patch("pathlib.Path.home", return_value=path)

    os.makedirs(path)

    yield path

    shutil.rmtree(path)


@pytest.fixture
def dummy_directory(
    unix_user_home_directory: Generator[str, None, None],
) -> Generator[str, None, None]:
    path = os.path.join(unix_user_home_directory, "subdir", "dummy_files")

    os.makedirs(path)

    with open(os.path.join(path, "test1.txt"), "w") as f:
        f.write("Hi! 1")

    with open(os.path.join(path, "test2.txt"), "w") as f:
        f.write("Hi! 2")

    yield os.path.relpath(path, unix_user_home_directory)

    shutil.rmtree(path)


@pytest.fixture
def archive(
    dummy_directory: Generator[str, None, None],
    archive_path_root_directory: Generator[str, None, None],
) -> Generator[str, None, None]:
    archive_path, _ = UNIXUserHomeDirectoryArchive(
        store_path=dummy_directory,
        exclude_paths=[],
        archive_path_root_directory=archive_path_root_directory,
    ).create()

    yield archive_path

    os.unlink(archive_path)
