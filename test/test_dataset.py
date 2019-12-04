import unittest

from dataset import Dataset, map_dataset


class TestMapDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = Dataset()

    def test_map_dataset(self):
        """Given data and an empty dataset, the dataset is populated with data."""
        data = dict(
            id='bae3d41e-a06e-4d70-9c41-86bb89814fc1',
            title='Social Security Administration (SSA) Enterprise Data Inventory (EDI)',
            metadata_created='2019-12-03T23:31:39.018162',
            metadata_modified='2019-12-03T23:31:39.041053',
            author=None,
            author_email=None,
            state='active',
            type='dataset',
        )

        dataset = self.dataset
        map_dataset(dataset, data)

        assert 'title' in dataset
        assert dataset['title'] == data['title']


    def test_map_dataset_with_no_theme(self):
        """Given data with an empty theme and an empty dataset, the dataset is populated with data."""
        data = dict(
            id='bae3d41e-a06e-4d70-9c41-86bb89814fc1',
            title='Social Security Administration (SSA) Enterprise Data Inventory (EDI)',
            metadata_created='2019-12-03T23:31:39.018162',
            metadata_modified='2019-12-03T23:31:39.041053',
            author=None,
            author_email=None,
            state='active',
            type='dataset',
            theme=None,
        )

        dataset = self.dataset
        map_dataset(dataset, data)

        assert 'title' in dataset
        assert dataset['title'] == data['title']
