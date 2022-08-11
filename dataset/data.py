import os
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import request

from .typing import Optional, PathLike, Callable, get_args, List, Union

ROOT = Path('~/.ai4scr/datasets/').expanduser()
ROOT.mkdir(parents=True, exist_ok=True)

class DataSet(ABC):
    """Generic dataset class. Manages download of raw data and supports different ways of processing the raw data
    based on so called `recipes`."""

    def __init__(self,
                 name: str,
                 module: str,
                 url: str,
                 extension: Optional[str] = None,
                 description: Optional[str] = None,
                 path: Optional[PathLike] = None):
        """Generic dataset class.

        Args:
            name: name of the dataset used to store the raw data
            module: name of the module that is used to create this dataset
            url: download url for raw data
            extension: extension of downloaded file
            description: description of the dataset
            path: directory path where the raw and processed files should be stored

        Notes:

        """

        self.name = self._standardize_names(name)
        self.module = self._standardize_names(module)
        self.url = url
        self.extension = extension if extension[0] == '.' else '.' + extension
        self.description = description

        if path is None:
            path = ROOT / self.module
            path.mkdir(parents=True, exist_ok=True)
        else:
            path = Path(path)
        self.path = path

        self.fpath = self.path / (self.name + self.extension)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, get_args(PathLike)):
            if Path(value).is_dir():
                self._path = Path(value)
                self.fpath = self.path / (self.name + self.extension)  # update fpath
            else:
                raise ValueError(f'provided path {value} is not a directory.')
        else:
            raise TypeError(f'trying to set path to type {type(value)}.')

    def has_cache_raw(self):
        """Check if dataset is cached"""
        return os.path.isfile(self.fpath)

    def has_cache_recipe(self, recipe: str):
        """Check if processed dataset is cached"""
        return os.path.isfile(self.get_rpath(recipe))

    def get_rpath(self, recipe: str):
        """Get file path of processed dataset recipe"""
        return self.path / f'{self.name}_recipe_{recipe}.pkl'

    def get_rfunc(self, recipe: str):
        """Get processing function for recipe"""
        func = getattr(self, f'recipe_{recipe}', None)
        if None:
            raise AttributeError(f'please implement a function called `recipe_{recipe}` to enable raw data processing.')
        elif isinstance(func, Callable):
            return func
        else:
            raise TypeError(f'{recipe} is of type {type(func)}. Should be type {type(Callable)}')

    def download(self):
        """Download raw dataset form url"""
        if self.fpath.parent.is_dir():
            self._download_progress(self.fpath, self.url)
        else:
            raise ValueError(f'{self.fpath} is not a valid directory')

    def get_data(self, recipe: Optional[str] = None, force_reload=False, **kwargs):
        if recipe is None:
            return self.get_raw_data(force_reload)
        else:
            return self.get_recipe_data(recipe, force_reload, **kwargs)

    def get_recipe_data(self, recipe: str, force_reload=False, **kwargs):
        if force_reload or not self.has_cache_recipe(recipe):
            return self.process(recipe, **kwargs)
        else:
            return self.rload(recipe)

    def get_raw_data(self, force_reload=False):
        if force_reload or not self.has_cache_raw():
            self.download()
        return self.load()

    def process(self, recipe: str, **kwargs):
        """handles processing of raw data for different recipes"""
        func = self.get_rfunc(recipe)
        raw_data = self.get_raw_data()
        data = func(raw_data, **kwargs)
        self.rsave(data, recipe)
        return data

    def __repr__(self):
        if self.description is None:
            repr = f'Dataset("{self.name}")\ncached at {self.path})'
        else:
            repr = f'Dataset("{self.name}")\n{self.description}\ncached at {self.path})'
        return repr

    @abstractmethod
    def load(self):
        """load and return raw data as downloaded"""
        return None

    @abstractmethod
    def rload(self, recipe):
        """load and return cached recipe"""
        return None

    @abstractmethod
    def rsave(self, data, recipe):
        """save processed raw data"""
        pass

    @abstractmethod
    def recipe_default(self, raw_data, **kwargs):
        """Example recipe. Return a processed version of the raw data

        Args:
            raw_data: the raw data as returned by the `load` function
            **kwargs: kwargs for processing, can be passed from :meth:`get_data`

        Returns:
            processed data in a customer defined format

        Examples:
            Assuming the raw data comes as a :class:`~pandas.DataFrame`

            .. code-block:: python

            data = defaultdict(dict)
            data['targets'] = raw_data[['Y']]
            data['inputs'] = raw_data[['X']]

        """
        return data

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


    @staticmethod
    def _standardize_names(names: Union[List[str], str]):
        """replace white spaces with underscore and convert to lower"""
        def standardize_name(name: str):
            return '_'.join(name.lower().split())

        if isinstance(names, list):
            names = [standardize_name(i) for i in names]
        elif isinstance(names, str):
            names = standardize_name(names)
        else:
            raise TypeError(f'{names} should be of type str or List[str]')
        return names