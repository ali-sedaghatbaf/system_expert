# tag::importtool[]
import langchain
from langchain.tools import StructuredTool
from langchain import hub
import streamlit as st

# end::importtool[]
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
    initialize_agent,
    create_tool_calling_agent,
    AgentType,
)


# tag::importmemory[]
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

# end::importmemory[]
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    PromptTemplate,
)
from dotenv import load_dotenv
from llm import chains
from utils import load_embedding_model, load_llm
from adapters.neo4j_adapter import SWNeo4j, MITRENeo4j, NVDNeo4j
langchain.debug = True


embeddings, dimension = load_embedding_model()
llm = load_llm()
asset_chain = chains.configure_asset_chain(llm)
damage_chain = chains.configure_damage_chain(llm)
threat_chain = chains.configure_threat_chain(llm)
attack_path_chain = chains.configure_attack_path_chain(llm)
goal_chain = chains.configure_goal_chain(llm)
sw_vector_chain = chains.configure_llm_vector_chain(llm, embeddings, SWNeo4j.vector)
attack_vector_chain = chains.configure_llm_vector_chain(llm, embeddings, MITRENeo4j.vector)
nvd_vector_chain = chains.configure_llm_vector_chain(llm, embeddings, NVDNeo4j.vector)
# tag::tools[]
tools = [
    StructuredTool.from_function(
        name="Asset Identification",
        description="Identiffies assets in a given item. It receives an item name as input and returns the list of identified assets",
        func=asset_chain,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="Damage Scenario Specification",
        description="Determines potential damage scenarios for a given set of assets. It receives a list of assets and their security properties as input and returns the damage scenarios.",
        func=damage_chain,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="Cyber threat Scenario Specification",
        description="Determines potential threat scenarios for a given set of assets. It receives a list of assets and their security properties as input and returns the threat scenarios.",
        func=threat_chain,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="Attack Path Specification",
        description="Determines potential attack paths for a given set of threat scenarios. It receives a list of threat scenarios as input and returns the attack paths.",
        func=attack_path_chain,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="Goal Specification",
        description="Determines potential goals for improving the cybersecurity of a given set of assets. It receives a list of assets and their foreseen threat scenarios as input and returns the goals.",
        func=goal_chain,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="SystemWeaver Vector Search Index",
        description="Provides information about an individual SystemWeaver item using Vector Search",
        func=sw_vector_chain.run,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="MITRE Att&ck Vector Search Index",
        description="Provides information about an individual MITRE Att&ck entry using Vector Search",
        func=attack_vector_chain.run,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="NVD Vector Search Index",
        description="Provides information about an individual NVD entry using Vector Search",
        func=nvd_vector_chain.run,
        return_direct=True,
    ), 
]
# end::tools[]


# tag::memory[]
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True,
    input_key="input",
    output_key="output",
)


# tag::agent[]
agent_prompt = PromptTemplate.from_template(
    """
You are an automotive cybersecurity expert with knowledge about ISO 21434.
You are supposed to help users perform Threat Analysis and Risk Assessment (TARA).
TARA consists of several steps including 1. item definition, 2. asset identification, 3. damage scenario specification.
You have access to the following tools, where each tool is dedicated to a specific step in the TARA process:

{tools}

Use the following format to help users:

Input: the info about the TARA step and the data needed to execute the step
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: your response to the user request

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
)
agent = create_react_agent(
    llm,
    tools,
    agent_prompt,
)
""" agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
) """
agent_executor = AgentExecutor(
    agent=agent, tools=tools, memory=memory, verbose=True, handle_parsing_errors=True
)
# end::agent[]


# tag::generate_response[]
def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = agent_executor.invoke({"input":prompt})
    
    return response["output"]


# end::generate_response[]


"""

The `generate_response()` method can be called from the `handle_submit()` method in `bot.py`:

# tag::import[]
from agent import generate_response
# end::import[]

# tag::submit[]
# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('Thinking...'):

        response = generate_response(message)
        write_message('assistant', response)
# end::submit[]

"""
