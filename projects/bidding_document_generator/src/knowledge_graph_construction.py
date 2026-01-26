from neo4j import GraphDriver
import pandas as pd


class KnowledgeGraphConstruction:
    def __init__(self, uri, user, password):
        self.driver = GraphDriver(uri, user, password)

    def create_node(self, label, properties):
        with self.driver.session() as session:
            session.run(f"CREATE (n:{label} $props)", props=properties)

    def create_relationship(self, node1_label, node1_id, rel_type, node2_label, node2_id):
        with self.driver.session() as session:
            session.run(f"MATCH (a:{node1_label} {{id: $id1}}), (b:{node2_label} {{id: $id2}}) "
                        "CREATE (a)-[r:{rel_type}]->(b)", id1=node1_id, id2=node2_id, rel_type=rel_type)

    def build_graph(self):
        laws_df = pd.read_csv('../data/laws.csv')
        standards_df = pd.read_csv('../data/standards.csv')
        project_cases_df = pd.read_csv('../data/project_cases.csv')
        suppliers_df = pd.read_csv('../data/suppliers.csv')
        experts_df = pd.read_csv('../data/experts.csv')

        # 创建招标项目节点
        for index, row in project_cases_df.iterrows():
            self.create_node("招标项目", {"id": row["project_id"], "name": row["project_name"]})

        # 创建投标方节点
        for index, row in suppliers_df.iterrows():
            self.create_node("投标方", {"id": row["supplier_id"], "name": row["supplier_name"]})

        # 创建招标项目与投标方的参与关系
        for index, row in project_cases_df.iterrows():
            self.create_node("招标项目", row["project_id"], "参与", "投标方", row["supplier_id"])

    def query_graph(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record for record in result]