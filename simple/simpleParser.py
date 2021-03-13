
import pandas as pd
import numpy as np
import json
import sys
import jsonlines

# You need to have access to GQA's scene graphs to run this code. 
def parseGraphs(scene_graphs_data):
    graphs = []
    for name, row in (scene_graphs_data.T.iterrows()):
        graphs.append({ name: row.to_dict()['objects'] })
    
    return graphs

# Transform a single graph to a list of all the object relationships
def scene_graph_to_relations_pairs(scene_graph): 
    scene_graph_id = list(scene_graph.keys())[0]  
    scene_graph_objects = scene_graph[scene_graph_id]
    scene_graph_objects_items = [obj_key for obj_key in scene_graph_objects]
    labels = [('{}-{}'.format(scene_graph_objects[obj_key]['name'], obj_key)) for obj_key in scene_graph_objects]

    scene_graph_relations = {}

    for item in scene_graph_objects_items:
        current_item = scene_graph_objects[item]
        attributes = current_item['attributes']
        for related_objects in current_item['relations']:
            attribute = ''
            if (len(attributes) >= 1):
                attribute = '{}'.format(np.random.choice(attributes))
            pair = (scene_graph_objects_items.index(item),scene_graph_objects_items.index(related_objects['object']))
            if attribute == '':
                scene_graph_relations[(labels[pair[0]], labels[pair[1]])] = related_objects['name']
            else:
                scene_graph_relations[('{} {}'.format(attribute, labels[pair[0]]), labels[pair[1]])] = related_objects['name']
    return { scene_graph_id: scene_graph_relations }

# Transform all scene graphs into list of simple sentences
def scene_graphs_to_sentences(scene_graphs):
    scene_graphs_relations_pairs = [scene_graph_to_relations_pairs(graph) for graph in scene_graphs]

    scene_graphs_sentences = []
    for scene_graph_pairs in scene_graphs_relations_pairs:
        scene_graph_id = list(scene_graph_pairs.keys())[0]
        scene_graph_sentences = []
        for pair in scene_graph_pairs[scene_graph_id]:
            item_a, item_b = pair
            relation = scene_graph_pairs[scene_graph_id][pair]
            sentence = 'The {} {} the {}'.format(item_a, relation, item_b)
            scene_graph_sentences.append(sentence)
        scene_graphs_sentences.append({'id': scene_graph_id, 'sentences': scene_graph_sentences})

    return scene_graphs_sentences

if __name__ == "__main__":

    # GQA scene graphs route
    scene_graphs_file = sys.argv[2]

    # output file .jsonlines file
    output_file = sys.argv[3]

    scene_graphs = []
    with open(scene_graphs_file, 'r') as graphs_file:
        scene_graphs_data = pd.read_json(graphs_file)

    scene_graphs = parseGraphs(scene_graphs_data)
    
    scene_graphs_sentences = scene_graphs_to_sentences(scene_graphs)

    with open(output_file, 'w') as fp:
        with jsonlines.Writer(fp) as writer:
            for scene_graph_sentences in scene_graphs_sentences:
                writer.write(json.dumps(scene_graph_sentences))
