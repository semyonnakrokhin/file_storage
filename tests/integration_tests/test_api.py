from httpx import AsyncClient


class TestCreateUpdateEndpoint:
    _url = "v1/api/upload"

    async def test_successful_file_upload(self, async_client: AsyncClient):
        file_id = 1
        name = "test_file.txt"
        tag = "test_tag"
        file_content = b"Hello, World!"

        response = await async_client.post(
            url=self._url,
            files={"file": ("test_file.txt", file_content)},
            params={"file_id": file_id, "name": name, "tag": tag},
        )

        assert response.status_code == 201

    async def test_failed_file_upload(self, async_client: AsyncClient):
        # Неверные данные, например, неверный file_id
        file_id = "invalid_file_id"
        name = "test_file.txt"
        tag = "test_tag"
        file_content = b"Hello, World!"

        response = await async_client.post(
            url=self._url,
            files={"file": ("test_file.txt", file_content)},
            params={"file_id": file_id, "name": name, "tag": tag},
        )

        assert response.status_code == 422


class TestGetFilesInfoEndpoint:
    _url = "v1/api/get"

    async def test_successful_get_files_info(self, async_client: AsyncClient):
        response = await async_client.get(url=self._url)
        assert response.status_code == 200

    async def test_get_files_info_with_parameters(self, async_client: AsyncClient):
        # Передаем параметры запроса
        file_id = [1, 2]
        name = ["file1", "file2"]
        tag = ["tag1", "tag2"]
        limit = 10
        offset = 0

        response = await async_client.get(
            url=self._url,
            params={
                "file_id": file_id,
                "name": name,
                "tag": tag,
                "limit": limit,
                "offset": offset,
            },
        )

        assert response.status_code == 200


class TestDeleteFilesEndpoint:
    _url = "v1/api/delete"

    async def test_successful_delete_files(self, async_client: AsyncClient):
        file_id = [1, 2]
        name = ["file1", "file2"]

        response = await async_client.delete(
            url=self._url, params={"file_id": file_id, "name": name}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "4 files deleted"}

    async def test_failed_delete_files(self, async_client: AsyncClient):
        response = await async_client.delete(url=self._url)
        assert response.status_code == 400
        assert response.json() == {"message": "There are no parameters for deletion"}


class TestDownloadFileEndpoint:
    _url = "v1/api/download"

    async def test_successful_download_file(self, async_client: AsyncClient):
        file_id = 1

        response = await async_client.get(url=self._url, params={"file_id": file_id})

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

    async def test_failed_download_file(self, async_client: AsyncClient):
        file_id = -1

        response = await async_client.get(url=self._url, params={"file_id": file_id})

        assert response.status_code == 404
        assert response.json() == {"message": "The file does not exist"}
