#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements
# pylint: disable=protected-access

import unittest
import json

import fw.config.manage as config_manage
import fw_tests.config as test_configs

CONFIG_1_0_0 = {
    '@api': {
        'type': 'jconf',
        'name': 'TestConfig',
        'version': '1.0.0',
        'prev_version': None
    },
    '@config_id': 'testing',
    'root': {
        'id': '001',
        'child_nodes': [
            {
                'id': '002',
                'child_nodes': [
                    {
                        'id': '003'
                    }
                ]
            },
            {
                'id': '004',
                'child_nodes': [
                    {
                        'id': '005',
                        'child_nodes': [
                            {
                                'id': '006',
                                'child_nodes': [
                                    {
                                        'id': '007'
                                    }
                                ]
                            },
                            {
                                'id': '008'
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

CONFIG_1_0_1 = {
    '@api': {
        'type': 'jconf',
        'name': 'TestConfig',
        'version': '1.0.1',
        'prev_version': '1.0.0'
    },
    '@config_id': 'testing',
    'root': {
        'id': '001',
        'content': [
            {
                'id': '002',
                'content': [
                    {
                        'id': '003'
                    }
                ]
            },
            {
                'id': '004',
                'content': [
                    {
                        'id': '005',
                        'content': [
                            {
                                'id': '006',
                                'content': [
                                    {
                                        'id': '007'
                                    }
                                ]
                            },
                            {
                                'id': '008'
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

CONFIG_1_1_0 = {
    '@api': {
        'type': 'jconf',
        'name': 'TestConfig',
        'version': '1.1.0',
        'prev_version': '1.0.1'
    },
    '@config_id': 'testing',
    'root': '001',
    'nodes': {
        '001': {
            'id': '001',
            'content': [
                '002',
                '004'
            ]
        },
        '002': {
            'id': '002',
            'content': [
                '003'
            ]
        },
        '003': {
            'id': '003'
        },
        '004': {
            'id': '004',
            'content': [
                '005'
            ]
        },
        '005': {
            'id': '005',
            'content': [
                '006',
                '008'
            ]
        },
        '006': {
            'id': '006',
            'content': [
                '007'
            ]
        },
        '007': {
            'id': '007'
        },
        '008': {
            'id': '008'
        }
    }
}


class TestConfigManage(unittest.TestCase):

    def test_01_register_config_package(self):
        import fw.config
        configs = config_manage.get_config_types()
        self.assertEqual({}, configs)
        config_manage.register_config_package(fw.config,
            include_names=['FileTree'])
        type_keys = ['FileTree']
        config_keys = list(configs.keys())
        config_keys.sort()
        self.assertEqual(type_keys, config_keys)

        config_manage.remove_all_config_types()
        self.assertEqual({}, configs)
        config_manage.register_config_package(fw.config)
        type_keys = [
            'FileTree',
            'GitRepo',
            'WsgiApps',
            'WsgiServer'
        ]
        config_keys = list(configs.keys())
        config_keys.sort()
        self.assertEqual(type_keys, config_keys)

    def test_02_get_config_versions(self):
        config_manage.register_config_package(test_configs)
        versions = config_manage.get_config_versions('TestConfig')
        self.assertEqual(versions, ['1.0.0', '1.0.1', '1.1.0'])

    def _latest_version(self, versions, match):
        self.assertEqual(config_manage.get_latest_version(versions), match)

    def test_03_get_latest_version(self):
        self._latest_version([], None)
        self._latest_version(['0'], '0')
        self._latest_version(['0.0.0'], '0.0.0')
        self._latest_version(['123'], '123')
        self._latest_version(['1', '1'], '1')
        self._latest_version(['2.1', '2.2'], '2.2')
        self._latest_version(['3.0.4.10', '3.0.4.2'], '3.0.4.10')
        self._latest_version(['3.0.4.10', '3.0.4.1'], '3.0.4.10')
        self._latest_version(['4.08', '4.08.01'], '4.08.01')
        self._latest_version(['3.2.1.9.8144', '3.2'], '3.2.1.9.8144')
        self._latest_version(['3.2', '3.2.1.9.8144'], '3.2.1.9.8144')
        self._latest_version(['5.6.7', '5.6.7'], '5.6.7')
        self._latest_version(['1.01.1', '1.1.1'], '1.1.1')
        self._latest_version(['1', '1.0'], '1.0')
        self._latest_version(['1.0.2.0', '1.0.2'], '1.0.2')
        self._latest_version(['1.0.2', '1.0.2.0'], '1.0.2.0')
        self._latest_version(['1.1.0', '1.1.1', '1.1.2'], '1.1.2')
        self._latest_version(['1.1.1', '1.1.2', '1.1.0'], '1.1.2')
        self._latest_version(['1.1.2', '1.1.0', '1.1.1'], '1.1.2')
        self._latest_version(['1-0', '1'], '1-0')
        self._latest_version(['1.1-0', '1'], '1.1-0')
        self._latest_version(['1.1.1-0', '1'], '1.1.1-0')
        self._latest_version(['1.1.1-0', '1.1.2'], '1.1.2')
        self._latest_version(['1.1.1-1', '1.1.1-2', '1.1.1-3'], '1.1.1-3')
        self._latest_version(['1.1.1-2', '1.1.1-3', '1.1.1-1'], '1.1.1-3')
        self._latest_version(['1.1.1-3', '1.1.1-1', '1.1.1-2'], '1.1.1-3')

    def test_04a_get_new_config(self):
        config = config_manage.create_new_config('WsgiServer',
            type_version='1.0.0')
        self.assertEqual(config['@api']['name'], 'WsgiServer')
        self.assertEqual(config['@api']['version'], '1.0.0')
        self.assertEqual(config['@api']['prev_version'], None)
        self.assertEqual(config['server']['address'], 'localhost')
        self.assertEqual(config['server']['port'], 9000)
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_04b_get_new_config(self):
        config = config_manage.create_new_config('TestConfig',
            type_version='1.0.0')
        self.assertEqual(config['@api']['name'], 'TestConfig')
        self.assertEqual(config['@api']['version'], '1.0.0')
        self.assertEqual(config['@api']['prev_version'], None)
        self.assertEqual(config['root'], {})
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_04c_get_new_config(self):
        config = config_manage.create_new_config('TestConfig',
            type_version='1.0.1')
        self.assertEqual(config['@api']['name'], 'TestConfig')
        self.assertEqual(config['@api']['version'], '1.0.1')
        self.assertEqual(config['@api']['prev_version'], '1.0.0')
        self.assertEqual(config['root'], {})
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_04d_get_new_config(self):
        config = config_manage.create_new_config('TestConfig',
            type_version='1.1.0')
        self.assertEqual(config['@api']['name'], 'TestConfig')
        self.assertEqual(config['@api']['version'], '1.1.0')
        self.assertEqual(config['@api']['prev_version'], '1.0.1')
        self.assertEqual(config['root'], '001')
        self.assertEqual(config['nodes']['001'], {'id': '001'})
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_04e_get_new_config_with_overrides(self):
        overrides = {
            '@config_id': 'Foobar123',
            'root': '002',
            'nodes': {
                '002': {
                    'id': '002',
                    'content': [
                        '002'
                    ]
                }
            }
        }
        config = config_manage.create_new_config('TestConfig',
            overrides=overrides)
        self.assertEqual(config['@api']['name'], 'TestConfig')
        self.assertEqual(config['@api']['version'], '1.1.0')
        self.assertEqual(config['@api']['prev_version'], '1.0.1')
        self.assertEqual(config['root'], '002')
        self.assertEqual(config['nodes']['001'], {'id': '001'})
        self.assertEqual(config['nodes']['002']['id'], '002')
        self.assertEqual(config['nodes']['002']['content'], ['002'])
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)
        # Verify that the overrides variable have not been modified.
        self.assertEqual(overrides.get('@api'), None)
        self.assertEqual(overrides['nodes'].get('001'), None)

    def test_05_validate_config_ok(self):
        result = config_manage.validate_config(CONFIG_1_0_0)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

        result = config_manage.validate_config(CONFIG_1_0_1)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

        result = config_manage.validate_config(CONFIG_1_1_0)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_06a_validate_config_config_api(self):
        config = {
            '@api': {
                # Missing config type.
                'name': 'TestConfig',
                'version': '1.0.0',
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "'type' is a required property")

    def test_06b_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                # Missing config name.
                'version': '1.0.0',
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Config api type name missing.')

    def test_06c_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'FooBar',  # Unregistered config type.
                'version': '1.0.0',
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Config api type not registered: "FooBar"')

    def test_06d_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                # Missing version.
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Config api version missing.')

    def test_06e_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': 'foobar',  # Incorrect version format.
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Illegally formatted config api version: "foobar"')

    def test_06f_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.0.0',
                # Missing previous version.
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Config api previous version missing.')

    def test_06g_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.0.0',
                'prev_version': 'foobar'
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Illegally formatted config api previous version: "foobar"')

    def test_06h_validate_config_config_api(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.2.3',  # Non-registered version.
                'prev_version': None
            },
            '@config_id': 'testing',
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            'Config api version not registered: "1.2.3"')

    def test_07a_validate_config_missing_item(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.0.0',
                'prev_version': None
            },
            '@config_id': 'testing'
            # Missing required item 'root'.
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "'root' is a required property"
        )

    def test_07b_validate_config_missing_item(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.1.0',
                'prev_version': '1.0.1'
            },
            '@config_id': 'testing'
            # Missing required item 'root'.
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "'root' is a required property"
        )

    def test_07c_validate_config_missing_item(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.1.0',
                'prev_version': '1.0.1'
            },
            # Missing required item '@config_id'.
            'root': {}
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "'@config_id' is a required property"
        )

    def test_08a_validate_config_incorrect_items(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.1.0',
                'prev_version': '1.0.1'
            },
            '@config_id': 'testing',
            'root': '001',
            'nodes': {
                '002': {
                    'id': '002',
                    'content': [
                        '003'
                    ]
                },
                'foobar': {
                    'id': 'foobar'
                }
            }
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "Additional properties are not allowed ('foobar' was unexpected)"
        )

    def test_08b_validate_config_incorrect_items(self):
        config = {
            '@api': {
                'type': 'jconf',
                'name': 'TestConfig',
                'version': '1.1.0',
                'prev_version': '1.0.1'
            },
            '@config_id': 'testing',
            'root': '001',
            'nodes': {
                '002': {
                    'id': '002',
                    'content': [
                        '003'
                    ]
                },
                '003': {
                    'id': '003',
                    'content': [
                        'foobar'
                    ]
                }
            }
        }
        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0].message,
            "'foobar' does not match '^[0-9]{3}$'"
        )

    def test_09_get_version_chain(self):
        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.0', latest_version='1.0.1')
        self.assertEqual(chain, [('1.0.0', '1.0.1')])

        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.0', latest_version='1.1.0')
        self.assertEqual(chain, [('1.0.0', '1.0.1'), ('1.0.1', '1.1.0')])

        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.1', latest_version='1.1.0')
        self.assertEqual(chain, [('1.0.1', '1.1.0')])

    def test_10_update_1_0_0_to_1_0_1(self):
        config = _copy_config(CONFIG_1_0_0)
        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.0', latest_version='1.0.1')
        before = json.dumps(config, sort_keys=True)
        config_manage.update_config(config, chain)
        after = json.dumps(config, sort_keys=True)
        correct = json.dumps(CONFIG_1_0_1, sort_keys=True)
        self.assertNotEqual(before, after)
        self.assertEqual(after, correct)

        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_11_update_1_0_1_to_1_1_0(self):
        config = _copy_config(CONFIG_1_0_1)
        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.1', latest_version='1.1.0')
        before = json.dumps(config, sort_keys=True)
        config_manage.update_config(config, chain)
        after = json.dumps(config, sort_keys=True)
        correct = json.dumps(CONFIG_1_1_0, sort_keys=True)
        self.assertNotEqual(before, after)
        self.assertEqual(after, correct)

        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_12_update_1_0_0_to_1_1_0(self):
        config = _copy_config(CONFIG_1_0_0)
        before = json.dumps(config, sort_keys=True)
        config_manage.update_config(config)
        after = json.dumps(config, sort_keys=True)
        correct = json.dumps(CONFIG_1_1_0, sort_keys=True)
        self.assertNotEqual(before, after)
        self.assertEqual(after, correct)

        result = config_manage.validate_config(config)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['errors']), 0)

    def test_13_update_missing_method(self):
        config = _copy_config(CONFIG_1_0_0)
        chain = config_manage.get_version_chain('TestConfig',
            target_version='1.0.0', latest_version='1.1.0')
        chain.append(('1.1.0', '1.1.1'))
        self.assertRaisesRegex(Exception,
            r'Config update failed! Config type: TestConfig, config version: 1.0.0.',
            config_manage.update_config, config, chain)


def _copy_config(config):
    return json.loads(json.dumps(config))


if __name__ == '__main__':
    unittest.main()
