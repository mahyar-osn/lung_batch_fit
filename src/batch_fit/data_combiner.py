from opencmiss.zinc.context import Context
from opencmiss.zinc.field import FieldGroup
from opencmiss.zinc.result import RESULT_OK
from opencmiss.zinc.field import Field

from opencmiss.utils.zinc.general import ChangeManager
from opencmiss.utils.zinc.general import AbstractNodeDataObject
from opencmiss.utils.zinc.general import create_node as create_zinc_node
from opencmiss.utils.zinc.field import create_field_coordinates, find_or_create_field_group


class Point(AbstractNodeDataObject):

    def __init__(self, x, y, z):
        super(Point, self).__init__(['coordinates'])
        self._x = x
        self._y = y
        self._z = z

    def get(self):
        return [self._x, self._y, self._z]

    def coordinates(self):
        return [self._x, self._y, self._z]

    def __repr__(self):
        return 'x="{0}" y="{1}" z="{2}"'.format(self._x, self._y, self._z)


def write_ex(file_name, data):
    context = Context("Lung Data")
    region = context.getDefaultRegion()
    load(region, data)
    if not isinstance(file_name, str):
        file_name = str(file_name)
    region.writeFile(file_name)


def read_single_group(file_name):
    context = Context('Single Data')
    region = context.getDefaultRegion()
    result = region.readFile(file_name)
    assert result == RESULT_OK, "Failed to load data file " + str(file_name)
    node_parameters = extract_node_parameter(region)
    return node_parameters


def extract_node_parameter(region):
    fieldmodule = region.getFieldmodule()
    coordinates = fieldmodule.findFieldByName('coordinates').castFiniteElement()
    components_count = coordinates.getNumberOfComponents()
    assert components_count in [1, 2, 3], 'extract_node_parameter. Invalid coordinates number of components'
    cache = fieldmodule.createFieldcache()

    return_values = list()
    nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_iter = nodes.createNodeiterator()
    node = node_iter.next()
    while node.isValid():
        cache.setNode(node)
        result, values = coordinates.getNodeParameters(cache, -1, 1, 1, components_count)
        return_values.append(values)
        node = node_iter.next()

    return return_values


def load(region, data):
    field_module = region.getFieldmodule()
    coordinate_filed = create_field_coordinates(field_module)

    for surface, points in data.items():
        node_identifiers = create_nodes(field_module, points)
        create_group_nodes(field_module, surface, node_identifiers, node_set_name='datapoints')


def create_nodes(field_module, embedded_lists, node_set_name='datapoints'):
    node_identifiers = []
    for pt in embedded_lists:
        if isinstance(pt, list):
            node_ids = create_nodes(field_module, pt, node_set_name=node_set_name)
            node_identifiers.extend(node_ids)
        else:
            local_node_id = create_zinc_node(field_module, pt, node_set_name=node_set_name)
            node_identifiers.append(local_node_id)

    return node_identifiers


def create_group_nodes(field_module, group_name, node_ids, node_set_name='datapoints'):
    with ChangeManager(field_module):
        group = find_or_create_field_group(field_module, name=group_name)
        group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)

        nodeset = field_module.findNodesetByName(node_set_name)
        node_group = group.getFieldNodeGroup(nodeset)
        if not node_group.isValid():
            node_group = group.createFieldNodeGroup(nodeset)

        nodeset_group = node_group.getNodesetGroup()
        for group_node_id in node_ids:
            node = nodeset.findNodeByIdentifier(group_node_id)
            nodeset_group.addNode(node)
