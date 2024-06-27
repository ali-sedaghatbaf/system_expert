# tag::importtool[]
import langchain
from langchain.tools import Tool, StructuredTool
from langchain import hub
import streamlit as st
from functools import cache

# end::importtool[]
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
    initialize_agent,
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
from utils import load_embedding_model, load_llm
from llm import chains
from adapters.neo4j_adapter import SWNeo4j, MITRENeo4j, NVDNeo4j

langchain.debug = True


@cache
class ChatAgent:
    def __init__(self) -> None:
        embeddings, _ = load_embedding_model()
        llm = load_llm()

        llm_chain = chains.configure_llm_only_chain(llm)
        sw_vector_chain = chains.configure_llm_vector_chain(
            llm, embeddings, SWNeo4j.vector
        )
        attack_vector_chain = chains.configure_llm_vector_chain(
            llm, embeddings, MITRENeo4j.vector
        )
        nvd_vector_chain = chains.configure_llm_vector_chain(
            llm, embeddings, NVDNeo4j.vector
        )
        cypher_chain = chains.configure_llm_cypher_chain(llm)
        # tag::tools[]
        tools = [
            Tool.from_function(
                name="Graph Search",
                description="Provides information about itens and their relations using Graph Search",
                func=cypher_chain.run,
                return_direct=True,
            ),
            Tool.from_function(
                name="SystemWeaver Vector Search Index",
                description="Provides information about an individual SystemWeaver item using Vector Search",
                func=sw_vector_chain.run,
                return_direct=True,
            ),
            Tool.from_function(
                name="Att&ck Vector Search Index",
                description="Provides information about an individual Att&ck entry using Vector Search",
                func=attack_vector_chain.run,
                return_direct=True,
            ),
            Tool.from_function(
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
        SW stands for SystemWeaver and you are a cybersecurity expert having access to SystemWeaver database.
        Answer the following questions as best you can. You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

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
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
        )
        # end::agent[]

    def generate_response(self, prompt):
        """
        Create a handler that calls the Conversational agent
        and returns a response to be rendered in the UI
        """

        response = self.agent_executor.invoke({"input": prompt})

        return response["output"]
