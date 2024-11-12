import pandas as pd
from graph_tool.all import Graph
from graph_tool.all import CliqueState

def csv2graph(filepath):
    # 读取 CSV 文件并提取 "node_id" 和 "neighbour" 列
    print(filepath)
    data = pd.read_csv(filepath, usecols=["node_id", "neighbour"])
    
    # return
    # 创建一个空的无向图
    g = Graph(directed=False)
    # 使用字典来映射 node_id 到 graph_tool 中的顶点
    node_map = {}
    # 遍历数据，添加节点和边
    for _, row in data.iterrows():
        node_id = row["node_id"]
        neighbours = eval(row["neighbour"])  # 将字符串列表转换为 Python 列表
        
        # 如果当前节点不在图中，先添加它
        if node_id not in node_map:
            node_map[node_id] = g.add_vertex()
        
        # 添加相邻节点和边
        for neighbour in neighbours:
            if neighbour not in node_map:
                node_map[neighbour] = g.add_vertex()
            
            # 添加无向边
            g.add_edge(node_map[node_id], node_map[neighbour])
    return g

def graph2hyperg(g: Graph, niter = 10000):
    state = CliqueState(g)
    state.mcmc_sweep(niter=niter)

    # 使用CliqueState找到所有cliques
    cliques = []
    for v in state.f.vertices():      # 遍历factor graph(节点和超边组成)
        if state.is_fac[v]:
            continue                  # 跳过factors（因子节点在 CliqueState 中用于表示连接不同节点的约束，不需要被当作实际的 clique 节点处理）
        # print(state.c[v], state.x[v]) # state.c[v] 是节点 v 所属于的 clique（即其所属的超边），state.x[v] 是一个值，表示节点 v 是否被占用（只有被占用的节点才被认为是属于一个有效的 clique）。
        if state.x[v] > 0:
            cliques.append(state.c[v])
 
    # 创建超图，使用一个邻接表来存储超边
    hypergraph = {}
    for clique in cliques:
        # 将 clique 转换为元组，作为超边的键
        hyperedge_key = tuple(clique)
        # 通过index返找出原始的node_id
        node_id_list = list(clique)
        hypergraph[hyperedge_key] = node_id_list
   
    return hypergraph

def count_hyperedges(hypergraph):
    """统计超边数量"""
    return len(hypergraph)


def count_two_node_hyperedges(hypergraph):
    """统计仅含有两个节点的超边数量"""
    return sum(1 for edge in hypergraph.values() if len(edge) == 2)

def count_isolated_nodes(hypergraph):
    """统计去掉仅含有两个节点的超边后孤立节点数量"""
    # 删除仅含两个节点的超边
    filtered_hypergraph = {e: nodes for e, nodes in hypergraph.items() if len(nodes) > 2}
    
    # 统计所有出现的节点
    all_nodes = set()
    for nodes in hypergraph.values():
        all_nodes.update(nodes)
    
    # 统计每个节点的出现次数
    node_degree = {node: 0 for node in all_nodes}
    for nodes in filtered_hypergraph.values():
        for node in nodes:
            node_degree[node] += 1
    
    # 统计孤立节点数量
    return sum(1 for degree in node_degree.values() if degree == 0)

def max_hyperedge_size(hypergraph):
    """计算最大超边的大小"""
    return max(len(edge) for edge in hypergraph.values())

def node_coverage_rate(hypergraph):
    """计算节点覆盖率"""
    # 统计所有节点
    all_nodes = set()
    for nodes in hypergraph.values():
        all_nodes.update(nodes)
    
    # 假设超图的节点总数为覆盖节点数
    total_possible_nodes = len(all_nodes)
    covered_nodes = {node for nodes in hypergraph.values() for node in nodes}
    
    return len(covered_nodes) / total_possible_nodes if total_possible_nodes > 0 else 0

def hyperedge_sparsity(hypergraph):
    """计算超边稀疏度(实际超边数量与理论最大超边数量之比)"""
    all_nodes = set()
    for nodes in hypergraph.values():
        all_nodes.update(nodes)
    
    num_nodes = len(all_nodes)
    max_possible_hyperedges = 2 ** num_nodes - 1 if num_nodes > 1 else 1
    return len(hypergraph) / max_possible_hyperedges if max_possible_hyperedges > 0 else 0

def hyperege_incidence(hypergraph):
    """计算超边incidence"""
    return sum(len(nodes) for nodes in hypergraph.values())



if __name__ == "__main__":

    root_path = "/Users/z5547461/code/TAG_Dataset/"
    out_path = "output_analysis.txt"

    dataset_name_list = {
        'Children':'Children',
        'CitationV8':'Citation-2015',
        'Computers':'Computers',
        'Fitness':'Fitness',
        'Goodreads':'Goodreads',
        # 'History':'',
        'Photo':'Photo'
    }
    result = { }
    for key in dataset_name_list:
        file = root_path + key + '/' + dataset_name_list[key] +'.csv'
        g = csv2graph(filepath=file)
        hypergraph = graph2hyperg(g)
        # res = "数据集\t节点数目\t普通边数量\t超边数量\tincidence\t仅含有两个节点的超边数量\t孤立节点数量\t最大超边\t节点覆盖率\t超边稀疏度"
        res = " "
        with open(out_path, "w") as file:
            # res = "数据集\t节点数目\t普通边数量\t超边数量\tincidence\t仅含有两个节点的超边数量\t孤立节点数量\t最大超边\t节点覆盖率\t超边稀疏度"
            res = key+'\t'+g.num_vertices()+'\t' + g.num_edges()+'\t'+len(hypergraph)+'\t'+count_two_node_hyperedges(hypergraph)+'\t'+count_isolated_nodes(hypergraph)+'\t'+max_hyperedge_size(hypergraph)+'\t'+node_coverage_rate(hypergraph)+'\t'+hyperedge_sparsity(hypergraph)
            file.write(res+ "\n")
            print(key +' word down!')