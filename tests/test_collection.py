import unittest
from collection import catalog_record, validate_edit, safe_image, save_edit, collection_metrics


class CollectionTests(unittest.TestCase):
    def metric_item(self, identity='X', quantity=1, set_name='Base', **extra):
        return dict(catalog_id=identity, quantity=quantity, set_name=set_name, wishlist=False, **extra)

    def test_metrics_empty_collection(self):
        self.assertEqual(collection_metrics([]), dict(copies=0, distinct=0, sets=0, duplicates=0, wishlist=0))

    def test_metrics_zero_quantity_is_not_owned(self):
        item = self.metric_item(quantity=0)
        item['wishlist'] = True
        self.assertEqual(collection_metrics([item]), dict(copies=0, distinct=0, sets=0, duplicates=0, wishlist=1))

    def test_metrics_multiple_copies(self):
        self.assertEqual(collection_metrics([self.metric_item(quantity=4)]),
                         dict(copies=4, distinct=1, sets=1, duplicates=3, wishlist=0))

    def test_metrics_aggregate_identity_across_variants(self):
        items = [self.metric_item(quantity=2, language='English', condition='Near Mint', variant='Holo'),
                 self.metric_item(quantity=1, language='Japanese', condition='Damaged', variant='Regular')]
        self.assertEqual(collection_metrics(items), dict(copies=3, distinct=1, sets=1, duplicates=2, wishlist=0))

    def test_metrics_multiple_sets_and_unknown_set(self):
        items = [self.metric_item('X', 2, 'Base'), self.metric_item('Y', 1, 'Base'),
                 self.metric_item('Z', 3, 'Jungle'), self.metric_item('W', 0, 'Fossil'),
                 self.metric_item('U', 1, '  '), self.metric_item('V', 1, ' Base ')]
        self.assertEqual(collection_metrics(items), dict(copies=8, distinct=5, sets=2, duplicates=3, wishlist=0))

    def test_catalog_does_not_import_private_or_untrusted_fields(self):
        record = catalog_record({'id': 'smp-SM211', 'name': 'Charizard', 'user_id': 'attacker', 'quantity': 100,
                                 'images': {'small': 'javascript:alert(1)'}}, 'owner')
        self.assertEqual(record['user_id'], 'owner')
        self.assertEqual(record['image_url'], '')
        self.assertNotIn('quantity', record)

    def test_image_hosts(self):
        self.assertTrue(safe_image('https://assets.tcgdex.net/en/sm/smp/SM211/low.webp'))
        self.assertFalse(safe_image('https://assets.tcgdex.net.attacker.test/card.png'))

    def test_wishlist_can_have_zero_owned_copies(self):
        values = validate_edit(0, 'Not assessed', ' English ', '', '', True)
        self.assertEqual(values['quantity'], 0)
        self.assertTrue(values['wishlist'])
        self.assertEqual(values['language'], 'English')

    def test_invalid_edits(self):
        for quantity in (-1, 10000, True, 1.5):
            with self.assertRaises(ValueError):
                validate_edit(quantity, 'Near Mint', '', '', '', False)
        with self.assertRaises(ValueError):
            validate_edit(1, 'Near Mint', '', '', 'a' * 2001, False)

    def test_update_is_scoped_to_owner_and_entry(self):
        class Client:
            def __init__(self): self.filters = []
            def table(self, name): return self
            def update(self, values): return self
            def eq(self, key, value): self.filters.append((key, value)); return self
            def execute(self): return self
        client = Client()
        save_edit(client, 'owner', 'entry', {'quantity': 2})
        self.assertEqual(client.filters, [('user_id', 'owner'), ('id', 'entry')])


if __name__ == '__main__':
    unittest.main()
