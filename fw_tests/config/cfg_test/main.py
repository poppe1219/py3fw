"""Test config, to test conversion methods."""

CONFIG_TYPE = 'TestConfig'


def update_1_0_0_to_1_0_1(config):
    """Update from version 1.0.0 to 1.0.1."""
    api = config['@api']
    api['version'] = '1.0.1'
    api['prev_version'] = '1.0.0'
    _traverse_1_0_0(config['root'])
    return config


def _traverse_1_0_0(item):
    """Help method for updating from 1.0.0 to 1.0.1."""
    if 'child_nodes' in item.keys():
        for child_node in item['child_nodes']:
            _traverse_1_0_0(child_node)
        item['content'] = item['child_nodes']
        del item['child_nodes']


def update_1_0_1_to_1_1_0(config):
    """Update from version 1.0.1 to 1.1.0."""
    api = config['@api']
    api['version'] = '1.1.0'
    api['prev_version'] = '1.0.1'
    root_id = config['root']['id']
    nodes = {}
    nodes[root_id] = config['root']
    _traverse_1_0_1(config['root'], nodes)
    config['root'] = root_id
    config['nodes'] = nodes
    return config


def _traverse_1_0_1(item, nodes):
    """Help method for updating from 1.0.1 to 1.1.0."""
    if 'content' in item.keys():
        ids = []
        for node in item['content']:
            nodes[node['id']] = node
            ids.append(node['id'])
            _traverse_1_0_1(node, nodes)
        item['content'] = ids
