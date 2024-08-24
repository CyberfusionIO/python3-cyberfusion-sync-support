import os
import shutil
from pathlib import Path
from typing import Generator

import pytest
from pytest_mock import MockerFixture  # type: ignore[attr-defined]

from cyberfusion.SyncSupport.exceptions import (
    FilesystemPathNotRelativeError,
    IllegalMemberError,
    StorePathNotRelativeError,
)
from cyberfusion.SyncSupport.unix_users import (
    UNIXUserHomeDirectoryArchiveRestoration,
)


def test_unix_user_home_directory_archive_restoration_store_path_absolute(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    with pytest.raises(StorePathNotRelativeError):
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=os.path.join(os.path.sep, dummy_directory),
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )


def test_unix_user_home_directory_archive_restoration_filesystem_path_absolute(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    with pytest.raises(FilesystemPathNotRelativeError):
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=os.path.join(os.path.sep, dummy_directory),
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )


def test_unix_user_home_directory_archive_restoration_attributes(
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    unix_user_home_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )
    )

    assert unix_user_home_directory_archive_restoration.home_directory == Path.home()
    assert unix_user_home_directory_archive_restoration.filesystem_path == os.path.join(
        unix_user_home_directory, dummy_directory
    )
    assert unix_user_home_directory_archive_restoration.old_path.startswith(
        os.path.join(
            unix_user_home_directory,
            "subdir",
            ".archive-restore-old.dummy_files-",
        )
    )
    assert unix_user_home_directory_archive_restoration.new_path.startswith(
        os.path.join(
            unix_user_home_directory,
            "subdir",
            ".archive-restore-new.dummy_files-",
        )
    )
    assert unix_user_home_directory_archive_restoration.temporary_path.startswith(
        os.path.join(temporary_path_root_path, ".archive-restore-tmp.dummy_files-")
    )

    assert os.path.isdir(unix_user_home_directory_archive_restoration.temporary_path)
    assert (
        os.stat(unix_user_home_directory_archive_restoration.temporary_path).st_mode
        == 16832
    )


def test_unix_user_home_directory_archive_restoration_restore_directory_not_exists(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )
    )

    shutil.rmtree(unix_user_home_directory_archive_restoration.filesystem_path)

    spy_lexists = mocker.spy(os.path, "lexists")
    spy_shutil_move = mocker.spy(shutil, "move")
    spy_rename = mocker.spy(os, "rename")

    unix_user_home_directory_archive_restoration.replace()

    spy_shutil_move.assert_called_once_with(
        os.path.join(
            unix_user_home_directory_archive_restoration.temporary_path,
            "subdir",
            "dummy_files",
        ),
        unix_user_home_directory_archive_restoration.new_path,
    )
    spy_lexists.assert_has_calls(
        [
            mocker.call(unix_user_home_directory_archive_restoration.filesystem_path),
            mocker.call(unix_user_home_directory_archive_restoration.old_path),
        ],
    )
    assert spy_rename.call_args_list[-1] == mocker.call(
        unix_user_home_directory_archive_restoration.new_path,
        unix_user_home_directory_archive_restoration.filesystem_path,
    )


def test_unix_user_home_directory_archive_restoration_restore_directory_exists(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )
    )

    spy_lexists = mocker.spy(os.path, "lexists")
    spy_shutil_move = mocker.spy(shutil, "move")
    spy_shutil_rmtree = mocker.spy(shutil, "rmtree")
    spy_rename = mocker.spy(os, "rename")

    unix_user_home_directory_archive_restoration.replace()

    spy_shutil_move.assert_called_once_with(
        os.path.join(
            unix_user_home_directory_archive_restoration.temporary_path,
            "subdir",
            "dummy_files",
        ),
        unix_user_home_directory_archive_restoration.new_path,
    )
    spy_lexists.assert_has_calls(
        [
            mocker.call(unix_user_home_directory_archive_restoration.filesystem_path),
            mocker.call(unix_user_home_directory_archive_restoration.old_path),
        ],
    )
    assert spy_rename.call_args_list[-2] == mocker.call(
        unix_user_home_directory_archive_restoration.filesystem_path,
        unix_user_home_directory_archive_restoration.old_path,
    )
    assert spy_rename.call_args_list[-1] == mocker.call(
        unix_user_home_directory_archive_restoration.new_path,
        unix_user_home_directory_archive_restoration.filesystem_path,
    )
    spy_shutil_rmtree.assert_called_once_with(
        unix_user_home_directory_archive_restoration.old_path
    )


def test_unix_user_home_directory_archive_restoration_restore_member_not_in_store_path(
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path="archive_with_unexpected_file.tar.gz",
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=[],
        )
    )

    with pytest.raises(
        IllegalMemberError,
    ) as e:
        unix_user_home_directory_archive_restoration.replace()

    assert e.value.member_name == "unexpected"


def test_unix_user_home_directory_archive_restoration_restore_copy_file(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=["subdir/dummy_files/only_in_right_and_excluded.txt"],
        )
    )

    spy_shutil_copyfile = mocker.spy(shutil, "copyfile")

    with open(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "only_in_right_and_excluded.txt",
        ),
        "w",
    ):
        pass

    with open(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "only_in_right_and_not_excluded.txt",
        ),
        "w",
    ):
        pass

    unix_user_home_directory_archive_restoration.replace()

    spy_shutil_copyfile.assert_called_once_with(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "only_in_right_and_excluded.txt",
        ),
        os.path.join(
            unix_user_home_directory_archive_restoration.temporary_path,
            "subdir/dummy_files/only_in_right_and_excluded.txt",
        ),
    )

    assert (
        mocker.call(
            os.path.join(
                unix_user_home_directory_archive_restoration.filesystem_path,
                "only_in_right_and_not_excluded.txt",
            ),
            os.path.join(
                unix_user_home_directory_archive_restoration.temporary_path,
                "subdir/dummy_files/only_in_right_and_not_excluded.txt",
            ),
            unix_user_home_directory_archive_restoration.new_path,
        )
        not in spy_shutil_copyfile.call_args_list
    )


def test_unix_user_home_directory_archive_restoration_restore_copy_directory(
    mocker: MockerFixture,
    archive: Generator[str, None, None],
    dummy_directory: Generator[str, None, None],
    temporary_path_root_path: Generator[str, None, None],
) -> None:
    unix_user_home_directory_archive_restoration = (
        UNIXUserHomeDirectoryArchiveRestoration(
            store_path=dummy_directory,
            filesystem_path=dummy_directory,
            archive_path=archive,
            temporary_path_root_path=temporary_path_root_path,
            exclude_paths=["subdir/dummy_files/subdir1"],
        )
    )

    spy_shutil_copytree = mocker.spy(shutil, "copytree")

    os.makedirs(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "subdir1",
        )
    )

    os.makedirs(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "subdir2",
        )
    )

    unix_user_home_directory_archive_restoration.replace()

    spy_shutil_copytree.assert_called_once_with(
        os.path.join(
            unix_user_home_directory_archive_restoration.filesystem_path,
            "subdir1",
        ),
        os.path.join(
            unix_user_home_directory_archive_restoration.temporary_path,
            "subdir/dummy_files/subdir1",
        ),
        ignore_dangling_symlinks=True,
    )

    assert (
        mocker.call(
            os.path.join(
                unix_user_home_directory_archive_restoration.filesystem_path,
                "subdir2",
            ),
            os.path.join(
                unix_user_home_directory_archive_restoration.temporary_path,
                "subdir/dummy_files/subdir2",
            ),
            ignore_dangling_symlinks=True,
        )
        not in spy_shutil_copytree.call_args_list
    )
