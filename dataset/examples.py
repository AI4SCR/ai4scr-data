from pathlib import Path

import pandas as pd

from .datasets import AI4SCRDataset, BaseDataset, DownloadMixIn, RecipeMixIn, CacheMixIn


class SimpleInMemoryDataset(BaseDataset):
    path = Path('~/tmp/test.csv').expanduser()
    data = None

    def __getitem__(self, index):
        return self.data.iloc[index]

    def __len__(self):
        return len(self.data)

    def setup(self):
        self.data = pd.read_csv(self.path)


class SimpleDiskDataset(BaseDataset):
    path = Path('~/tmp/bs345.tar.gz').expanduser()
    files = None

    def __getitem__(self, index):
        data = []
        for i in index:
            f = self.files[i]
            with open(f, 'r') as f:
                data.append(f.readlines())
        return data

    def __len__(self):
        return len(self.files)

    def setup(self):
        import tarfile

        with tarfile.open(self.path, 'r:gz') as tar:
            tar.extractall(self.path.parent)
            p = self.path.parent / 'bs345'
            self.files = list(p.glob('*.txt'))


class SimpleDownloadDataset(SimpleInMemoryDataset, DownloadMixIn):
    url = 'http://ml-flow.tracking.zc2.ibm.com:8000/data.csv'

    def __init__(self, path: str = Path('~/tmp/download_data.csv').expanduser()):
        self.path = path  # set path before calling super as this is consumed by the mixin
        super().__init__()


class SimpleCacheDataset(SimpleInMemoryDataset, CacheMixIn):
    cache_root = Path('~/tmp/cache/').expanduser()

    def setup(self):
        fname = self.path.name.split('.')[0] + '.pkl'
        if self.has_cache(fname):
            self.data = self.load_cache(fname)
        else:
            super().setup()
            self.save_cache(self.data, fname)


class SimpleRecipe(SimpleInMemoryDataset, RecipeMixIn):

    def __init__(self, recipe = None):
        self.recipe = recipe
        super().__init__()

    def setup(self):
        super().setup()
        if self.recipe:
            self.data = self.get_recipe_fn()(self.data)

    @staticmethod
    @RecipeMixIn.register_recipe('default')
    def recipe_default(data):
        data['age'] = data.age + 1
        return data


class DB(AI4SCRDataset):
    url = 'http://ml-flow.tracking.zc2.ibm.com:8000/data.csv'
    module = 'drug-interaction'

    def __getitem__(self, index):
        return self.data.iloc[index]

    def __len__(self):
        return len(self.data)

    def process_raw_data(self):
        return pd.read_table(self.path, sep=';')

    @staticmethod
    @RecipeMixIn.register_recipe('default')
    def recipe_default(data):
        """

        Args:
            data: raw data as loaded by process_raw_data
            **kwargs:

        Returns:

        """
        data['age'] = data.age + 1
        return data
