import unittest
from client.dict_builder import DictionaryBuilder, _ensure_empty_paths
import logging
logging.basicConfig(level=logging.DEBUG)

class DictionaryBuilderTests(unittest.TestCase):

    def test_add(self):
        result = DictionaryBuilder(inherit={'meta': {'old_attr': "value"}}, add=["meta.attr=something="])
        self.assertEqual("something=", result['meta']['attr'])
        self.assertEqual("value", result['meta']['old_attr'])

    def test_add_nested_none_can_be_overwritten(self):
        result = DictionaryBuilder(inherit={'meta': None}, add=["meta.parent.child=something"])
        self.assertEqual("something", result['meta']['parent']['child'])

    def test_add_nested(self):
        result = DictionaryBuilder(inherit={'meta': {'key': 'value'}}, add=["meta.parent.child=something"])
        self.assertEqual("something", result['meta']['parent']['child'])
        self.assertEqual("value", result['meta']['key'])

    def test_add_already_existing_value_can_be_overwritten(self):
        result = DictionaryBuilder(inherit={'meta': {'old_attr': "value"}}, add=["meta.old_attr=something"])
        self.assertEqual("something", result['meta']['old_attr'])

    def test_add_can_not_overwrite_string_value_with_dictionary(self):
        with self.assertRaises(RuntimeError):
            DictionaryBuilder(inherit={'meta': {'old_attr': "value"}}, add=["meta.old_attr.new_type.new=something"])

    def test_add_can_not_overwrite_list_value_with_dictionary(self):
        with self.assertRaises(RuntimeError):
            DictionaryBuilder(inherit={'meta': ["item"]}, add=["meta.attr=new"])

    def test_delete(self):
        result = DictionaryBuilder(inherit={'meta': {'attr': "orig"}}, delete=["meta.attr"])
        self.assertNotIn('attr', result['meta'])

    def test_delete_does_not_exist_works(self):
        DictionaryBuilder(inherit={'meta': {'attr': "orig"}}, delete=["meta.attr_not_exist"])

    def test_delete_parent(self):
        result = DictionaryBuilder(inherit={'meta': {'attr': "orig"}, 'feta': "foobar"}, delete=["meta"])
        self.assertNotIn("meta", result.data.keys())

    def test_delete_parent_does_not_exist_works(self):
        DictionaryBuilder(inherit={'meta': {'attr': "orig"}}, delete=["meta_does_not_exist"])

    def test_append(self):
        result = DictionaryBuilder(inherit={'meta': {'attr': ["orig"]}}, append=["meta.attr=modified"])
        self.assertEqual(result['meta']['attr'], ["orig", "modified"])

    def test_append_nested(self):
        result = DictionaryBuilder(inherit={'meta': {'key': 'value'}}, append=["meta.attr.new=list_item"])
        self.assertEqual(result['meta']['attr']['new'], ["list_item"])
        self.assertEqual(result['meta']['key'], "value")

    def test_append_target_is_not_list(self):
        with self.assertRaises(Exception):
            DictionaryBuilder(inherit={'meta': {'attr': "orig"}}, append=["meta.attr=modified"])

    def test_append_target_does_not_exist(self):
        result = DictionaryBuilder(inherit={'meta': {}}, append=["meta.attr=modified"])
        self.assertEqual(result['meta']['attr'], ["modified"])

    def test_append_target_is_none(self):
        result = DictionaryBuilder(inherit={'meta': {'attr': None}}, append=["meta.attr=modified"])
        self.assertEqual(result['meta']['attr'], ["modified"])

    def test_get_modified_dict(self):
        expected_result = {'items': ["1","2","3","4","5","6"]}
        result = DictionaryBuilder(inherit={'items': ["1", "2", "3", "4", "5"]}, append=["items=6"])
        self.assertDictEqual(result.data, expected_result)

    def test_get_modified_dict_exclude_meta_fields(self):
        expected_result = {'items': ["1","2","3","4","5","6"]}
        result = DictionaryBuilder(inherit={'items': ["1", "2", "3", "4", "5"], '_id': "12345", '_created': "7876768768"}, append=["items=6"], exclude_meta=True)
        self.assertDictEqual(result.data, expected_result)

    def test_ensure_empty_paths(self):
        expected_result = {'meta': {
                                'parent': {
                                    'child': None},
                                'other-parent': "foobar",
                                },

                            'other': "stay"
                           }
        my_d = {'meta': {'other-parent': "foobar"}, 'other': "stay"}
        _ensure_empty_paths(my_d, ["meta", "parent", "child"])
        self.assertDictEqual(expected_result, my_d)


if __name__ == '__main__':
    unittest.main()
