# Renoun 実装の詳細、結果のまとめなど

## ディレクトリ構成
- requirements.txt: 必要パッケージ
- renoun.py: 実装本体
- test_renoun.py: サンプルテキストに対する実験
- extract_from_eval_set.py: 評価データからのトリプル抽出
- data: データのディレクトリ
    - open_eval_200211_GG.csv: 評価データ（グーグル翻訳）
    - seed_fact_list.pickle: 評価データから抽出された seed_fact のリスト
    - att_patt_graph.pickle: 各 Attribute と Dependency Pattern の対応関係を示すグラフ
    - result.txt: 評価データからの抽出結果
        - 今回は抽出できた文章がかなり少ないため、抽出できた文章と抽出トリプルの一覧という形式で表示しています

## 実験設定
- 処理の流れ
    1. Seed fact extraction: 単純なルールベースでトリプルを得る
    2. Extraction pattern generaion: 1.で得たトリプルの依存構造木のパターンを得る
    3. Candidate generation: 2.で得たパターンをコーパスに適用し、トリプルの候補を得る。
    4. Scoring: 3.で得た候補をスコアリングする。（今回はデータセットが小さかったので未実装）
- Attribute のデータセットは評価データの中央の語とする
- 抽出パターンを評価データから取った
    + 入力まわりを修正すれば enwiki など大きなデータから取ることもできるはず

## 実験結果のまとめ
- Seed fact の数: 11（文章数1700程度に対して6%程度）
    - 抽出時間: およそ3分
- Extraction pattern の数: 21
    - 抽出時間: およそ1分
- Candidate fact の数: 32
    - 抽出時間: およそ30分
    - 精度に問題はあれど Seed fact で取れなかったものが取れている
- 今回は小さなスケールでの実験であり Attribute のリストも得られた抽出パターンも貧弱ではあったが、Seed fact とは別の新たなトリプルを少し得ることができた。データを増やすことでより良い出力を得られる見込み。

## 実装本体（renoun.py）の詳細、注意点、懸念点など
- 参考として各変数と関数の意味合いを記す。
- Rules: 1.で用いるルール。
- Attributes: トリプルの中央に位置する単語のデータセット。今回は評価データから抽出（size=251）
- NLP: 固有表現抽出や依存構造解析などに使う SpaCy というライブラリのクラス。
- resolution: 単語に Freebase ID を付与（未実装）
    - 論文では、抽出した(S,A,O)のAとOのFreebase ID が一致することが求められているが、そもそも Freebase が現在廃止されていること、今回はデータサイズが小さいため制限をかけずに抽出結果を見たかったことから、全て同じ ID を付与する形をとっている。
    - Freebase ID の代替として、word2vec でベクトル化し、コサイン類似度を測って閾値で切るという方針があり得る。
- get_noun_list(doc)
    - 入力: doc （spacyで解析された文章）
    - 出力: 名詞句のリスト。(S,A,O)の S と O の候補となる。
    - noun_chunk と named entity recognition をしているが、不十分なケースもある。
        - test_renoun.py で、Facebook という語が抽出されていないケースがある
- get_noun_list_over(doc)
    - get_noun_list(doc) に加えて、名詞もリスト化。元々取れていなかった語が取れるように。
    - しかし、取れ過ぎてしまうケースもある。
        - Larry と Larry Page が両方とれてしまうなど
    - 今回はこちらではなく get_noun_list() を使って実装。
- extract_seed_fact(doc)
    - ステップ1.に対応
    - 出力: seed fact のリスト
    - Attribute に含まれる語が doc 中にあるかを調べた上でルールにかけて(S,A,O)を出力。
    - S, O は get_noun_list で得た noun_list 中の語でなくてはならない。
- get_root(s)
    - 入力: 名詞句 s
    - 出力: ルートにあたるトークン。依存構造木中の名詞句の代表。
        - "Larry Page" -> "Larry"
- create_graph(doc)
    - 出力: 成型した依存構造木。Networkx ライブラリの Graph() クラスで表現。
    - ノードは spacy の token を持ち、エッジは係り元 token 情報 ['head'] と関係名 ['relation'] を持つ。
- get_subgraph(graph, s, a, o)
    - 入力: 依存構造木とトリプル
    - 出力: トリプルを含む最小部分木。
- dependency_pattern_generation(doc, seed_fact)
    - ステップ2.に対応
    - 出力: doc から見つかった seed_fact の delexicalized subgraph 対応する attribute のタプル
    - seed_fact (S,A,O) の代表トークンに対して get_subgraph を実行
    - delexicalize は、S,A,O については文字列 "S", "A", "O" とし、その他のトークンは token.text をそのまま使う
    - エッジの['head']も忘れずに delexicalize する
- find_SO(att_token, node_t, node_p, dep_tree, dep_patt, token_check_dict)
    - 出力: 与えられた依存構造パターンの各ノードと、doc の依存構造木のノードの対応関係。
        - "S" や "O" に対応する具体的なトークンをマッピング
        - 対応がつかない場合は False
- candidate_generation(doc, att_patt_graph)
    - ステップ3.に対応。
    - 入力: doc, attribute とそれに対応する delexicalized subgraph の対応関係（二部グラフの形で表現）
    - 出力: doc 中から見つかったトリプルの候補
    - attribute を中心にして find_SO をかけて得る。

