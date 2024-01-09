import pandas as pd
from neo4j import GraphDatabase


uri = "bolt://localhost:7687"
user = "neo4j"
password = "lmm1314520"
driver = GraphDatabase.driver(uri, auth=(user, password))


def create_node(tx, coordinates):
    # 创建具有坐标的节点
    tx.run("MERGE (p:Point {coordinates: $coordinates})", coordinates=coordinates)

def create_relationship(tx, point1, point2):
    # 在两个坐标点之间创建关系
    tx.run(
        """
        MATCH (p1:Point {coordinates: $point1}), (p2:Point {coordinates: $point2})
        MERGE (p1)-[:CONNECTED_TO]->(p2)
        """,
        point1=point1, point2=point2
    )

df = pd.read_excel(r'C:\Users\11054\Desktop\hust\Question1\point_connections.xlsx')
# 连接到数据库并创建节点和关系
with driver.session() as session:
    # 创建所有独特的节点
    unique_points = set(df['Point'])
    unique_points = {point for point in unique_points if not pd.isna(point)}  # 使用 pd.isna 处理 NaN # 移除任何 NA 值
    for point in unique_points:
        session.execute_write(create_node, point)

    # 为每个连接创建关系
    for index, row in df.iterrows():
        main_point = row['Point']
        connected_points = [point for point in row[1:] if point is not pd.NA]
        for connected_point in connected_points:
            session.execute_write(create_relationship, main_point, connected_point)

driver.close()

