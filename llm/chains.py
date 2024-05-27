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
from utils import ImpactEnum
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

    # end::vector[]

    # tag::retriever[]
    retriever = neo4jvector.as_retriever()
    # end::retriever[]

    # tag::qa[]
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

    """ def generate_llm_output(user_input: str, callbacks: List[Any]) -> str:
        chain = cypher_chain
        answer = chain.invoke(
            {"input": user_input}, config={"callbacks": callbacks}
        ).content
        return {"output": answer}
 """
    return cypher_chain


class SWModelEleemnt(BaseModel):
    name: str = Field(description="element name")
    is_asset: bool = Field(description="element is an asset")
    confidentiality: bool = Field(description="element\'s confidentiality is important")
    integrity: bool = Field(description="element\'s integrity is important")
    availability: bool = Field(description="element\'s availability is important")
    authenticity: bool = Field(description="element\'s authenticity is important")
    non_repudiation: bool = Field(description="element\'s non-repudiation is important")
    asset_reason: str = Field(description="reason about your choice for considering the element as an asset")
    confidentiality_reason: str = Field(description="reason about your choice for the importance of the element's confidentiality")
    integrity_reason: str = Field(description="reason about your choice for the importance of the element's integrity")
    availability_reason: str = Field(description="reason about your choice for the importance of the element's availability")
    authenticity_reason: str = Field(description="reason about your choice for the importance of the element's authenticity")
    non_repudiation_reason: str = Field(description="reason about your choice for the importance of the element's non-repudiation")

class SWModelElements(BaseModel):
    elements: List[SWModelEleemnt] = Field(description="list of elements")





def configure_asset_chain(llm):
    template = """
    You are an automotive cybersecurity engineer and quite familiar with ISO 21434.
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
    """ system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "Is this element an asset? {element}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    ai_message_prompt = AIMessagePromptTemplate.from_template(
        "", partial_variables={"format_instructions": format_instructions}
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt, ai_message_prompt]
    ) """

    def generate_llm_output(user_input, callbacks: List[Any], prompt=chat_prompt) -> str: #using dict or other types raises error
        
        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input":user_input},
            config={
                "callbacks": callbacks,
            },
        )
       
        return str(answer)

    return generate_llm_output



class DamageScenario(BaseModel):
    asset_name: str = Field(description="name of target asset")
    scenario_description: str = Field(description="description of the damage scenario")
    safety_impact:ImpactEnum = Field(description="the safety impact of the scenario")
    privacy_impact:ImpactEnum = Field(description="the privacy impact of the scenario")
    financial_impact:ImpactEnum = Field(description="the financial impact of the scenario")
    operational_impact:ImpactEnum = Field(description="the operational impact of the scenario")
    safety_reason: str = Field(description="reason about your choice for the safety impact")
    privacy_reason: str = Field(description="reason about your choice for the privacy impact")
    fin_reason: str = Field(description="reason about your choice for the financial impact")
    op_reason: str = Field(description="reason about your choice for the operational impact")



class DamageScenarios(BaseModel):
    scenarios: List[DamageScenario] = Field(description="list of damage scenarios")
    

def configure_damage_chain(llm):
    template = """
    You are an automotive cybersecurity engineer and quite familiar with ISO 21434.
    As input you get a list of vehicle assets and their important security properties.    
    For each asset in the list you need to specify the worst-case damage scenario that would ocuur as a consequence of compromising the security propoerties. 
    If you do not recognize the asset, ignore it and move to the next one.
    For each scenario you specify, you should assess potential adverse consequences for road users in the impact categories of safety, financial, operational, and privacy respectively.
    Follow the format instructions to generate the output and do not provide any additional information.
    {input} 
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=DamageScenarios)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )
    """ system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "Is this element an asset? {element}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    ai_message_prompt = AIMessagePromptTemplate.from_template(
        "", partial_variables={"format_instructions": format_instructions}
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt, ai_message_prompt]
    ) """

    def generate_llm_output(user_input: str, callbacks: List[Any], prompt=chat_prompt) -> str: #using dict or other types raises error

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
    affected_properties:str = Field(description="security properties affected by the threat scenario")

class ThreatScenarios(BaseModel):
    scenarios: List[ThreatScenario] = Field(description="list of threat scenarios")
    

def configure_threat_chain(llm):
    template = """
    You are an automotive cybersecurity engineer and quite familiar with ISO 21434.
    As input you get the following list of vehicle assets and their important security properties:
    {input} 
    Forv each asset in the list you need to specify at least one threat scenarios that would lead to the compromise of at least one of the asset's security propoerties. 
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
    """ system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "Is this element an asset? {element}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    ai_message_prompt = AIMessagePromptTemplate.from_template(
        "", partial_variables={"format_instructions": format_instructions}
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt, ai_message_prompt]
    ) """

    def generate_llm_output(user_input: str, callbacks: List[Any], prompt=chat_prompt) -> str: #using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )
       
        return str(answer)

    return generate_llm_output

def configure_attack_path_chain(llm):
    template = """
    You are an automotive cybersecurity engineer and quite familiar with ISO 21434.
    As input you get the following list of vehicle assets and their important security properties:
    {input} 
    Forv each asset in the list you need to specify one or more threat scenarios that would lead to the compromise of one or more of the specified security propoerties. 
    You need to make sure that the threat scenarios cover all security properties. For example, if the asset has only one security property, then one threat scenario would be enough. 
    However if it has two prooerties, then you need to specify either one scenario for each property (i.e., two in total) or one scenario that affects both properties.
    If you do not recognize the asset, ignore it and move to the next one.
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=ThreatScenarios)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )
    """ system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "Is this element an asset? {element}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    ai_message_prompt = AIMessagePromptTemplate.from_template(
        "", partial_variables={"format_instructions": format_instructions}
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt, ai_message_prompt]
    ) """

    def generate_llm_output(user_input: str, callbacks: List[Any], prompt=chat_prompt) -> str: #using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )
       
        return str(answer)

    return generate_llm_output

def configure_goal_chain(llm):
    template = """
    You are an automotive cybersecurity engineer and quite familiar with ISO 21434.
    As input you get the following list of vehicle assets and their important security properties:
    {input} 
    Forv each asset in the list you need to specify one or more threat scenarios that would lead to the compromise of one or more of the specified security propoerties. 
    You need to make sure that the threat scenarios cover all security properties. For example, if the asset has only one security property, then one threat scenario would be enough. 
    However if it has two prooerties, then you need to specify either one scenario for each property (i.e., two in total) or one scenario that affects both properties.
    If you do not recognize the asset, ignore it and move to the next one.
    Follow the format instructions to generate the output and do not provide any additional information.
    {format_instructions}
    
    """
    parser = JsonOutputParser(pydantic_object=ThreatScenarios)
    format_instructions = parser.get_format_instructions()
    chat_prompt = PromptTemplate.from_template(
        template, partial_variables={"format_instructions": format_instructions}
    )
    """ system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "Is this element an asset? {element}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    ai_message_prompt = AIMessagePromptTemplate.from_template(
        "", partial_variables={"format_instructions": format_instructions}
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt, ai_message_prompt]
    ) """

    def generate_llm_output(user_input: str, callbacks: List[Any], prompt=chat_prompt) -> str: #using dict or other types raises error

        chain = prompt | llm | parser
        answer = chain.invoke(
            {"input": user_input},
            config={
                "callbacks": callbacks,
            },
        )
       
        return str(answer)

    return generate_llm_output