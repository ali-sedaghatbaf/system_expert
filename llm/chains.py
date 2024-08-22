from langchain.chains import GraphCypherQAChain
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    PromptTemplate,
    AIMessagePromptTemplate,
)
from utils import (
    ImpactEnum,
    ElapsedTimeEnum,
    EquipmentEnum,
    WindowEnum,
    KnowledgeEnum,
    ExpertiseEnum,
)
from typing import List, Any
from adapters.neo4j_adapter import Neo4j


def configure_llm_only_chain(llm):
    # LLM only response
    template = """
    You are a helpful assistant that helps a support agent with answering questions about systems engineering, cyber security, functional safety and the automotive industry.
    If you don't know the answer, just say that you don't know, you must not make up an answer.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    def generate_llm_output(
        user_input: str, callbacks: List[Any], prompt=chat_prompt
    ) -> str:
        chain = prompt | llm
        answer = chain.invoke(
            {"question": user_input}, config={"callbacks": callbacks}
        ).content
        return {"answer": answer}

    return generate_llm_output


def configure_llm_vector_chain(llm, query_embeddings, vector_func):

    neo4jvector = vector_func(query_embeddings)

    retriever = neo4jvector.as_retriever()

    kg_qa = RetrievalQA.from_chain_type(
        llm,  # <1>
        chain_type="stuff",  # <2>
        retriever=retriever,  # <3>
    )
    return kg_qa


def configure_llm_cypher_chain(llm):

    graph = Neo4j.graph()
    graph.refresh_schema()
    CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
    Instructions:
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    Ignore the embedding property of each node.
    Schema:
    {schema}
    Note: Do not include any explanations or apologies in your responses.
    Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
    Do not include any text except the generated Cypher statement.
    Cypher examples:
    # which requirements are associated with the Camera ECU?
    MATCH (s:Item {{name: 'Camera ECU'}})-[:Requirement]->(d:Item)
    RETURN d.name as requirement
    The question is:
    {question}"""

    CYPHER_GENERATION_PROMPT = PromptTemplate(
        input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
    )
    cypher_chain = GraphCypherQAChain.from_llm(
        cypher_llm=llm,
        qa_llm=llm,
        graph=graph,
        verbose=True,
        top_k=2,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        validate_cypher=True,
    )

    return cypher_chain


class SWModelEleemnt(BaseModel):
    name: str = Field(description="element name")
    is_asset: bool = Field(description="element is an asset")
    confidentiality: bool = Field(description="element's confidentiality is important")
    integrity: bool = Field(description="element's integrity is important")
    availability: bool = Field(description="element's availability is important")
    authenticity: bool = Field(description="element's authenticity is important")
    non_repudiation: bool = Field(description="element's non-repudiation is important")
    asset_reason: str = Field(
        description="reason about your choice for considering the element as an asset"
    )
    confidentiality_reason: str = Field(
        description="reason about your choice for the importance of the element's confidentiality"
    )
    integrity_reason: str = Field(
        description="reason about your choice for the importance of the element's integrity"
    )
    availability_reason: str = Field(
        description="reason about your choice for the importance of the element's availability"
    )
    authenticity_reason: str = Field(
        description="reason about your choice for the importance of the element's authenticity"
    )
    non_repudiation_reason: str = Field(
        description="reason about your choice for the importance of the element's non-repudiation"
    )


class SWModelElements(BaseModel):
    elements: List[SWModelEleemnt] = Field(description="list of elements")


def configure_asset_chain(llm):
    template = """
    As input you get a list of vehicle design elements, their relationships and the security propoerties you should consider:
    {input}
    Forv each element in the list you need to first determine whether it could be considered as an asset as defined by the ISO standard. 
    If you do not recognize the element, mark it as not an asset and move to the next one.
    If you considered an element is an asset, then you should specify which security properties are important for that asset.  
    You shouldf focus only on the security properties provided to you as input. 
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=SWModelElements)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )

    def generate_llm_output(
        user_input, callbacks: List[Any], prompt=chat_prompt
    ) -> str:  # using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )

        return str(answer)

    return generate_llm_output


class ThreatScenario(BaseModel):
    asset_name: str = Field(description="name of target asset")
    scenario_description: str = Field(description="description of the threat scenario")
    affected_properties: str = Field(
        description="security properties affected by the threat scenario"
    )


class ThreatScenarios(BaseModel):
    scenarios: List[ThreatScenario] = Field(description="list of threat scenarios")


def configure_threat_chain(llm):
    template = """
    As input you get the following list of vehicle assets and their important security properties:
    {input} 
    Forv each asset in the list you need to specify at least one threat scenarios that would lead to the compromise of at least one of the asset's security propoerties. 
    You should lookup scenarios in the ATM database which could be found here (https://atm.automotiveisac.com/home).
    You need to make sure that the final list of threat scenarios cover all the security properties impotant for that asset. For example, if the asset has only one security property, then one threat scenario would be enough. 
    However if it has two prooerties, then you need to specify either one scenario for each property (i.e., two scenarios in total) or one scenario that affects both properties.
    Focus only on the security properties associated with the asset and marked True.
    If you do not recognize the asset, ignore it and move to the next one.
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=ThreatScenarios)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )

    def generate_llm_output(
        user_input: str, callbacks: List[Any], prompt=chat_prompt
    ) -> str:  # using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )

        return str(answer)

    return generate_llm_output


class DamageScenario(BaseModel):
    asset_name: str = Field(description="name of target asset")
    threat_scenario: str = Field(description="name of target threat")
    damage_scenario: str = Field(description="description of the damage scenario")
    safety_impact: ImpactEnum = Field(description="the safety impact of the scenario")
    privacy_impact: ImpactEnum = Field(description="the privacy impact of the scenario")
    financial_impact: ImpactEnum = Field(
        description="the financial impact of the scenario"
    )
    operational_impact: ImpactEnum = Field(
        description="the operational impact of the scenario"
    )
    safety_reason: str = Field(
        description="reason about your choice for the safety impact"
    )
    privacy_reason: str = Field(
        description="reason about your choice for the privacy impact"
    )
    fin_reason: str = Field(
        description="reason about your choice for the financial impact"
    )
    op_reason: str = Field(
        description="reason about your choice for the operational impact"
    )


class DamageScenarios(BaseModel):
    scenarios: List[DamageScenario] = Field(description="list of damage scenarios")


def configure_damage_chain(llm):
    template = """
    As input you get a list of vehicle assets and their associated cyber threats.  
    {input}   
    For each pair of (asset, threat scenario) in the list you need to specify the worst-case damage scenario that would ocuur as a result of successfully implementing the threat scenario. 
    If you do not recognize the asset, ignore it and move to the next one.
    For each damage scenario you come up with, you should assess potential adverse consequences for road users in the impact categories of safety, financial, operational, and privacy respectively.
    Follow the format instructions to generate the output and do not provide any additional information.
    
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=DamageScenarios)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )

    def generate_llm_output(
        user_input: str, callbacks: List[Any], prompt=chat_prompt
    ) -> str:  # using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )

        return str(answer)

    return generate_llm_output


class AttackPath(BaseModel):
    asset_name: str = Field(description="name of target asset")
    threat_scenario: str = Field(description="description of the threat scenario")
    attack_path: str = Field(
        description="steps to follow to implement the threat scenario"
    )
    elapsed_time: ElapsedTimeEnum = Field(
        description=" The time required to identify and exploit the associated vulnerability"
    )
    equipment: EquipmentEnum = Field(
        description="The necessity and availability of specialized tools or equipment to perform the attack."
    )
    knowledge: KnowledgeEnum = Field(
        description="The level of asset knowledge required to carry out the attack on the target asset"
    )
    expertise: ExpertiseEnum = Field(
        description="The level of expertise required to carry out the step"
    )
    window: WindowEnum = Field(
        description="The specific conditions and time frame within which the attack can be executed"
    )
    elapsed_time_reason: str = Field(
        description="reason about your choice for elapsed time"
    )
    equipment_reason: str = Field(description="reason about your choice for equipment")
    knowledge_reason: str = Field(description="reason about your choice for knowledge")
    expertise_reason: str = Field(description="reason about your choice for expertise")
    window_reason: str = Field(
        description="reason about your choice for the window of opportunity"
    )


class AttackPaths(BaseModel):
    paths: List[AttackPath] = Field(description="list of attack paths")


def configure_attack_path_chain(llm):
    template = """
    As input you get a list of vehicle assets and their associated cyber threats.  
    {input}   
    For each pair of (asset, threat scenario) in the list you need to specify the worst-case attack path that should be followed to implwement the threat scenario. 
    After that you need to analyze the feasibility factors (e.g., equipment, knowledge, expertise) on the identified attack path.
    If you do not recognize the asset, ignore it and move to the next one.
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=AttackPaths)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )

    def generate_llm_output(
        user_input: str, callbacks: List[Any], prompt=chat_prompt
    ) -> str:  # using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )

        return str(answer)

    return generate_llm_output


class Goal(BaseModel):
    asset_name: str = Field(description="name of target asset")
    threat_scenario: str = Field(description="description of the threat scenario")
    goal: str = Field(
        description="cybersecurity goal identified for reducing the risk of the threat scenario"
    )
    requirements: str = Field(
        description="cybersecurity requirmeents for realizing the goal"
    )


class Goals(BaseModel):
    goals: List[Goal] = Field(description="list of goals")


def configure_goal_chain(llm):
    template = """
    As input you get the following list of vehicle assets and their associated cyber threats.  
    {input} 
    For each pair of (asset, threat scenario) in the list you need to specify the cybersecurity goal that should be realized to reduce the risk of the threat scenario. 
    Then, you should specify at least one cybersecuirty  reuirmeent to address the goal.
    If you do not recognize the asset, ignore it and move to the next one.
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=Goals)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )

    def generate_llm_output(
        user_input: str, callbacks: List[Any], prompt=chat_prompt
    ) -> str:  # using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )

        return str(answer)

    return generate_llm_output
