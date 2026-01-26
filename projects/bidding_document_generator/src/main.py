from src.nlp_model_integration import NLPModelIntegration
from src.knowledge_graph_construction import KnowledgeGraphConstruction
from src.template_management import fill_template


def main():
    # 初始化 NLP 模型集成
    nlp_integration = NLPModelIntegration(api_key="YOUR_OPENAI_API_KEY")
    # 微调模型
    nlp_integration.fine_tune_model('../data/bidding_data.csv')
    
    # 初始化知识图谱构建
    kg_construction = KnowledgeGraphConstruction(uri="bolt://localhost:7687", user="neo4j", password="password")
    kg_construction.build_graph()

    # 获取项目信息和从知识图谱查询相关内容
    project_name = "示例项目"
    current_date = "2024 - 01 - 01"
    scope = "软件开发"
    query = "MATCH (p:招标项目)-[:关联技术标准]->(s:技术标准) WHERE p.name = '示例项目' RETURN s.content"
    tech_standards = kg_construction.query_graph(query)

    # 填充模板
    data = {
        "project_name": project_name,
        "current_date": current_date,
        "scope": scope,
        "tech_standards": tech_standards
    }
    filled_template = fill_template('../templates/bidding_template.json', data)

    # 生成最终文件
    final_document = nlp_integration.combine_models_outputs(filled_template)
    print(final_document)


if __name__ == "__main__":
    main()