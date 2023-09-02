import pytest
import pandas as pd
from pandas.testing import assert_frame_equal as pd_assert_frame_equal

from pinecone_datasets import Dataset, DatasetInitializationError
from pinecone_datasets.catalog import DatasetMetadata, DenseModelMetadata

d = pd.DataFrame(
    [
        {
            "id": "1",
            "values": [0.1, 0.2, 0.3],
            "sparse_values": {"indices": [1, 2, 3], "values": [0.1, 0.2, 0.3]},
            "metadata": {"title": "title1", "url": "url1"},
            "blob": None,
        },
        {
            "id": "2",
            "values": [0.4, 0.5, 0.6],
            "sparse_values": {"indices": [4, 5, 6], "values": [0.4, 0.5, 0.6]},
            "metadata": {"title": "title2", "url": "url2"},
            "blob": None,
        },
    ]
)

q = pd.DataFrame(
    [
        {
            "vector": [0.1, 0.2, 0.3],
            "sparse_vector": {"indices": [1, 2, 3], "values": [0.1, 0.2, 0.3]},
            "filter": {"filter1": {"$eq": "filter1"}},
            "top_k": 1,
            "blob": None,
        },
        {
            "vector": [0.4, 0.5, 0.6],
            "sparse_vector": {"indices": [4, 5, 6], "values": [0.4, 0.5, 0.6]},
            "filter": {"filter2": {"$eq": "filter2"}},
            "top_k": 2,
            "blob": None,
        },
    ]
)


def test_default_loading():
    ds = Dataset.from_pandas(documents=d, queries=q)
    assert ds.metadata.name.startswith("pinecone_dataset_")
    assert isinstance(ds, Dataset)
    assert ds.queries.shape[0] == 2
    assert ds.documents.shape[0] == 2
    assert ds.metadata.dense_model.dimension == 3
    pd_assert_frame_equal(ds.documents, d)
    pd_assert_frame_equal(ds.queries, q)


def test_fails_save_name_not_match(tmpdir):
    dataset_name = "test_io_dataset"
    dataset_path = tmpdir.mkdir(dataset_name)
    ds = Dataset.from_pandas(documents=d, queries=q)
    caught_exception = None
    with pytest.raises(ValueError) as e:
        ds.to_path(str(dataset_path))


def test_io(tmpdir):
    dataset_name = "test_io_dataset"
    dataset_path = tmpdir.mkdir(dataset_name)
    metadata = DatasetMetadata(
        name=dataset_name,
        created_at="2021-01-01 00:00:00.000000",
        documents=2,
        queries=2,
        dense_model=DenseModelMetadata(
            name="ada2",
            dimension=2,
        ),
    )
    ds = Dataset.from_pandas(documents=d, queries=q, metadata=metadata)
    ds.to_path(str(dataset_path))
    loaded_ds = Dataset.from_path(str(dataset_path))
    assert loaded_ds.metadata == metadata
    pd_assert_frame_equal(loaded_ds.documents, ds.documents)
    pd_assert_frame_equal(loaded_ds.queries, ds.queries)


def test_io_no_queries(tmpdir):
    dataset_name = "test_io_dataset_no_q"
    dataset_path = tmpdir.mkdir(dataset_name)
    metadata = DatasetMetadata(
        name=dataset_name,
        created_at="2021-01-01 00:00:00.000000",
        documents=2,
        queries=0,
        dense_model=DenseModelMetadata(
            name="ada2",
            dimension=2,
        ),
    )
    ds = Dataset.from_pandas(documents=d, queries=None, metadata=metadata)

    assert ds.queries.empty
    assert [_ for _ in ds.iter_queries()] == []

    ds.to_path(str(dataset_path))

    loaded_ds = Dataset.from_path(str(dataset_path))
    with pytest.warns(UserWarning):
        print(loaded_ds.queries)

    assert loaded_ds.metadata == metadata
    pd_assert_frame_equal(loaded_ds.documents, ds.documents)

    assert loaded_ds.queries.empty
    assert [_ for _ in loaded_ds.iter_queries()] == []


def test_io_access_to_forbidden_functions():
    dataset_name = "forbidden_functions_dataset"
    metadata = DatasetMetadata(
        name=dataset_name,
        created_at="2021-01-01 00:00:00.000000",
        documents=2,
        queries=2,
        dense_model=DenseModelMetadata(
            name="ada2",
            dimension=2,
        ),
    )
    ds = Dataset.from_pandas(documents=d, queries=q, metadata=metadata)

    with pytest.raises(DatasetInitializationError):
        ds._safe_read_from_path(data_type="documents")

    with pytest.raises(DatasetInitializationError):
        ds._is_datatype_exists(data_type="documents")
