import xml.etree.ElementTree as ET
import requests
from flask import Flask, jsonify


class treeObject:
    def __init__(self,data,parent=None):
        self.data=data
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
    # tree = ET.parse("test.xml") save for maybe working with files
    # root = tree.getroot()
    prefix = xmlTree.getroot().tag.split("}")[0] + "}"
 #iterate all url tags and add loc to a set
    for url in xmlTree.findall(prefix+'url'):
        loc = url.find(prefix+'loc').text
        urlSet.append(loc)

    for loc in urlSet:
        counter = loc[8:].count('/') # this saves the amount of '/' in the url to know how many levels are in this url's tree
        node = urlTree
        for i in range(0, counter):
            node = addNode(node,loc[8:].split('/',counter)[i+1])



def get_tree_nodes(node, nodes):
    nodes.append(node)
    for child in node.children:
        get_tree_nodes(child, nodes)
    return nodes

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


# class xmlToObject():
app = Flask(__name__)

@app.route('/api/get_changes', methods=['GET'])
def get_changes():
    xmlTree = ET.parse('old.xml')
    prefix = xmlTree.getroot().tag.split("}")[0] + "}"
    domain = xmlTree.find(prefix + 'url').find(prefix + 'loc').text[8:].split('/', 1)[0]
    urlTree = treeObject(domain)  # this saves the domain: www.cynergy.app to be the root of the tree
    makeTree(urlTree,xmlTree)
    printTree(urlTree)

    print('--------------')

    xmlTree2 = ET.parse('new.xml')
    prefix2 = xmlTree2.getroot().tag.split("}")[0] + "}"
    domain2 = xmlTree2.find(prefix2 + 'url').find(prefix2 + 'loc').text[8:].split('/', 1)[0]
    urlTree2 = treeObject(domain2)  # this saves the domain: www.cynergy.app to be the root of the tree
    makeTree(urlTree2, xmlTree2)
    printTree(urlTree2)

    added, removed = find_tree_differences(urlTree,urlTree2)
    data_added = [node[0][-1].data for node in added]
    path_added = [[node.data for node in path[0]] for path in added]
    data_removed = [node[0][-1].data for node in removed]
    path_removed = [[node.data for node in path[0]] for path in removed]

    response = {'added': [data_added, path_added], 'removed': [data_removed,path_removed]}
    return jsonify(response)
    # print('-----------------------')
    # print("\033[1m"+"\033[4m"+"Added: "+"\033[0m")
    # for path, node in added:
    #     node_data = node.data
    #     print("\nAdded node with data:", node_data)
    #     print("Path: ", end=" ")
    #     for i in range(len(path)-1):
    #         print(path[i].data+" -> ", end=" ")
    #     print(path[len(path)-1].data, end=" ")
    #
    # print("\n\n\033[1m"+"\033[4m"+"Removed: "+"\033[0m")
    # for path, node in removed:
    #     node_data = node.data
    #     print("\nRemoved node with data:", node_data)
    #     print("Path: ", end=" ")
    #     for i in range(len(path)-1):
    #         print(path[i].data + " -> ", end=" ")
    #     print(path[len(path)-1].data, end=" ")

if __name__ == '__main__':
    app.run(debug=True)
