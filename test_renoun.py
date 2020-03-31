from renoun import *

import time

sentences = [
"the CEO of Google, Larry Page started his term in 2011, when he succeeded Eric Schmidt.",
"the CEO of Google is Larry Page, who started his term in 2011, when he succeeded Eric Schmidt.",
"Larry Page, Google CEO started his term in 2011, when he succeeded Eric Schmidt.",
"Larry Page, Google’s CEO started his term in 2011, when he succeeded Eric Schmidt.",
"Larry Page, CEO of Google, started his term in 2011, when he succeeded Eric Schmidt.",
"Larry Page, the CEO of Google, started his term in 2011, when he succeeded Eric Schmidt.",
"Google CEO Larry Page started his term in 2011, when he succeeded Eric Schmidt.",
"Google CEO, Larry Page started his term in 2011, when he succeeded Eric Schmidt.",
"Google’s CEO, Larry Page started his term in 2011, when he succeeded Eric Schmidt."
]

seed_fact_list = []
for sentence in sentences:
    doc = NLP(sentence)
    try:
        seed_fact_list += extract_seed_fact(doc)
    except re.error:
        continue

seed_fact_list = list(set(seed_fact_list))

att_patt_graph = nx.Graph()

for sentence in sentences:
    doc = NLP(sentence)

    for seed_fact in seed_fact_list:
        attribute = seed_fact[1]
        if attribute not in doc.text:
            continue
        single_patt_set, A = dependency_pattern_generation(doc, seed_fact)
        att_patt_graph.add_node(A, bipartite=0)
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

for i, sentence in enumerate(sentences, 1):
    doc = NLP(sentence)
    found_sao = candidate_generation(doc, att_patt_graph)
    print(found_sao)

# 適当に単語を変えてうまく行くとは限らない
# 依存構造が変わる（謎の依存構造が抽出されている: npadvmod）
# noun_list の取得漏れ

sentences = [
"the CEO of Facebook, Mark Zuckerberg started his term in 2011, when he succeeded Eric Schmidt.",
"the CEO of Facebook is Mark Zuckerberg, who started his term in 2011, when he succeeded Eric Schmidt.",
"Mark Zuckerberg, Facebook CEO started his term in 2011, when he succeeded Eric Schmidt.",
"Mark Zuckerberg, Facebook’s CEO started his term in 2011, when he succeeded Eric Schmidt.",
"Mark Zuckerberg, CEO of Facebook, started his term in 2011, when he succeeded Eric Schmidt.",
"Mark Zuckerberg, the CEO of Facebook, started his term in 2011, when he succeeded Eric Schmidt.",
"Facebook CEO Mark Zuckerberg started his term in 2011, when he succeeded Eric Schmidt.",
"Facebook CEO, Mark Zuckerberg started his term in 2011, when he succeeded Eric Schmidt.",
"Facebook’s CEO, Mark Zuckerberg started his term in 2011, when he succeeded Eric Schmidt."
]

for i, sentence in enumerate(sentences, 1):
    doc = NLP(sentence)
    found_sao = candidate_generation(doc, att_patt_graph)
    print(found_sao)
