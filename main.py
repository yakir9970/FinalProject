import json
import threading
import xml.etree.ElementTree as ET
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from ScopingCrawlerUtils.CrawlerInitiator import CrawlerInitiator

class treeObject:
    def __init__(self, data, parent=None):
        self.data = data
        self.children = []
        self.parent = parent
        self.color = None


def addNode(graph, data):
    for node in graph.children:
        if data == node.data:
            return node
    if data != '':
        newNode = treeObject(data, graph)
        graph.children.append(newNode)
        return newNode


def printTree(graph, level=0):
    indent = " " * level * 2
    if graph.parent is not None:
        print(f"{indent}{level} - {graph.data}")
        if graph.color is not None:
            print(f"{graph.data} - {graph.color}")
    else:
        print(f"{indent}{level} - {graph.data}")
        if graph.color is not None:
            print(f"{graph.data} - {graph.color}")
    for node in graph.children:
        printTree(node, level=level + 1)
    return


def toDict(node):
    result = {
        'data': node.data,
        'color': node.color,
        'children': []
    }
    for child in node.children:
        result['children'].append(toDict(child))
        result['children'][-1]['parent'] = node.data
    return result


def getXML(url):
    xmlSet = []
    xmlTree = getSiteMap(url)
    prefix = xmlTree.tag.split("}")[0] + "}"
    domain = xmlTree.find(prefix + 'sitemap').find(prefix + 'loc').text[8:].split('/', 1)[0]
    urlTree = treeObject(domain)  # this saves the domain: www.cynergy.app to be the root of the tree

    for sitemap in xmlTree.findall(prefix + 'sitemap'):
        loc = sitemap.find(prefix + 'loc').text
        if (loc.endswith('.xml')):
            xmlSet.append(loc)

    for xml in xmlSet:
        makeTree(urlTree, getSiteMap(xml))

    return urlTree


def getSiteMap(url):
    response = requests.get(url, stream=True)
    return ET.fromstring(response.content)


def makeTree(urlTree, xmlTree):
    urlSet = []
    prefix = xmlTree.tag.split("}")[0] + "}"
    # iterate all url tags and add loc to a set
    for url in xmlTree.findall(prefix + 'url'):
        loc = url.find(prefix + 'loc').text
        urlSet.append(loc)

    for loc in urlSet:
        counter = loc[8:].count(
            '/')  # this saves the amount of '/' in the url to know how many levels are in this url's tree
        node = urlTree
        for i in range(0, counter):
            node = addNode(node, loc[8:].split('/', counter)[i + 1])


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
                node.color = '#00b830'
                added.append((path + [node], node))
        for node in removed_nodes:
            if node not in removed:
                node.color = '#bd0606'
                removed.append((path + [node], node))

        for node in old_tree.children:
            matching_nodes = [n for n in new_tree.children if n.data == node.data]
            if matching_nodes:
                helper(node, matching_nodes[0], path + [node])

    helper(old_tree, new_tree, [old_tree])

    return added, removed


def find_feature_diff(old_feature, new_feature):
    old_json_feature = json.loads(old_feature)
    new_json_feature = json.loads(new_feature)
    domain = list(old_json_feature['featuresData'].keys())[0]
    old_features_by_key = {}
    new_features_by_key = {}
    for key in old_json_feature['featuresData'][domain]:
        if "Evidence" not in key:
            if old_json_feature['featuresData'][domain][key] == True:
                old_features_by_key[key] = old_json_feature['featuresData'][domain][key+"Evidence"]
            elif old_json_feature['featuresData'][domain][key] == False:
                old_features_by_key[key] = []
            if new_json_feature['featuresData'][domain][key] == True:
                new_features_by_key[key] = new_json_feature['featuresData'][domain][key+"Evidence"]
            elif new_json_feature['featuresData'][domain][key] == False:
                new_features_by_key[key] = []

    added = {}
    removed = {}
    for key, value in new_features_by_key.items():
        if key in old_features_by_key:
            added[key] = list(set(value) - set(old_features_by_key[key]))
            removed[key] = list(set(old_features_by_key[key]) - set(value))
        else:
            added[key] = value
            removed[key] = []
    for key, value in old_features_by_key.items():
        if key not in new_features_by_key:
            added[key] = []
            removed[key] = value

    return added, removed, new_features_by_key, old_features_by_key


app = Flask(__name__)
CORS(app)

@app.route('/api/upload_files', methods=['POST'])
def upload():
    if request.method == 'POST':
        file1_content = request.files['file1'].read().decode('utf-8')
        file2_content = request.files['file2'].read().decode('utf-8')
        old_tree, new_tree = calculateDiff(file1_content, file2_content)

        old_file_path = 'old-website-feature.txt'
        with open(old_file_path, 'r') as f:
            old_file_contents = f.read()
        new_file_path = 'new-website-feature.txt'
        with open(new_file_path, 'r') as f:
            new_file_contents = f.read()

        added, removed, new_features_by_key, old_features_by_key = find_feature_diff(old_file_contents, new_file_contents)
        return jsonify({'old': old_tree, 'new': new_tree, 'added': added, 'removed': removed, 'new_features_by_key': new_features_by_key, 'old_features_by_key': old_features_by_key})


@app.route('/api/feature', methods=['POST'])
def crawler():
    request_json = request.json
    targets = request_json['targets']
    crawler_obj = CrawlerInitiator(targets, request_json)
    x = threading.Thread(target=crawler_obj.subprocess_main_starter, )
    x.start()
    x.join()
    result = crawler_obj.get_result()
    return jsonify(result)


def calculateDiff(file1_content, file2_content):
    root1 = ET.fromstring(file1_content)
    root2 = ET.fromstring(file2_content)

    prefix1 = root1.tag.split("}")[0] + "}"
    prefix2 = root2.tag.split("}")[0] + "}"

    domain1 = root1.find(prefix1 + 'url').find(prefix1 + 'loc').text[8:].split('/', 1)[0]
    domain2 = root2.find(prefix2 + 'url').find(prefix2 + 'loc').text[8:].split('/', 1)[0]

    urlTree1 = treeObject(domain1)
    makeTree(urlTree1, root1)

    urlTree2 = treeObject(domain2)
    makeTree(urlTree2, root2)

    added, removed = find_tree_differences(urlTree1, urlTree2)

    urlTree1_json = toDict(urlTree1)
    urlTree2_json = toDict(urlTree2)

    return urlTree1_json, urlTree2_json


if __name__ == '__main__':
    app.run(debug=True)
