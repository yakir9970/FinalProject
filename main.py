import xml.etree.ElementTree as ET
import requests

# prefix = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


class treeObject:
    def __init__(self,data,parent=None):
        self.data=data
        #maybe turn into set() to add new child and merge if already exists
        self.children=[]
        self.parent=parent


def addNode(graph, data):
    for node in graph.children:
        if data == node.data:
            return node
    newNode = treeObject(data,graph)
    graph.children.append(newNode)
    return newNode

def printTree(graph, level=0):
    # Use the level parameter to keep track of the depth of the node in the tree
    # and print appropriate number of spaces to create an indent
    indent = " " * level * 2
    if graph.parent is not None:
        print(f"{indent}{level} - {graph.data}")
    else:
        print(f"{indent}{level} - {graph.data}")
    for node in graph.children:
        # Recursively call the function with the level increased by 1
        printTree(node, level=level+1)
    return




# def printTree(graph):
#     if graph.parent is not None:
#         print(graph.data + " parent: " + graph.parent.data)
#     for node in graph.children:
#         printTree(node)
#     return

def getXML(url):
    xmlSet=[]
    xmlTree = getSiteMap(url)
    prefix = xmlTree.tag.split("}")[0] + "}"
    domain = xmlTree.find(prefix+'sitemap').find(prefix+'loc').text[8:].split('/', 1)[0]
    urlTree = treeObject(domain)  # this saves the domain: www.cynergy.app to be the root of the tree

    for sitemap in xmlTree.findall(prefix + 'sitemap'):
        loc = sitemap.find(prefix+'loc').text
        if(loc.endswith('.xml')):
            xmlSet.append(loc)

    for xml in xmlSet:
        makeTree(urlTree,getSiteMap(xml))

    return urlTree
def getSiteMap(url):
    response = requests.get(url, stream=True)
    return ET.fromstring(response.content)

def makeTree(urlTree, xmlTree):
    urlSet=[]
    # tree = ET.parse("test.xml")
    # root = tree.getroot()
    prefix = xmlTree.tag.split("}")[0] + "}"
 #iterate all url tags and add loc to a set
    for url in xmlTree.findall(prefix+'url'):
        loc = url.find(prefix+'loc').text
        urlSet.append(loc)

    for loc in urlSet:
        #domain = loc[8:].split('/',1)[0] # this saves the domain: www.cynergy.app
        counter = loc[8:].count('/') # this saves the amount of '/' in the url to know how many levels are in this url's tree
        node = urlTree
        for i in range(1, counter):
            node = addNode(node,loc[8:].split('/',counter)[i])
# def find_differences(node1, node2, path=[]):
#     differences = []
#     if node1.data != node2.data:
#         differences.append(path + [node1.data] + [('value', node1.data, node2.data)])
#     if len(node1.children) != len(node2.children):
#         differences.append(path + [node1.data] + [('number of children', len(node1.children), len(node2.children))])
#     # else:
#     for i, (child1, child2) in enumerate(zip(node1.children, node2.children)):
#         differences.extend(find_differences(child1, child2, path))
#     return differences


def get_tree_nodes(node, nodes):
    nodes.append(node)
    for child in node.children:
        get_tree_nodes(child, nodes)
    return nodes

# def find_tree_differences(old_tree, new_tree):
#     added, removed = [], []
#
#     def helper(old_tree, new_tree, path):
#         nonlocal added, removed
#         old_children_data = {node.data for node in old_tree.children}
#         new_children_data = {node.data for node in new_tree.children}
#
#         added_nodes = [node for node in new_tree.children if node.data not in old_children_data]
#         removed_nodes = [node for node in old_tree.children if node.data not in new_children_data]
#
#         for node in added_nodes:
#             if node not in added:
#                 added.append((path + [node], node))
#         for node in removed_nodes:
#             if node not in removed:
#                 removed.append((path + [node], node))
#
#         for node1, node2 in zip(old_tree.children, new_tree.children):
#             if node1.data == node2.data:
#                 helper(node1, node2, path + [node1])
#
#     helper(old_tree, new_tree, [old_tree])
#
#     return added, removed

def find_tree_differences(old_tree, new_tree):
    added, removed = [], []

    def helper(old_tree, new_tree, path):
        nonlocal added, removed
        old_children_data = {node.data for node in old_tree.children}
        new_children_data = {node.data for node in new_tree.children}

        added_nodes = [node for node in new_tree.children if node.data not in old_children_data]
        removed_nodes = [node for node in old_tree.children if node.data not in new_children_data]

        for node in added_nodes:
            if node not in added:
                added.append((path + [node], node))
        for node in removed_nodes:
            if node not in removed:
                removed.append((path + [node], node))

        for node in old_tree.children:
            matching_nodes = [n for n in new_tree.children if n.data == node.data]
            if matching_nodes:
                helper(node, matching_nodes[0], path + [node])

    helper(old_tree, new_tree, [old_tree])

    return added, removed


class xmlToObject:
    # xmlSet=[]
    #
    # prefix='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    # #need to make it generic for all cases
    #
    # url = "https://www.cynergy.app/sitemap_index.xml"
    # urlTree = getXML(url)
    # printTree(urlTree)
    #
    # url2 = "https://seocrawl.com/sitemap_index.xml"
    # urlTree2 = getXML(url2)
    # printTree(urlTree2)
    #
    # tree = ET.parse('test.xml')
    # root = tree.getroot()
    #
    # for sitemap in root.findall(prefix+'sitemap'):
    #     loc = sitemap.find(prefix+'loc').text
    #     if(loc.endswith('.xml')):
    #         xmlSet.append(loc)
    # #print(xmlSet)
    # urlTree = treeObject(url[8:].split('/', 1)[0])  # this saves the domain: www.cynergy.app to be the root of the tree
    #
    # for xml in xmlSet:
    #     getXML(xml)
    #     makeTree(urlTree)
    # test1 = getXML('XML Sitemap.xml')
    # test2 = getXML('XML Sitemap2.xml')

    # urlTree = treeObject(xmlTree[0][0].text[8:].split('/', 1)[0])  # this saves the domain: www.cynergy.app to be the root of the tree
    # makeTree(urlTree)

    # printTree(urlTree)
    # makeTree(urlTree,'XML Sitemap.xml')

    # tree = ET.parse('XML Sitemap2.xml')
    # root = tree.getroot()
    #
    # for sitemap in root.findall(prefix + 'sitemap'):
    #     loc = sitemap.find(prefix + 'loc').text
    #     if (loc.endswith('.xml')):
    #         xmlSet.append(loc)
    # print(xmlSet)
    # urlTree2 = treeObject(url[8:].split('/', 1)[0])  # this saves the domain: www.cynergy.app to be the root of the tree

    # for xml in xmlSet:
    #     getXML(xml)
    #     makeTree(urlTree2)

    # makeTree(urlTree2,'XML Sitemap2.xml')

    # printTree(urlTree)
    #
    # printTree(urlTree2)

    # print('--------------------')
    #
    # for child in urlTree.children:
    #     print(child.data + ' parent: ' + urlTree.data)

    #testing comparison
    testTree = treeObject('1')
    testTree.children.append(treeObject('5',testTree))
    # testTree.children.append(treeObject('3',testTree))
    testTree.children.append(treeObject('4',testTree))
    # testTree.children[0].children.append(treeObject('10',testTree.children[0]))
    # testTree.children[0].children.append(treeObject('6',testTree.children[0]))
    # testTree.children[0].children.append(treeObject('7',testTree.children[0]))
    # testTree.children[0].children[0].children.append(treeObject('11',testTree.children[0].children[0]))
    #printTree(testTree)

    testTree2 = treeObject('1')
    # testTree2.children.append(treeObject('5', testTree2))
    testTree2.children.append(treeObject('12', testTree2))
    testTree2.children.append(treeObject('5', testTree2))
    # testTree2.children[0].children.append(treeObject('2', testTree2.children[0]))
    # testTree2.children[0].children.append(treeObject('9', testTree2.children[0]))
    # testTree2.children[0].children.append(treeObject('7', testTree2.children[0]))
    # testTree2.children[0].children[0].children.append(treeObject('8', testTree2.children[0].children[0]))
    # printTree(testTree2)

    added, removed = find_tree_differences(testTree,testTree2)

    print('-----------------------')
    print("\033[1m"+"\033[4m"+"Added: "+"\033[0m")
    for path, node in added:
        node_data = node.data
        print("\nAdded node with data:", node_data)
        print("Path: ", end=" ")
        for i in range(len(path)-1):
            print(path[i].data+" -> ", end=" ")
        print(path[len(path)-1].data, end=" ")

    print("\n\n\033[1m"+"\033[4m"+"Removed: "+"\033[0m")
    for path, node in removed:
        node_data = node.data
        print("\nRemoved node with data:", node_data)
        print("Path: ", end=" ")
        for i in range(len(path)-1):
            print(path[i].data + " -> ", end=" ")
        print(path[len(path)-1].data, end=" ")
