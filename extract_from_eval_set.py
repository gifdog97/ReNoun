from renoun import *

import matplotlib.pyplot as plt

import time
import pickle

df = pd.read_csv("./data/openie_eval_200221_GG.csv")

sentences_en = df['Sentence_en']

# seed fact extraction
seed_fact_list = []
for sentence in sentences_en:
    doc = NLP(sentence)
    seed_fact_list.append(extract_seed_fact(doc))

# with open ("./data/seed_fact_list.pickle", 'wb') as f:
#     pickle.dump(seed_fact_list, f)

# with open ("./data/seed_fact_list.pickle", 'rb') as f:
#     seed_fact_list = pickle.load(f)

seed_fact_list = [seed_fact[0] for seed_fact in seed_fact_list if seed_fact != []]
seed_fact_list = list(set(seed_fact_list))

print(len(seed_fact_list))
print(seed_fact_list)
att_patt_graph = nx.Graph()

# extraction pattern generation
for sentence in sentences_en:
    doc = NLP(sentence)

    # TODO: 本当は seed_fact そのものでなく、Aは完全一致、S, O は freebase_id が一致していればOK
    for seed_fact in seed_fact_list:
        attribute = seed_fact[1]
        if attribute not in doc.text:
            continue
        single_patt_set, A = dependency_pattern_generation(doc, seed_fact)
        for s_pat in list(single_patt_set):
            generated_patt_list = []

            for node_k, node_v in dict(att_patt_graph.nodes).items():
                if node_v['bipartite'] == 1:
                    generated_patt_list.append(node_k)

            found_same = False
            for g_pat in generated_patt_list:
                # 1週目は generated_patt_set が attribute の set になる
                if type(g_pat) == type(""):
                    break 
                # 同じ構造のグラフが含まれているかチェック
                # 素朴な add_edges では失敗する（Graph()クラスの性質上、同じ構造のグラフ G, Hについて G != H となるため）
                if dict(s_pat.edges) == dict(g_pat.edges):
                    found_same = True
                    att_patt_graph.add_node(A, bipartite=0)
                    att_patt_graph.add_edge(A, g_pat)
                    break
            if (not found_same):
                att_patt_graph.add_node(A, bipartite=0)
                att_patt_graph.add_node(s_pat, bipartite=1)
                att_patt_graph.add_edge(A, s_pat)

# with open ("./data/att_patt_graph.pickle", 'wb') as f:
#     pickle.dump(att_patt_graph, f)

# with open ("./data/att_patt_graph.pickle", 'rb') as f:
#     att_patt_graph = pickle.load(f)

# 抽出した delexicalized tree の図示
"""
for patt_k, patt_v in dict(att_patt_graph.nodes).items():
    if patt_v['bipartite'] == 1:
        nx.draw_networkx(patt_k)
        plt.show()
"""

# candidate generation
for i, sentence in enumerate(sentences_en, 1):
    doc = NLP(sentence)
    found_sao = candidate_generation(doc, att_patt_graph)

