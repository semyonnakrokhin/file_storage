import io
import os
from contextlib import nullcontext as does_not_raise

import pytest
from fastapi import UploadFile

from fastapi_app.src.file_storage.exceptions import FileAlreadyExistsError
from fastapi_app.src.schemas import FileMetadata

temp_dir = os.path.join(os.path.dirname(__file__), os.path.pardir, "storage_test")


@pytest.mark.usefixtures("test_storage_dir")
class TestCheckStorageDirectoryExists:
    def test_directory_created_successfully(
        self, disk_repository_test, test_storage_dir
    ):
        disk_repository_test._DiskRepository__check_storage_directory_exists()
        assert os.path.exists(temp_dir)


@pytest.mark.usefixtures("test_storage_dir")
class TestGetFilePath:
    @pytest.mark.parametrize(
        argnames="file_id, file_name_ext, file_content, mime_type, expectation",
        argvalues=[
            (1, "test_file_1.txt", b"Hello, World!", "text/plain", does_not_raise()),
            (2, "test_file_2.txt", b"Hello, World 2!", "text/plain", does_not_raise()),
        ],
    )
    def test_file_path_generated_successfully(
        self,
        disk_repository_test,
        test_storage_dir,
        file_id,
        file_name_ext,
        file_content,
        mime_type,
        expectation,
    ):
        file_path_expected = os.path.join(test_storage_dir, file_name_ext)
        with open(file_path_expected, "wb") as f:
            f.write(file_content)

        file_metadata = FileMetadata(id=file_id, name=file_name_ext, mimeType=mime_type)

        with expectation:
            file_path = disk_repository_test._DiskRepository__get_file_path(
                domain_obj=file_metadata
            )
            assert file_path is not None
            assert file_path == file_path_expected

        if file_path_expected:
            os.remove(file_path_expected)


@pytest.mark.usefixtures("test_storage_dir")
class TestValidateFileDoesNotExist:
    def test_file_does_not_exist(self, disk_repository_test):
        file_metadata = FileMetadata(
            id=1, name="test_file_1.txt", mimeType="text/plain"
        )
        disk_repository_test._DiskRepository__validate_file_does_not_exist(
            file_metadata
        )

    @pytest.mark.parametrize(
        argnames="file_id, file_name_ext, file_content, mime_type",
        argvalues=[
            (1, "test_file_1.txt", b"Hello, World!", "text/plain"),
        ],
    )
    def test_file_exists(
        self,
        disk_repository_test,
        test_storage_dir,
        file_id,
        file_name_ext,
        file_content,
        mime_type,
    ):
        file_path_expected = os.path.join(test_storage_dir, file_name_ext)
        with open(file_path_expected, "wb") as f:
            f.write(file_content)

        file_metadata = FileMetadata(id=file_id, name=file_name_ext, mimeType=mime_type)

        with pytest.raises(FileAlreadyExistsError):
            disk_repository_test._DiskRepository__validate_file_does_not_exist(
                file_metadata
            )

        if file_path_expected:
            os.remove(file_path_expected)


@pytest.mark.usefixtures("test_storage_dir")
class TestWriteFile:
    @pytest.mark.parametrize(
        argnames="file_id, file_name_ext, file_content, mime_type, expectation",
        argvalues=[
            (1, "test_file_1.txt", b"Hello, World!", "text/plain", does_not_raise()),
        ],
    )
    async def test_write_file_successful(
        self,
        test_storage_dir,
        disk_repository_test,
        file_content,
        file_id,
        file_name_ext,
        mime_type,
        expectation,
    ):
        file_path_expected = os.path.join(test_storage_dir, file_name_ext)
        file_metadata = FileMetadata(id=file_id, name=file_name_ext, mimeType=mime_type)
        file = UploadFile(filename="example.txt", file=io.BytesIO(file_content))

        with expectation:
            await disk_repository_test.write_file(file=file, domain_obj=file_metadata)
            assert os.path.exists(file_path_expected)

        if file_path_expected:
            os.remove(file_path_expected)


@pytest.mark.usefixtures("test_storage_dir")
class TestReadFile:
    @pytest.mark.parametrize(
        argnames="file_id, file_name_ext, file_content, mime_type, expectation",
        argvalues=[
            (1, "test_file_1.txt", b"Hello, World!", "text/plain", does_not_raise()),
        ],
    )
    async def test_read_file_successful(
        self,
        test_storage_dir,
        disk_repository_test,
        file_content,
        file_id,
        file_name_ext,
        mime_type,
        expectation,
    ):
        file_path_expected = os.path.join(test_storage_dir, file_name_ext)
        with open(file_path_expected, "wb") as f:
            f.write(file_content)

        file_metadata = FileMetadata(id=file_id, name=file_name_ext, mimeType=mime_type)

        with expectation:
            payload = disk_repository_test.read_file(domain_obj=file_metadata)

            assert payload["path"] == file_path_expected
            assert payload["media_type"] == mime_type
            assert payload["filename"] == file_name_ext

        if file_path_expected:
            os.remove(file_path_expected)


@pytest.mark.usefixtures("test_storage_dir")
class TestDeleteFile:
    @pytest.mark.parametrize(
        argnames="file_id, file_name_ext, file_content, mime_type, expectation",
        argvalues=[
            (1, "test_file_1.txt", b"Hello, World!", "text/plain", does_not_raise()),
        ],
    )
    async def test_delete_file_successful(
        self,
        test_storage_dir,
        disk_repository_test,
        file_content,
        file_id,
        file_name_ext,
        mime_type,
        expectation,
    ):
        file_path_expected = os.path.join(test_storage_dir, file_name_ext)
        with open(file_path_expected, "wb") as f:
            f.write(file_content)

        file_name, _ = os.path.splitext(file_name_ext)
        file_metadata = FileMetadata(id=file_id, name=file_name, mimeType=mime_type)

        with expectation:
            disk_repository_test.delete_file(domain_obj=file_metadata)

            file = disk_repository_test._DiskRepository__get_file_path(
                domain_obj=file_metadata
            )
            assert file is None

        if file:
            os.remove(file_path_expected)
