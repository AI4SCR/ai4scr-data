import pickle
from abc import ABC, abstractmethod
from pathlib import Path

class CacheMixIn:
    cache_root = None

    def __init__(self, **kwargs):
        self.cache_root = Path(self.cache_root)
        super().__init__(**kwargs)

    def load_cache(self, fname):
        """load and return cached raw data"""
        with open(self.cache_root / fname, 'rb') as f:
            data = pickle.load(f)
        return data

    def save_cache(self, data, fname):
        """save processed raw data"""
        with open(self.cache_root / fname, 'wb') as f:
            pickle.dump(data, f)

    def has_cache(self, fname):
        """Check if dataset is cached"""
        return (self.cache_root / fname).is_file()

    def get_cache_path(self, fname):
        """Check if dataset is cached"""
        return self.cache_root / fname


class DownloadMixIn:
    url = None
    path = None
    force_download = False

    def __init__(self, **kwargs):
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
    path = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup()

    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def setup(self):
        """Setup the loading of the dataset
        This could includes anything that is required to make the data accessible with the __getitem__ method.
        This could be unzipping or loading in memory.
        """
        return


class AI4SCRDataset(BaseDataset, DownloadMixIn, CacheMixIn, RecipeMixIn):
    """Prototye for a in memory dataset with caching, recipe and download support"""

    url = None
    module = None
    cache_root = Path('~/.ai4scr/datasets').expanduser()

    def __init__(self, path=None, recipe=None, recipe_kwargs=None, force_download=False, force_process=False):

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

