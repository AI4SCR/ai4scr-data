from .data import DataSet

class MyData(DataSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):
        pass

    def recipe_adriano(self):
        pass