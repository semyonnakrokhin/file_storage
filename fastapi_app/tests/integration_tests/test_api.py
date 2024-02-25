import os

import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("test_storage_dir")
@pytest.mark.usefixtures("database_with_data")
class TestCreateUpdateEndpoint:
    _url = "v1/api/upload"

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, file",
        argvalues=[
            (5, "some_name", "test_tag", ("test_file.txt", b"Hello, World!")),
            (6, "another_name", "test_tag", ("fff.txt", b"Hello, World!")),
        ],
    )
    async def test_successful_file_add(
        self, async_client: AsyncClient, file_id, name, tag, file, test_storage_dir
    ):
        response_empty = await async_client.get(
            url="v1/api/get",
            params={
                "file_id": [
                    file_id,
                ],
                "name": [
                    name,
                ],
                "tag": [
                    tag,
                ],
            },
        )
        data_empty_lst = response_empty.json()
        assert data_empty_lst == []

        response = await async_client.post(
            url=self._url,
            files={"file": file},
            params={"file_id": file_id, "name": name, "tag": tag},
        )

        assert response.status_code == 201

        data = response.json()
        assert len(data) == 6
        assert data["id"] == file_id
        assert data["name"] == name
        assert data["tag"] == tag

        _, ext = os.path.splitext(file[0])
        file_path_expected = os.path.join(test_storage_dir, name + ext)
        assert os.path.exists(file_path_expected)
        # os.remove(file_path_expected)

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, file",
        argvalues=[
            (
                1,
                "new_some_name",
                "new_test_tag",
                ("test_file.txt", b"New Hello, World!"),
            ),
            (2, "new_another_name", "new_test_tag", ("fff.txt", b"New Hello, World!")),
        ],
    )
    async def test_successful_file_update(
        self, async_client: AsyncClient, file_id, name, tag, file, test_storage_dir
    ):
        response_exist = await async_client.get(
            url="v1/api/get",
            params={
                "file_id": [
                    file_id,
                ]
            },
        )
        data_exist_lst = response_exist.json()
        assert len(data_exist_lst) == 1
        data_exist_dict = data_exist_lst[0]
        assert data_exist_dict["id"] == file_id

        response = await async_client.post(
            url=self._url,
            files={"file": file},
            params={"file_id": file_id, "name": name, "tag": tag},
        )

        assert response.status_code == 201

        data = response.json()
        assert len(data) == 6
        assert data["id"] == file_id
        assert data["name"] == name
        assert data["tag"] == tag

        _, ext = os.path.splitext(file[0])
        file_path_expected = os.path.join(test_storage_dir, name + ext)
        assert os.path.exists(file_path_expected)
        # os.remove(file_path_expected)

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, file",
        argvalues=[
            (
                "invalid_file_id",
                "string",
                "super_tag",
                ("test_file.txt", b"New Hello, World!"),
            ),
        ],
    )
    async def test_failed_file_upload(
        self, async_client: AsyncClient, file_id, name, tag, file
    ):
        response = await async_client.post(
            url=self._url,
            files={"file": file},
            params={"file_id": file_id, "name": name, "tag": tag},
        )

        assert response.status_code == 422


@pytest.mark.usefixtures("test_storage_dir")
@pytest.mark.usefixtures("database_with_data")
class TestGetFilesInfoEndpoint:
    _url = "v1/api/get"

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, limit, offset, result_ids",
        argvalues=[([1, 2, 3, "ddd"], None, ["important", "presentations"], 2, 2, [])],
    )
    async def test_get_files_info_errors(
        self, async_client: AsyncClient, file_id, name, tag, limit, offset, result_ids
    ):
        params = {
            n: v
            for n, v in locals().items()
            if n in ("file_id", "name", "tag", "limit", "offset") and v is not None
        }

        response = await async_client.get(
            url=self._url,
            params=params,
        )

        assert response.status_code == 422

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, limit, offset, result_ids",
        argvalues=[
            (
                None,
                None,
                [
                    "important",
                ],
                None,
                None,
                [2, 3],
            ),
            (None, ["3", "file4.pdf"], None, None, None, [3, 4]),
            ([1, 4], None, None, None, None, [1, 4]),
            ([1, 2], None, ["important"], None, None, [2]),
            (
                [1, 2, 3, 4],
                ["file1.txt", "file2.docx", "lalala"],
                ["important"],
                None,
                None,
                [2],
            ),
            ([1, 2, 3, 4], None, ["important", "presentations"], 2, None, [2, 3]),
            ([1, 2, 3, 4], None, ["important", "presentations"], None, 1, [3, 4]),
            ([1, 2, 3, 4], None, ["important", "presentations"], None, 2, [4]),
            (
                [1, 2, 3, 4, 5, 100, -20],
                ["AAA", "WWW"],
                ["important", "presentations", "SSS"],
                2,
                2,
                [],
            ),
        ],
    )
    async def test_get_files_info_with_parameters(
        self, async_client: AsyncClient, file_id, name, tag, limit, offset, result_ids
    ):
        params = {
            n: v
            for n, v in locals().items()
            if n in ("file_id", "name", "tag", "limit", "offset") and v is not None
        }

        response = await async_client.get(
            url=self._url,
            params=params,
        )

        assert response.status_code == 200
        data_lst = response.json()
        for data in data_lst:
            assert data["id"] in result_ids


@pytest.mark.usefixtures("test_storage_dir")
@pytest.mark.usefixtures("database_with_data")
class TestDeleteFilesEndpoint:
    _url = "v1/api/delete"

    @pytest.mark.parametrize(
        argnames="file_id, name, tag, num_deleted",
        argvalues=[
            ([1, 4], None, None, 2),
            ([1, 2, 3, 4], None, ["important"], 2),
        ],
    )
    async def test_successful_delete_files(
        self, async_client: AsyncClient, file_id, name, tag, num_deleted
    ):
        params = {
            n: v
            for n, v in locals().items()
            if n in ("file_id", "name", "tag", "limit", "offset") and v is not None
        }

        response = await async_client.delete(url=self._url, params=params)
        assert response.status_code == 200
        assert response.json() == {"message": f"{num_deleted} files deleted"}

    async def test_failed_delete_files(self, async_client: AsyncClient):
        response = await async_client.delete(url=self._url)
        assert response.status_code == 400
        assert response.json() == {"message": "There are no parameters for deletion"}


@pytest.mark.usefixtures("test_storage_dir")
@pytest.mark.usefixtures("database_with_data")
class TestDownloadFileEndpoint:
    _url = "v1/api/download"

    async def test_successful_download_file(
        self, async_client: AsyncClient, test_storage_dir
    ):
        response_post = await async_client.post(
            url="v1/api/upload",
            files={"file": ("test_delete.txt", b"New Hello, World!")},
            params={"file_id": 1, "name": "test_delete"},
        )

        data_post = response_post.json()
        response = await async_client.get(
            url=self._url, params={"file_id": data_post["id"]}
        )

        assert response.status_code == 200
        assert "Custom-Message" in response.headers
        assert response.headers["Custom-Message"] == "OK"
        assert response.content == b"New Hello, World!"

    async def test_failed_download_file(self, async_client: AsyncClient):
        file_id = -1

        response = await async_client.get(url=self._url, params={"file_id": file_id})

        assert response.status_code == 404
        assert response.json() == {"message": "The file does not exist"}
