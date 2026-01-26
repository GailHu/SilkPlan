from py2neo import Graph, Node, Relationship
import re
import pandas as pd
from sklearn_crfsuite import CRF
from transformers import pipeline

# 连接到Neo4j数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# 基于规则的实体识别函数
def rule_based_entity_recognition(text):
    entities = {}
    # 示例：匹配项目编号，假设项目编号格式为以字母开头，后跟数字
    project_id_pattern = r'[A-Za-z]+\d+'
    project_ids = re.findall(project_id_pattern, text)
    if project_ids:
        entities['项目编号'] = project_ids
    # 示例：匹配金额，假设金额格式为数字后跟货币符号
    amount_pattern = r'\d+[元美元€£]'
    amounts = re.findall(amount_pattern, text)
    if amounts:
        entities['金额'] = amounts
    return entities

# 基于机器学习的实体识别函数（使用CRF示例）
def ml_based_entity_recognition(text):
    # 这里简单示例，实际需要训练数据和模型
    crf = CRF(algorithm='lbfgs',
              c1=0.1,
              c2=0.1,
              max_iterations=100,
              all_possible_transitions=False)
    # 这里假设已经有训练好的模型，直接预测
    # 实际应用中需要对文本进行特征提取等预处理
    # 这里简单返回示例结果
    entities = {'投标人': ['示例公司'], '招标人': ['招标单位']}
    return entities

# 基于预训练语言模型的实体识别函数（使用Hugging Face的pipeline）
def bert_based_entity_recognition(text):
    ner_pipeline = pipeline("ner", model="bert-base-chinese")
    results = ner_pipeline(text)
    entities = {}
    for result in results:
        entity_type = result['entity']
        entity_word = result['word']
        if entity_type not in entities:
            entities[entity_type] = [entity_word]
        else:
            entities[entity_type].append(entity_word)
    return entities

# 依存句法分析进行关系抽取（示例，实际需要更复杂的处理）
def dependency_parsing_relation_extraction(text):
    # 这里简单示例，假设可以直接从文本中提取关系
    relations = []
    if '投标人' in text and '投标项目' in text:
        relations.append(('投标人', '投标关系', '投标项目'))
    return relations

# 深度学习模型进行关系抽取（示例，实际需要构建和训练模型）
def deep_learning_relation_extraction(text):
    # 这里简单示例，假设可以直接从文本中提取关系
    relations = []
    if '投标人' in text and '产品/服务' in text:
        relations.append(('投标人', '提供关系', '产品/服务'))
    return relations

# 处理单个文本的实体和关系抽取并存储到Neo4j
def process_text(text):
    # 实体识别
    rule_entities = rule_based_entity_recognition(text)
    ml_entities = ml_based_entity_recognition(text)
    bert_entities = bert_based_entity_recognition(text)
    all_entities = {**rule_entities, **ml_entities, **bert_entities}

    # 创建实体节点
    entity_nodes = {}
    for entity_type, entity_list in all_entities.items():
        for entity in entity_list:
            node = Node(entity_type, name=entity)
            graph.create(node)
            entity_nodes[(entity_type, entity)] = node

    # 关系抽取
    dep_relations = dependency_parsing_relation_extraction(text)
    dl_relations = deep_learning_relation_extraction(text)
    all_relations = dep_relations + dl_relations

    # 创建关系
    for rel in all_relations:
        source_type, rel_type, target_type = rel
        source_nodes = [node for (etype, ename), node in entity_nodes.items() if etype == source_type]
        target_nodes = [node for (etype, ename), node in entity_nodes.items() if etype == target_type]
        if source_nodes and target_nodes:
            for source_node in source_nodes:
                for target_node in target_nodes:
                    relationship = Relationship(source_node, rel_type, target_node)
                    graph.create(relationship)

# 处理大批量文本文件
def process_batch_text_files(file_paths):
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            process_text(text)

# 示例调用
if __name__ == "__main__":
    file_paths = ['text_file1.txt', 'text_file2.txt']  # 替换为实际的文件路径列表
    process_batch_text_files(file_paths)