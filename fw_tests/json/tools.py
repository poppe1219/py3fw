#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods


import unittest
import json

import fw.json.tools as jsontools

BASE = {
    'id2': 99,
    'id3': 99,
    'id4': 99,
    'name1': "qqq",
    'name2': "qqq",
    'name3': "qqq",
    'name4': "qqq",
    'newList': [
        'qqq',
        99
    ],
    'subAttr1': {
        'value1': False,
        'value2': False,
        'value3': [
            'qqq'
        ],
        'value4': 'qqq',
        'value5': [
            'qqq',
            [
                'aaa',
                'bbb'
            ]
        ]
    },
    'subAttr2': {
        'test1': 'hej',
        'test2': None
    }
}

OVERLAY = {
    'id1': 1,
    'id2': 2,
    'id3': 3,
    'name1': "bleah",
    'name2': None,
    'name3': False,
    'subAttr1': {
        'value1': True,
        'value2': None,
        'value3': [
            'a',
            1,
            False,
            None
        ]
    }
}

MERGED = {
    "id1": 1,
    "id2": 2,
    "id3": 3,
    "id4": 99,
    "name1": "bleah",
    "name2": None,
    "name3": False,
    "name4": "qqq",
    "newList": [
        "qqq",
        99
    ],
    "subAttr1": {
        "value1": True,
        "value2": None,
        "value3": [
            "a",
            1,
            False,
            None
        ],
        "value4": "qqq",
        "value5": [
            "qqq",
            [
                "aaa",
                "bbb"
            ]
        ]
    },
    "subAttr2": {
        "test1": "hej",
        "test2": None
    }
}

MERGED_TEXT = """{
    "id1": 1,
    "id2": 2,
    "id3": 3,
    "id4": 99,
    "name1": "bleah",
    "name2": null,
    "name3": false,
    "name4": "qqq",
    "newList": [
        "qqq",
        99
    ],
    "subAttr1": {
        "value1": true,
        "value2": null,
        "value3": [
            "a",
            1,
            false,
            null
        ],
        "value4": "qqq",
        "value5": [
            "qqq",
            [
                "aaa",
                "bbb"
            ]
        ]
    },
    "subAttr2": {
        "test1": "hej",
        "test2": null
    }
}"""


class TestConfigManage(unittest.TestCase):

    def test_01_deep_copy(self):
        new_overlay = jsontools.deep_copy(OVERLAY)
        new_overlay_string = json.dumps(new_overlay, sort_keys=True)
        overlay_string = json.dumps(OVERLAY, sort_keys=True)
        self.assertEqual(new_overlay_string, overlay_string)

        # Try changing mutable objects to verify that the copy has new objects
        # and not references to the old objects.
        new_overlay['name1'] = 'NewValue'
        self.assertEqual(OVERLAY['name1'], 'bleah')
        self.assertEqual(BASE['name1'], 'qqq')

        new_overlay['subAttr1']['value1'] = 'NewValue'
        self.assertEqual(OVERLAY['subAttr1']['value1'], True)
        self.assertEqual(BASE['subAttr1']['value1'], False)

        new_overlay['subAttr1']['value3'][0] = 'NewValue'
        self.assertEqual(OVERLAY['subAttr1']['value3'][0], 'a')
        self.assertEqual(BASE['subAttr1']['value3'][0], 'qqq')

    def test_02_merge(self):
        new_overlay = jsontools.deep_copy(OVERLAY)
        jsontools.merge(new_overlay, BASE)
        new_overlay_string = json.dumps(new_overlay, sort_keys=True)
        merged_string = json.dumps(MERGED, sort_keys=True)
        self.assertEqual(new_overlay_string, merged_string)

        # Try changing mutable objects to verify that the copy has new objects
        # and not references to the old objects.
        new_overlay['name1'] = 'NewValue'
        self.assertEqual(OVERLAY['name1'], 'bleah')
        self.assertEqual(BASE['name1'], 'qqq')

        new_overlay['subAttr1']['value1'] = 'NewValue'
        self.assertEqual(OVERLAY['subAttr1']['value1'], True)
        self.assertEqual(BASE['subAttr1']['value1'], False)

        new_overlay['subAttr1']['value3'][0] = 'NewValue'
        self.assertEqual(OVERLAY['subAttr1']['value3'][0], 'a')
        self.assertEqual(BASE['subAttr1']['value3'][0], 'qqq')

    def test_03a_loads(self):
        text1 = '{\n    "key": "value"\n}'
        text2 = '{\r\n    "key": "value"\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03b_loads(self):
        text1 = '{\n    "key": "value" // JavaScript single line comment.\n}'
        text2 = '{\r\n    "key": "value" // JavaScript single line comment.\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03c_loads(self):
        text1 = '{\n    // JavaScript single line comment.\n    "key": "value"\n}'
        text2 = '{\r\n    // JavaScript single line comment.\r\n    "key": "value"\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03d_loads(self):
        text1 = '{\n    "key": "value"\n    // JavaScript single line comment.\n}'
        text2 = '{\r\n    "key": "value"\r\n    // JavaScript single line comment.\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03e_loads(self):
        text1 = '// JavaScript single line comment.\n{\n    "key": "value"\n}'
        text2 = '// JavaScript single line comment.\r\n{\r\n    "key": "value"\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03f_loads(self):
        text1 = '{\n    "key": "value" /* JavaScript multiline comment. */\n}'
        text2 = '{\r\n    "key": "value" /* JavaScript multiline comment. */\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03g_loads(self):
        text1 = '{\n    "key": "value" /*\n        JavaScript\n        multiline\n        comment. */\n}'
        text2 = '{\r\n    "key": "value" /*\r\n        JavaScript\r\n        multiline\r\n        comment. */\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03h_loads(self):
        text1 = '{\n    /*\n    JavaScript\n    multiline\n    comment.\n    */\n    "key": "value"\n}'
        text2 = '{\r\n    /*\r\n    JavaScript\r\n    multiline\r\n    comment.\r\n    */\r\n    "key": "value"\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03i_loads(self):
        text1 = '/*\n    JavaScript\n    multiline\n    comment.\n    */\n    {\n    "key": "value"\n}'
        text2 = '/*\r\n    JavaScript\r\n    multiline\r\n    comment.\r\n    */\r\n    {\r\n    "key": "value"\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_03j_loads(self):
        text1 = '/*\n    JavaScript\n    multiline\n    comment.\n    */\n    {\n    "key": "value" // JavaScript single line comment.\n}'
        text2 = '/*\r\n    JavaScript\r\n    multiline\r\n    comment.\r\n    */\r\n    {\r\n    "key": "value" // JavaScript single line comment.\r\n}'
        parsed1 = jsontools.loads(text1)
        parsed2 = jsontools.loads(text2)
        self.assertEqual(parsed1, {"key": "value"})
        self.assertEqual(parsed2, {"key": "value"})

    def test_loads_exception(self):
        text1 = '/*\n    JavaScript\n    multiline\n    comment.\n    */\n    {\n    "key": "value" // JavaScript single line comment.\n}'
        self.assertRaises(ValueError, jsontools.loads, text1, False)

    def test_dumps(self):
        parsed = jsontools.dumps(MERGED)
        self.assertEqual(MERGED_TEXT, parsed)


if __name__ == '__main__':
    unittest.main()
