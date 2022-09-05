Quickstart
----------
.. py:currentmodule:: dataset.datasets

.. code-block:: python

    data = MyDataset()
    sample = data[0]
    N = len(data)

Subclass the :class:`~BaseDataset` to create your own dataset class. The dataset should be saved as a single file pointed to
by :attr:`~BaseDataset.path`.

.. autoclass:: BaseDataset
    :members:
    :noindex:

    .. automethod:: __len__
    .. automethod:: __getitem__

To ensure a standardised data access you have to implement :meth:`~BaseDataset.__len__`, :meth:`~BaseDataset.__getitem__`
and :meth:`~BaseDataset.setup`. The :meth:`~BaseDataset.setup` is the core function to process you raw data stored
at :attr:`~BaseDataset.path`.


Simple In-Memory Dataset
^^^^^^^^^^^^^^^^^^^^^^^^
This is a minimal example of a dataset that is loaded from a csv file.
We subclass the :class:`~BaseDataset` and point :attr:`~BaseDataset.path` to the csv file. Next we overwrite the
the :meth:`~BaseDataset.setup` method and implement the loading logic of the dataset. In this case, we decided to store
the loaded dataset in the :attr:`data` attribute.


.. code-block:: python

       class SimpleInMemoryDataset(BaseDataset):
        path = Path('~/test.csv').expanduser()
        data = None

        def __getitem__(self, index):
            return self.data.iloc[index]

        def __len__(self):
            return len(self.data)

        def setup(self):
            self.data = pd.read_csv(self.path)


Simple Out-of-Memory Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class SimpleOutOfMemoryDataset(BaseDataset):
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