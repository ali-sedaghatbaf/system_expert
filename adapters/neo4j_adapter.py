from neo4j import GraphDatabase
import uuid
import hashlib
from llmsherpa.readers import LayoutPDFReader
import os
import glob
from datetime import datetime
import time
import streamlit as st
from streamlit.logger import get_logger
from utils import load_embedding_model
from functools import cache
from langchain_community.graphs import Neo4jGraph
from pathlib import Path
import json

from langchain_community.vectorstores import Neo4jVector

logger = get_logger(__name__)
# Please change the following variables to your own Neo4j instance
NEO4J_URI = st.secrets["NEO4J_URI"]
NEO4J_USERNAME = st.secrets["NEO4J_USERNAME"]
NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
NEO4J_DATABASE = st.secrets["NEO4J_DATABASE"]
OLLAMA_BASE_URL = st.secrets["OLLAMA_BASE_URL"]
EMBEDDING_MODEL_NAME = st.secrets["EMBEDDING_MODEL"]

driver = GraphDatabase.driver(
    NEO4J_URI, database=NEO4J_DATABASE, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


class Neo4j:
    def __init__(self) -> None:

        self.embedding_model, self.vector_dimension = load_embedding_model(
            EMBEDDING_MODEL_NAME,
            config={"ollama_base_url": OLLAMA_BASE_URL},
            logger=logger,
        )
        driver.verify_connectivity()

    def init_db(self, object_type):
        with driver.session() as session:

            query = f"CREATE CONSTRAINT {object_type} IF NOT EXISTS FOR (c:{object_type}) REQUIRE (c.object_id) IS UNIQUE;"
            session.run(query)

            query = f"CALL db.index.vector.createNodeIndex('{object_type}VectorIndex', '{object_type}', 'embedding', $dimension, 'COSINE');"

            try:
                session.run(query, {"dimension": self.vector_dimension})
            except:
                pass

        driver.close()

    @staticmethod
    def graph():
        return Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE,
            sanitize=True,
        )


@cache
class SWNeo4j(Neo4j):
    object_type = "Item"

    def __init__(self) -> None:
        super().__init__()

        self.init_db(SWNeo4j.object_type)

    @staticmethod
    def vector(embeddings):
        return Neo4jVector.from_existing_index(
            embeddings,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name=f"{SWNeo4j.object_type}VectorIndex",
            node_label=SWNeo4j.object_type,
            text_node_property="description",
            embedding_node_property="embedding",
            retrieval_query="""
        RETURN
            node.description AS text,
            score,
            {
                name: node.name,
                object_id: node.object_id
            } AS metadata
        """,
        )

    def find_security_properties(self, tara_handle):
        with driver.session() as session:
            params = {"tara_handle": tara_handle}
            query = "MATCH (t:TARA {object_id:$tara_handle})-[:Security_Property_List]->(p:Security_Property_Catalog)-[:Security_Property]->(m:Security_Property) return m.name as p_name"

            props = session.run(query=query, parameters=params)
            for d in props:
                yield d
        driver.close()

    def find_item_elements(self, item_name):
        with driver.session() as session:

            query = """MATCH (p:Conceptual_System_Model {name: $item_name})
            CALL apoc.path.subgraphAll(p, {
                relationshipFilter: "System_Component|Subcomponent|Communication_Medium|Stored_Information",
                labelFilter:"-System_Stakeholder",
                minLevel: 1,
                maxLevel: 4
                
            })
            YIELD  nodes, relationships            
            UNWIND relationships as rel
            UNWIND nodes as nd
            return type(rel) as rel_type, startNode(rel).name as rel_start, endNode(rel).name as rel_end, nd.name as node_name, nd.description as node_description, nd.object_id as node_id

            """
            result = session.run(query, parameters={"item_name": item_name})
            for d in result:
                yield d
        driver.close()

    def find_item_definitions(self):

        with driver.session() as session:

            query = (
                "MATCH (m:TARA)-[:Security_Item_Definition]->(n:Conceptual_System_Model)"
                + " RETURN n.name as item_name, n.object_id as item_handle, m.name as tara_name, m.object_id as tara_handle"
            )

            defs = session.run(query=query, parameters={})
            for d in defs:
                yield d
        driver.close()

    def insert_data(self, sw_items):

        with driver.session() as session:
            for sw_item in sw_items.values():

                params, query = self.generate_node_query(sw_item)
                session.run(query, parameters=params)
            for sw_item in sw_items.values():
                for part_handle, part_type in sw_item["parts"].items():
                    params, query = self.generate_relation_query(
                        sw_item, sw_items[part_handle], part_type
                    )

                    session.run(query, parameters=params)

        driver.close()

    def generate_relation_query(self, src_item, dest_item, rel_label):
        params = {
            "s_handle": src_item["handle"],
            "d_handle": dest_item["handle"],
        }

        query = (
            "MATCH (s:"
            + src_item["type"]
            + " {object_id: $s_handle}) MATCH (d:"
            + dest_item["type"]
            + " {object_id: $d_handle}) MERGE (d)<-[:"
            + rel_label
            + "]-(s);"
        )

        return params, query

    def find_paths_to_asset(self, asset_name):
        params = {"asset": asset_name}
        with driver.session() as session:
            query = "MATCH paths = (s)-[:Possible_Attack*]->(d {name:$asset} ) WITH reduce(output = [], n IN nodes(paths) | output + n ) as nodeCollection UNWIND nodeCollection as client RETURN client.name;"
            paths = session.run(query, params)
            for p in paths:
                yield p
        session.close()

    def add_attack_graph(self):
        with driver.session() as session:
            rel_labels = {
                "Input_Interface": False,
                "Output_Interface": True,
                "Stored_Information": True,
                # "Subcomponent": True,
                # "System_Component": True,
                # "External_Component": False,
            }

            for rel_label in rel_labels:
                params, query = self.generate_attack_relation_query(
                    rel_label, "Possible_Attack", rel_labels[rel_label]
                )

                session.run(query, parameters=params)
        driver.close()

    def delete_attack_graph(self):
        with driver.session() as session:
            query = "MATCH (n)-[r:Possible_Attack]->() DELETE r"
            session.run(query)
        driver.close()

    def generate_attack_relation_query(self, rel_label, attack_label, forward=True):

        query = (
            "MATCH (s:Item)-[r1:"
            + rel_label
            + "]->(d:Item) MERGE (s)-[r2:"
            + attack_label
            + "]->(d);"
        )

        if not forward:
            query = (
                "MATCH (s:Item)-[r1:"
                + rel_label
                + "]->(d:Item) MERGE (s)<-[r2:"
                + attack_label
                + "]-(d);"
            )

        return {}, query

    def generate_node_query(self, node):
        params = {
            "name": node["name"],
            "handle": node["handle"],
            "description": node["description"],
        }
        cypher_attrs = []
        for attr in node["attributes"]:
            attr_name = attr["name"].lower()
            params[attr_name] = attr["value"]
            cypher_attrs.append(f"i.{attr_name} = ${attr_name}")

        params["embedding"] = ""  # self.embedding_model.embed_query(
        #    "name: " + node["name"] + "\n" + "description: " + node["description"]
        # )

        cypher_attr_str = ""
        if cypher_attrs:
            cypher_attr_str = ", " + ", ".join(cypher_attrs)
        query = (
            "MERGE (i:"
            + node["type"]
            + " {object_id: $handle}) ON CREATE SET i.name = $name, i.description = $description, i.embedding = $embedding"
            + cypher_attr_str
            + " RETURN i;"
        )

        return params, query


@cache
class MITRENeo4j(Neo4j):
    object_type = "Attack"

    def __init__(self) -> None:
        super().__init__()
        self.init_db(MITRENeo4j.object_type)

    @staticmethod
    def vector(embeddings):
        return Neo4jVector.from_existing_index(
            embeddings,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name=f"{MITRENeo4j.object_type}VectorIndex",
            node_label=MITRENeo4j.object_type,
            text_node_property="description",
            embedding_node_property="embedding",
            retrieval_query="""
        RETURN
            node.description AS text,
            score,
            {
                name: node.name,
                object_id: node.object_id
            } AS metadata
        """,
        )

    def import_data(self, mitre_objects, mitre_relations):
        with driver.session() as session:
            for mitre_object in mitre_objects:
                params, query = self.generate_node_query(mitre_object)
                session.run(query, parameters=params)
            for mitre_relation in mitre_relations:
                params, query = self.generate_relation_query(mitre_relation)

                session.run(query, parameters=params)
        driver.close()

    def generate_relation_query(self, relation):

        params = {
            "s_ref": relation.source_ref,
            "t_ref": relation.target_ref,
        }

        rel_type = str.capitalize(relation.relationship_type.replace("-", "_"))
        query = (
            "MATCH (s:"
            + MITRENeo4j.object_type
            + " {object_id: $s_ref}) MATCH (t:"
            + MITRENeo4j.object_type
            + " {object_id: $t_ref}) MERGE (t)<-[:"
            + rel_type
            + "]-(s);"
        )

        return params, query

    def generate_node_query(self, node):

        params = {
            "name": node["name"] if "name" in node else "",
            "object_id": node["id"],
            "description": node["description"] if "description" in node else "",
            "external_id": (
                node["external_references"][0]["external_id"]
                if "external_references" in node
                else ""
            ),
        }
        cypher_attrs = []
        """ if "attributes" in obj:
            for attr in obj["attributes"]:
                attr_name = attr["name"]
                params[attr_name] = attr["value"]
                cypher_attrs.append(f"i.{attr_name} = ${attr_name}") """

        """ params["embedding"] = self.embedding_model.embed_query(
            "name: " + obj.name + "\n" + "description: " + obj.description
        ) """

        cypher_attr_str = ""
        if cypher_attrs:
            cypher_attr_str = ", " + ", ".join(cypher_attrs)
        obj_type = (
            str.capitalize(node["type"].replace("x-mitre-", "").replace("-", "_"))
            if "type" in node
            else ""
        )

        query = (
            "MERGE (i:"
            + MITRENeo4j.object_type
            + ":"
            + obj_type
            + " {object_id: $object_id}) ON CREATE SET i.name = $name, i.description = $description, i.external_id = $external_id"  # , i.embedding = $embedding"
            + cypher_attr_str
            + " RETURN i;"
        )

        return params, query


@cache
class NVDNeo4j(Neo4j):
    object_type = "Vulnerability"

    def __init__(self, object_type) -> None:
        super().__init__()
        NVDNeo4j.object_type = object_type
        self.init_db(NVDNeo4j.object_type)

    @staticmethod
    def vector(embeddings):
        return Neo4jVector.from_existing_index(
            embeddings,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name=f"{NVDNeo4j.object_type}VectorIndex",
            node_label=NVDNeo4j.object_type,
            text_node_property="description",
            embedding_node_property="embedding",
            retrieval_query="""
        RETURN
            node.description AS text,
            score,
            {
                object_id: node.object_id
            } AS metadata
        """,
        )

    def import_data(self, nvd_objects, nvd_relations={}):
        with driver.session() as session:
            for d in nvd_objects:
                params, query = self.generate_node_query(d)
                session.run(query, parameters=params)
            for nvd_relation in nvd_relations:
                params, query = self.generate_mitre_relation_query(nvd_relation)

                session.run(query, parameters=params)
        driver.close()

    def generate_mitre_relation_query(
        self, relation
    ):  # relations with attacks in the ATT&CK db

        params = {
            "s_ref": relation.source_ref,
            "t_ref": relation.target_ref,
        }

        rel_type = "Allows"
        query = (
            "MATCH (s:"
            + self.object_type
            + " {object_id: $s_ref}) MATCH (t:"
            + MITRENeo4j.object_type
            + " {external_id: $t_ref}) MERGE (t)<-[:"
            + rel_type
            + "]-(s);"
        )

        return params, query

    def generate_node_query(self, node):

        params = {
            "object_id": node["id"],
            "description": node["description"],
        }
        """ params["embedding"] = self.embedding_model.embed_query(
           "description: " + obj.description
        ) """
        query = (
            "MERGE (i:"
            + self.object_type
            + " {object_id: $object_id}) ON CREATE SET i.description = $description"  # , i.embedding = $embedding"
            + " RETURN i;"
        )

        return params, query


@cache
class ATMNeo4j(Neo4j):
    object_type = "ATM"

    def __init__(self) -> None:
        super().__init__()
        self.init_db(ATMNeo4j.object_type)

    @staticmethod
    def vector(embeddings):
        return Neo4jVector.from_existing_index(
            embeddings,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name=f"{NVDNeo4j.object_type}VectorIndex",
            node_label=NVDNeo4j.object_type,
            text_node_property="description",
            embedding_node_property="embedding",
            retrieval_query="""
        RETURN
            node.description AS text,
            score,
            {
                name: node.name,
                object_id: node.object_id
            } AS metadata
        """,
        )

    def import_data(self, atm_data):

        with driver.session() as session:
            for d in json.loads(atm_data):
                params, query = self.generate_node_query(d)
                session.run(query, parameters=params)
        driver.close()

    def generate_node_query(self, node):

        params = {
            "object_id": node["id"] if "id" in node else "",
            "name": node["title"],
            "description": node["description"],
        }
        """ params["embedding"] = self.embedding_model.embed_query(
        "description: " + obj.description
        ) """
        query = (
            "MERGE (i:"
            + self.object_type
            + ":"
            + node["type"].capitalize()
            + " {object_id: $object_id}) ON CREATE SET i.name = $name, i.description = $description"  # , i.embedding = $embedding"
            + " RETURN i;"
        )

        return params, query
