from .dataset import Dataset
from .catalog import Catalog
from . import cfg

catalog = None


def list_datasets(as_df=False) -> list:
    """
    List all datasets in the catalog, optionally as a pandas DataFrame.
    Catalog is set using the `PINECONE_DATASETS_EDNPOINT` environment variable.

    Args:
        as_df (bool, optional): Whether to return the list as a pandas DataFrame. Defaults to False.

    Returns:
        list: A list of dataset names; or
        df: A pandas DataFrame of dataset names and metadata

    Example:

        ```python
        from pinecone_datasets import list_datasets
        list_datasets() # -> ['dataset1', 'dataset2', ...]
        list_datasets(as_df=True) # -> pandas DataFrame of dataset names and metadata
        ```

    """
    global catalog
    catalog = Catalog.load()
    return catalog.list_datasets(as_df=as_df)


def load_dataset(dataset_id: str, **kwargs) -> Dataset:
    """
    Load a dataset from the catalog

    Args:
        dataset_id (str): The name of the dataset to load
        **kwargs: Additional keyword arguments to pass to the Dataset constructor, e.g. `engine='polars'`

    Returns:
        Dataset: A Dataset object

    Example:

        ```python
        from pinecone_datasets import load_dataset
        dataset = load_dataset("dataset_name")
        ```
    """
    if not catalog:
        raise ValueError(
            "Catalog not initialized. Please call pinecone_datasets.load_catalog() first."
        )
    if dataset_id not in catalog.list_datasets(as_df=False):
        raise FileNotFoundError(f"Dataset {dataset_id} not found in catalog")
    else:
        return Dataset(dataset_id, should_load_metadata=True, **kwargs)
