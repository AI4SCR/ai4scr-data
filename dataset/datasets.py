"""Base class implementation and MixIns"""

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional


class CacheMixIn:
    """Cache MixIn provides caching functionalities.

    Provides functionalities for caching processed data. Caching requires to set the `cache_path` attribute. Use the
    following functions to work with cached versions of your data:

    Attributes:
        cache_root: path to caching root

    """
    cache_root: Union[str, Path] = None

    def __init__(self, **kwargs):
        self.cache_root = Path(self.cache_root)
        super().__init__(**kwargs)

    def load_cache(self, fname):
        """loads pickled data from cache

        Args:
            fname: file name to which the data is saved

        Returns:
            the loaded data
        """
        with open(self.cache_root / fname, 'rb') as f:
            data = pickle.load(f)
        return data

    def save_cache(self, data, fname) -> None:
        """

        Args:
            data: data that should be saved
            fname: saves pickled data to cache

        Returns:
            None
        """
        with open(self.cache_root / fname, 'wb') as f:
            pickle.dump(data, f)

    def has_cache(self, fname) -> bool:
        """checks whether a cached file exits

        Args:
            fname: filename that should be checked for existing cache

        Returns:

        """
        return (self.cache_root / fname).is_file()

    def get_cache_path(self, fname) -> Path:
        """return cache path

        Args:
            fname: filename for which to return the caching path

        Returns:
            Path
        """
        return self.cache_root / fname


class DownloadMixIn:
    """Download MixIn provides functionalities to download the data.

    Attributes:
        url: URL from which the data can be downloaded
        path: path to which the downloaded file should be save to
        force_download: whether to force re-downloading the file if it already exists

    """

    url = None
    path = None
    force_download = False

    def __init__(self, **kwargs):
        """Download the file.

        Upon initialisation the file is automatically downloaded if it does not exist.
        """
        super().__init__(**kwargs)

        if self.force_download or not self.path.is_file():
            self.download()

    def download(self):
        """Download raw dataset form url"""
        if self.path.parent.is_dir():
            self._download_progress(self.path, self.url)
        else:
            raise ValueError(f'{self.path.parent} is not a valid path to a directory')

    @staticmethod
    def _download_progress(fpath: Path, url):
        from tqdm import tqdm
        from urllib.request import urlopen, Request
        blocksize = 1024 * 8
        blocknum = 0

        try:
            with urlopen(Request(url, headers={"User-agent": "dataset-user"})) as rsp:
                total = rsp.info().get("content-length", None)
                with tqdm(
                        unit="B",
                        unit_scale=True,
                        miniters=1,
                        unit_divisor=1024,
                        total=total if total is None else int(total)
                ) as t, fpath.open('wb') as f:
                    block = rsp.read(blocksize)
                    while block:
                        f.write(block)
                        blocknum += 1
                        t.update(len(block))
                        block = rsp.read(blocksize)
        except (KeyboardInterrupt, Exception):
            # Make sure file doesn’t exist half-downloaded
            if fpath.is_file():
                fpath.unlink()
            raise


class RecipeMixIn:
    """Recipe MixIn provides functionalities to create differently processed versions of the raw data

    Attributes:
        recipes: Dict of recipes registered with the :meth:`register_recipe` decorator
        recipe: the recipe to use for loading the data
        force_process: whether to force re-processing of the raw data

    """
    recipes = dict()
    recipe = None
    force_process = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_recipe_fn(self):
        return self.recipes[self.recipe]

    @classmethod
    def register_recipe(cls, name):
        def register_named_recipe(recipe):
            cls.recipes[name] = recipe
            return recipe

        return register_named_recipe


class BaseDataset(ABC):
    """Base dataset class

    A lightweight wrapper that implements loading data from a path and iterating over it. In general it its preferred
    to have :attr:`path` to point to a single file (potentially a archive) that is used in the :meth:`setup` to prepare
    iteration over the samples.

    Attributes:
        path: path to raw file
    """
    path = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup()

    @abstractmethod
    def __getitem__(self, index):
        """return samples at index"""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """return length of dataset"""
        pass

    @abstractmethod
    def setup(self):
        """Setup the dataset

        This could includes anything that is required to make the data accessible with the __getitem__ method.
        This could be unzipping or loading in memory.
        """
        return


class AI4SCRDataset(BaseDataset, DownloadMixIn, CacheMixIn, RecipeMixIn):
    """Prototye for a in memory dataset with caching, recipe and download support.

    Attributes:
        url: URL from which the data can be downloaded
        module: module / project to which the dataset belongs to. Dataset will be cached in a child folder of the cache_root with module name
        cache_root: path to caching root
    """

    url = None
    module = None
    cache_root = Path('~/.ai4scr/datasets').expanduser()

    def __init__(self,
                 path: Optional[Union[Path, str]] = None,
                 recipe: Optional[str] = None,
                 recipe_kwargs: Optional[dict] = None,
                 force_download: bool = False,
                 force_process: bool = False):
        """Initialise dataset

        Args:
            path: path to which the raw data should be downloaded, defaults to `cache_root / module / {classname}_raw`
            recipe: the recipe to use for loading the data
            recipe_kwargs: kwargs forwarded to the recipe function
            force_download: whether to force re-downloading the file if it already exists
            force_process: whether to force re-processing of the raw data
        """

        if recipe is not None and recipe not in self.recipes:
            raise KeyError(f'No recipe {recipe} registert. Use the RecipeMixIn.register_recipe() decorator to register '
                           f'functions as recipes.')

        self.recipe = recipe
        self.recipe_kwargs = recipe_kwargs if recipe_kwargs else {}

        # modify cache_root and create directory hierarchy
        self.cache_root = self.cache_root / self.module
        self.cache_root.mkdir(parents=True, exist_ok=True)

        # set dataset name to classname
        self.dataset_name = self.__class__.__name__

        # adjust path of raw data file to the cache location if not given
        if path:
            if not self.path.is_file():
                raise FileNotFoundError(f'File {self.path} does not exist.')
            self.path = path
        else:
            self.path = self.get_cache_path(self.dataset_name + '_raw')

        self.force_download = force_download
        self.force_process = force_process

        # initialise empty data
        self.data = None
        super().__init__()

    @abstractmethod
    def process_raw_data(self):
        """Processes raw data saved at :attr:`path`

        Returns:
            Processed raw data
        """
        return

    @abstractmethod
    def __getitem__(self, index):
        """return samples at index"""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """return length of dataset"""
        pass

    def load_raw_data(self):
        fname = self.dataset_name
        if self.force_download or self.force_process or not self.get_cache_path(fname).is_file():
            if self.force_download:
                self.download()

            data = self.process_raw_data()
            self.save_cache(data, fname)
        else:
            data = self.load_cache(fname)
        return data

    def load_recipe_data(self):
        fname = self.get_recipe_filename(self.recipe)
        if self.force_process or not self.has_cache(fname):
            data = self.load_raw_data()
            data = self.get_recipe_fn()(data, **self.recipe_kwargs)
            self.save_cache(data, fname)
        else:
            data = self.load_cache(fname)
        return data

    def setup(self):
        if self.recipe:
            data = self.load_recipe_data()
        else:
            data = self.load_raw_data()
        self.data = data

    def get_recipe_filename(self, recipe):
        return f'{self.dataset_name}_{recipe}.pkl'
