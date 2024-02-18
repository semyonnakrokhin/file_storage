from contextlib import nullcontext as does_not_raise
from datetime import datetime

import pytest

from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    MappingError,
    NoConditionsError,
    SessionNotSetError,
)
from fastapi_app.src.db_service.repositories import OrmAlchemyRepository
from fastapi_app.src.schemas import FileMetadata


@pytest.mark.usefixtures("empty_database")
class TestRepositoryInsertOne:
    file_metadata_1 = FileMetadata(
        id=1, name="file1.txt", tag=None, size=1024, mimeType="text/plain"
    )

    file_metadata_2 = FileMetadata(
        id=2,
        name="file2.docx",
        tag="important",
        size=1024,
        mimeType="application/msword",
        modificationTime=datetime.utcnow(),
    )

    file_metadata_3 = FileMetadata(
        id=3,
        name="3",
        tag=None,
        size=2048,
        mimeType="image/jpeg",
        modificationTime=None,
    )

    file_metadata_4 = FileMetadata(
        id=4,
        name="file4.pdf",
        tag=None,
        size=1024,
        mimeType="image/jpeg",
        modificationTime=datetime.utcnow(),
    )

    file_metadata_5 = FileMetadata(
        id=5, name="file5.pdf", size=1024, mimeType="image/jpeg", modificationTime=None
    )

    # Повторяющийся ключ id=6
    file_metadata_6 = FileMetadata(
        id=6, name="file6.pdf", size=1024, mimeType="image/jpeg", modificationTime=None
    )
    # Повторяющийся ключ id=6
    file_metadata_6_double = FileMetadata(
        id=6,
        name="file6_double.pdf",
        size=1024,
        mimeType="image/jpeg",
        modificationTime=None,
    )

    file_metadata_7 = {
        "id": 7,
        "name": "doc_7.docx",
        "tag": "important",
        "size": 1024,
        "mime_type": "application/msword",
    }

    @pytest.mark.parametrize(
        argnames="domain_input, expectation",
        argvalues=[
            (file_metadata_1, does_not_raise()),
            (file_metadata_2, does_not_raise()),
            (file_metadata_3, does_not_raise()),
            (file_metadata_4, does_not_raise()),
            (file_metadata_5, does_not_raise()),
            (file_metadata_7, pytest.raises(MappingError)),
        ],
    )
    async def test_insert_one_different_inputs(
        self, container, database_test, domain_input, expectation
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()
        timestamp = datetime.utcnow()

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.clear_session()
                repository.set_session(session)
                domain_output = await repository.insert_one(data=domain_input)
                await session.commit()
                repository.clear_session()

            assert domain_output.id == domain_input.id
            assert domain_output.name == domain_input.name
            assert domain_output.tag == domain_input.tag
            assert domain_output.size == domain_input.size
            assert domain_output.mimeType == domain_input.mimeType
            assert domain_output.modificationTime > timestamp

            # if domain_input.modificationTime:
            #     assert (
            #             domain_input.modificationTime
            #             < domain_output.modificationTime
            #             < datetime.utcnow()
            #     )
            # else:
            #     assert domain_output.modificationTime < datetime.utcnow()

    @pytest.mark.parametrize(
        argnames="domain_input, expectation",
        argvalues=[
            (file_metadata_6_double, pytest.raises(DatabaseError)),
        ],
    )
    async def test_insert_one_db_errors(
        self, container, database_test, domain_input, expectation
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.clear_session()
                repository.set_session(session)
                domain_output = await repository.insert_one(data=self.file_metadata_6)
                await repository.insert_one(data=domain_input)
                await session.commit()
                repository.clear_session()

            assert domain_output.id == domain_input.id
            assert domain_output.name == domain_input.name
            assert domain_output.tag == domain_input.tag
            assert domain_output.size == domain_input.size
            assert domain_output.mimeType == domain_input.mimeType

            if domain_input.modificationTime:
                assert (
                    domain_input.modificationTime
                    < domain_output.modificationTime
                    < datetime.utcnow()
                )
            else:
                assert domain_output.modificationTime < datetime.utcnow()

    async def test_insert_one_session_set_error(self, container, database_test):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with pytest.raises(SessionNotSetError):
            async with database_test.get_session_factory() as session:
                await repository.insert_one(data=self.file_metadata_6)
                await session.commit()


@pytest.mark.usefixtures("database_with_data")
class TestRepositoryUpdateOne:
    new_file_metadata_1 = FileMetadata(
        id=1, name="New_name.txt", tag="Add some tags", size=1024, mimeType="text/plain"
    )

    new_file_metadata_2 = FileMetadata(
        id=5,
        name="New_name_5.txt",
        tag="Add some tags",
        size=1024,
        mimeType="text/plain",
    )

    new_file_metadata_3 = {
        "id": 3,
        "name": "new_doc_2.docx",
        "tag": "VERY_important",
        "size": 1024,
        "mime_type": "application/msword",
    }

    @pytest.mark.parametrize(
        argnames="new_file_metadata, expectation",
        argvalues=[
            (new_file_metadata_1, does_not_raise()),
            (new_file_metadata_2, pytest.raises(DatabaseError)),
            (new_file_metadata_3, pytest.raises(AttributeError)),
        ],
    )
    async def test_update_one_new_data(
        self, container, database_test, new_file_metadata, expectation
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        timestamp = datetime.utcnow()

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                domain_output_new = await repository.update_one(
                    id=new_file_metadata.id, new_data=new_file_metadata
                )
                await session.commit()
                repository.clear_session()

            assert domain_output_new.id == new_file_metadata.id
            assert domain_output_new.name == new_file_metadata.name
            assert domain_output_new.tag == new_file_metadata.tag
            assert domain_output_new.size == new_file_metadata.size
            assert domain_output_new.mimeType == new_file_metadata.mimeType
            assert domain_output_new.modificationTime > timestamp
            # assert (
            #         domain_output_old.modificationTime
            #         < domain_output_new.modificationTime
            #         < datetime.utcnow()
            # )

    async def test_update_one_session_set_error(self, container, database_test):
        new_file_metadata = FileMetadata(
            id=4, name="New_name.pdf", tag="AAAAAAA", size=1024, mimeType="image/jpeg"
        )

        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with pytest.raises(SessionNotSetError):
            async with database_test.get_session_factory() as session:
                await repository.update_one(
                    id=new_file_metadata.id, new_data=new_file_metadata
                )
                await session.commit()


@pytest.mark.usefixtures("database_with_data")
class TestRepositorySelectOne:
    @pytest.mark.parametrize(
        argnames="id, expectation",
        argvalues=[
            (5, does_not_raise()),
            (4, does_not_raise()),
            (3, does_not_raise()),
            (2, does_not_raise()),
            (1, does_not_raise()),
        ],
    )
    async def test_select_one_different_ids(
        self, container, database_test, id, example_domains_entities, expectation
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        try:
            domain_output_expected = example_domains_entities["domains"][id - 1]
        except IndexError:
            domain_output_expected = None

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                domain_output = await repository.select_one_by_id(id=id)
                await session.commit()
                repository.clear_session()

            if domain_output_expected:
                assert domain_output.id == domain_output_expected.id
                assert domain_output.name == domain_output_expected.name
                assert domain_output.tag == domain_output_expected.tag
                assert domain_output.size == domain_output_expected.size
                assert domain_output.mimeType == domain_output_expected.mimeType
            else:
                assert domain_output is None

    async def test_select_one_session_set_error(self, container, database_test):
        id = 2

        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with pytest.raises(SessionNotSetError):
            async with database_test.get_session_factory() as session:
                await repository.select_one_by_id(id=id)
                await session.commit()


@pytest.mark.usefixtures("database_with_data")
class TestRepositorySelectSome:
    @pytest.mark.parametrize(
        argnames="params, limit, offset, res_ids, expectation",
        argvalues=[
            (
                {
                    "tag": ["important"],
                },
                None,
                None,
                [2, 3],
                does_not_raise(),
            ),
            (
                {
                    "name": ["3", "file4.pdf"],
                },
                None,
                None,
                [3, 4],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 4],
                },
                None,
                None,
                [1, 4],
                does_not_raise(),
            ),
            (
                {"id": [1, 2], "tag": ["important"]},
                None,
                None,
                [
                    2,
                ],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important"],
                    "name": ["file1.txt", "file2.docx", "lalala"],
                },
                None,
                None,
                [
                    2,
                ],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                2,
                None,
                [2, 3],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                None,
                1,
                [3, 4],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                2,
                2,
                [
                    4,
                ],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4, 5, 100, -20],
                    "tag": ["important", "presentations", "SSS"],
                    "name": ["AAA", "WWW"],
                },
                2,
                2,
                [],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, "ddd"],
                    "tag": ["important", "presentations"],
                },
                2,
                2,
                [
                    4,
                ],
                pytest.raises(DatabaseError),
            ),
        ],
    )
    async def test_select_some_different_params(
        self,
        container,
        database_test,
        params,
        limit,
        offset,
        res_ids,
        expectation,
        example_domains_entities,
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )

        domain_expected_lst = [
            domain
            for domain in example_domains_entities["domains"]
            if domain.id in res_ids
        ]

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                domain_output_lst = await repository.select_some_by_params(
                    params=params, limit=limit, offset=offset
                )
                await session.commit()
                repository.clear_session()

            assert len(domain_expected_lst) == len(domain_output_lst)

            for domain_output in domain_output_lst:
                id = domain_output.id
                for domain_expected in domain_expected_lst:
                    if domain_expected.id == id:
                        assert domain_output.id == domain_expected.id
                        assert domain_output.name == domain_expected.name
                        assert domain_output.tag == domain_expected.tag
                        assert domain_output.size == domain_expected.size
                        assert domain_output.mimeType == domain_expected.mimeType
                        break
                else:
                    raise

    async def test_select_some_session_set_error(self, container, database_test):
        params = {
            "id": [1, 2, 3, 4],
            "tag": ["important", "presentations"],
        }
        limit, offset = 2, 1

        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with pytest.raises(SessionNotSetError):
            async with database_test.get_session_factory() as session:
                await repository.select_some_by_params(
                    params=params, limit=limit, offset=offset
                )
                await session.commit()


@pytest.mark.usefixtures("database_with_data")
class TestRepositoryDeleteSome:
    @pytest.mark.parametrize(
        argnames="params, limit, offset, res_ids, expectation",
        argvalues=[
            ({}, None, None, [], pytest.raises(NoConditionsError)),
            (
                {
                    "id": [1, 4],
                },
                None,
                None,
                [1, 4],
                does_not_raise(),
            ),
            (
                {"id": [1, 2], "tag": ["important"]},
                None,
                None,
                [
                    2,
                ],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important"],
                    "name": ["file1.txt", "file2.docx", "lalala"],
                },
                None,
                None,
                [
                    2,
                ],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                2,
                None,
                [2, 3, 4],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                None,
                1,
                [2, 3, 4],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4],
                    "tag": ["important", "presentations"],
                },
                2,
                2,
                [2, 3, 4],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, 4, 5, 100, -20],
                    "tag": ["important", "presentations", "SSS"],
                    "name": ["AAA", "WWW"],
                },
                2,
                2,
                [],
                does_not_raise(),
            ),
            (
                {
                    "id": [1, 2, 3, "ddd"],
                    "tag": ["important", "presentations"],
                },
                2,
                2,
                [
                    4,
                ],
                pytest.raises(DatabaseError),
            ),
            (
                {
                    "tag": ["important"],
                },
                None,
                None,
                [2, 3],
                does_not_raise(),
            ),
            (
                {
                    "name": ["3", "file4.pdf"],
                },
                None,
                None,
                [3, 4],
                does_not_raise(),
            ),
        ],
    )
    async def test_delete_some_different_params(
        self,
        container,
        database_test,
        params,
        limit,
        offset,
        res_ids,
        expectation,
        database_with_data,
    ):
        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                id_lst = await repository.delete_some_by_params(
                    params=params, limit=limit, offset=offset
                )
                await session.commit()
                repository.clear_session()

            assert res_ids == id_lst

    async def test_delete_some_session_set_error(
        self,
        container,
        database_test,
    ):
        params = {
            "id": [1, 2, 3, 4],
            "tag": ["important", "presentations"],
        }
        limit, offset = 2, 1

        repository: OrmAlchemyRepository = (
            container.repositories.file_metadata_repository_provider()
        )
        repository.clear_session()

        with pytest.raises(SessionNotSetError):
            async with database_test.get_session_factory() as session:
                await repository.delete_some_by_params(
                    params=params, limit=limit, offset=offset
                )
                await session.commit()
