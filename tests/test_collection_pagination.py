from types import SimpleNamespace
import unittest
from collection import load_collection_items, collection_metrics


class PageClient:
    def __init__(self, rows, cap=500):
        self.rows, self.cap, self.offsets, self.filters = rows, cap, [], []
    def table(self, name): return self
    def select(self, fields): return self
    def eq(self, field, owner):
        self.filters.append((field, owner))
        return self
    def order(self, field): return self
    def range(self, start, end):
        self.offsets.append(start)
        self.start, self.end = start, min(end + 1, start + self.cap)
        return self
    def execute(self): return SimpleNamespace(data=self.rows[self.start:self.end])


class CollectionPaginationTests(unittest.TestCase):
    def test_large_collection_survives_server_page_cap(self):
        rows = [dict(id=str(i), user_id='owner', catalog_id='same-card', quantity=1,
                     set_name='Base', wishlist=False) for i in range(1201)]
        client = PageClient(rows, cap=100)
        result = load_collection_items(client, 'owner')
        self.assertEqual(result, rows)
        self.assertEqual(client.offsets[-1], 1201)
        self.assertTrue(all(pair == ('user_id', 'owner') for pair in client.filters))
        self.assertEqual(collection_metrics(result)['duplicates'], 1200)

    def test_empty_and_exact_full_page(self):
        for count in (0, 500):
            rows = [dict(id=str(i)) for i in range(count)]
            self.assertEqual(load_collection_items(PageClient(rows), 'owner'), rows)

    def test_repeated_page_or_wrong_owner_fails_closed(self):
        for rows in ([{'id': 'one'}, {'id': 'one'}], [{'id': 'one', 'user_id': 'other'}]):
            with self.assertRaises(ValueError):
                load_collection_items(PageClient(rows), 'owner')

    def test_partial_failure_does_not_return_partial_collection(self):
        client = PageClient([{'id': 'one'}], cap=1)
        execute = client.execute
        def fail_second_page():
            if client.start: raise RuntimeError('offline')
            return execute()
        client.execute = fail_second_page
        with self.assertRaises(RuntimeError): load_collection_items(client, 'owner')
