import argparse
from scipy.spatial import cKDTree

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from opencmiss.utils.zinc.finiteelement import getMaximumNodeIdentifier, getMaximumElementIdentifier
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.utils.zinc.field import findOrCreateFieldCoordinates


def create_middle_nodes(zinc_file):
    """
    Create middle nodes in cubic hermite mesh. Loop over each line and create a middle node. repeat it for the faces
    and elements
    :param zinc_file:
    :return:
    """
    context = Context('create_middle_nodes')
    region = context.getDefaultRegion()
    region.readFile(zinc_file)
    field_module = region.getFieldmodule()
    coordinates = field_module.findFieldByName('coordinates').castFiniteElement()
    lung_coordinates = field_module.findFieldByName('lung coordinates').castFiniteElement()
    nodes = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    mesh1d = field_module.findMeshByDimension(1)
    mesh2d = field_module.findMeshByDimension(2)
    mesh3d = field_module.findMeshByDimension(3)

    fieldcache = field_module.createFieldcache()
    fieldcache2 = field_module.createFieldcache()

    # create a node template with 2 coordinate fields
    nodetemplate = nodes.createNodetemplate()
    nodetemplate.defineField(coordinates)
    nodetemplate.defineField(lung_coordinates)
    nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
    nodetemplate.setValueNumberOfVersions(lung_coordinates, -1, Node.VALUE_LABEL_VALUE, 1)

    nodeIdentifier = max(1, getMaximumNodeIdentifier(nodes) + 1)
    # get element iterator for line, face and element and loop over each element and add a middle point
    for mesh in [mesh1d, mesh2d, mesh3d]:
        elementiterator = mesh.createElementiterator()
        element = elementiterator.next()
        if mesh.getDimension() == 1:
            xi_list = [0.5]
        elif mesh.getDimension() == 2:
            xi_list = [[0.5, 0.5]]
        else:
            xi_list = [[0.5, 0.5, 0.5]]
        while element.isValid():
            print(element.getIdentifier())
            # create the middle nodes where at least one xi is 0.5 in one of the directions
            for xi in xi_list:
                # get coordinates at xi
                fieldcache2.setMeshLocation(element, xi)
                result, x = coordinates.evaluateReal(fieldcache2, coordinates.getNumberOfComponents())
                result, x_lc = lung_coordinates.evaluateReal(fieldcache2, lung_coordinates.getNumberOfComponents())
                # create a node at x
                node = nodes.createNode(nodeIdentifier, nodetemplate)
                fieldcache.setNode(node)
                coordinates.setNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                lung_coordinates.setNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, x_lc)
                nodeIdentifier += 1
            element = elementiterator.next()

    # get all the nodes and create a kd tree
    points = []
    points2 = []
    node_ids = []
    node_iterator = nodes.createNodeiterator()
    node = node_iterator.next()
    while node.isValid():
        fieldcache.setNode(node)
        result, x = coordinates.evaluateReal(fieldcache, coordinates.getNumberOfComponents())
        result, x_lc = lung_coordinates.evaluateReal(fieldcache, lung_coordinates.getNumberOfComponents())
        if node.getIdentifier() not in [136, 137, 138, 139]:
            points.append(x)
            points2.append(x_lc)
            node_ids.append(node.getIdentifier())
        node = node_iterator.next()

    tree = cKDTree(points)
    elementiterator = mesh3d.createElementiterator()
    element = elementiterator.next()

    xis = [0.0, 0.5, 1.0]
    xi_list = [[x, y, z] for z in xis for y in xis for x in xis]
    elem_node_lists = []
    # element_ids
    # get node identifiers for each element
    while element.isValid():
        elem_node_list = []
        for xi in xi_list:
            fieldcache.setMeshLocation(element, xi)
            result, x = coordinates.evaluateReal(fieldcache, coordinates.getNumberOfComponents())
            dist, idx = tree.query(x)
            elem_node_list.append(node_ids[idx])
        elem_node_lists.append(elem_node_list)
        element = elementiterator.next()

    # fielditer = field_module.createFielditerator()
    # field = fielditer.next()
    # while field.isValid():
    #     field_name = field.getName()
    #     if 'marker' in field_name.lower():
    #         if 'name' in field_name.lower():
    #             marker_name = field_name
    #         elif 'location' in field_name.lower():
    #             marker_location_name = field_name
    #         elif '.' not in field_name:
    #             marker_group_name = field_name
    #     field = fielditer.next()
    # if all([marker_name, marker_location_name, marker_group_name]):
    #     return marker_location_name, marker_name, marker_group_name
    # else:
    #     raise AssertionError('Could not find marker fields')

    return node_ids, points, points2, elem_node_lists


def create_quad_lagrange_elements(node_ids, points, points2, elem_node_lists):
    """
    Read the zinc file which includes the middle nodes and create quadratic lagrange elements.

    *** Not sure why 1D mesh and 2D mesh do not return the nodes - I am going to use closest point to generate
    the elements
    :param node_ids: list of node identifiers corresponding to points
    :param points: list of coordinates.
    :param points2: list of lung coordinates.
    :param elem_node_lists: list of node identifiers for each element
    :return:
    """
    context = Context('create_elements')
    region = context.getDefaultRegion()
    field_module = region.getFieldmodule()
    coordinates = findOrCreateFieldCoordinates(field_module, name="coordinates")
    lung_coordinates = findOrCreateFieldCoordinates(field_module, name="lung coordinates")
    nodes = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    mesh3d = field_module.findMeshByDimension(3)

    fieldcache = field_module.createFieldcache()

    nodetemplate = nodes.createNodetemplate()
    nodetemplate.defineField(coordinates)
    nodetemplate.defineField(lung_coordinates)
    nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
    nodetemplate.setValueNumberOfVersions(lung_coordinates, -1, Node.VALUE_LABEL_VALUE, 1)

    for node_id, point, point2 in zip(node_ids, points, points2):
        node = nodes.createNode(node_id, nodetemplate)
        fieldcache.setNode(node)
        coordinates.setNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, point)
        lung_coordinates.setNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, point2)

    # create quadratic lagrange 3d mesh
    quadratic_lagrange_basis = field_module.createElementbasis(3, Elementbasis.FUNCTION_TYPE_QUADRATIC_LAGRANGE)
    eft = mesh3d.createElementfieldtemplate(quadratic_lagrange_basis)
    elementtemplate = mesh3d.createElementtemplate()
    elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    result = elementtemplate.defineField(coordinates, -1, eft)
    result = elementtemplate.defineField(lung_coordinates, -1, eft)

    elementIdentifier = 1
    for elem_node_list in elem_node_lists:
        element = mesh3d.createElement(elementIdentifier, elementtemplate)
        element.setNodesByIdentifier(eft, elem_node_list)
        elementIdentifier += 1

    field_module.defineAllFaces()
    region.writeFile('lung_quad_lagrange7.exf')


if __name__ == "__main__":
    ar = argparse.ArgumentParser()
    ar.add_argument('-f', '--file', help='Input file')
    args = vars(ar.parse_args())

    node_ids, points, points2, elem_node_lists = create_middle_nodes(args['file'])
    create_quad_lagrange_elements(node_ids, points, points2, elem_node_lists)



