from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_models import BedrockChat
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
import streamlit as st
import pdfkit
from pdfkit.api import configuration
import pandas as pd 
from enum import StrEnum
import itertools

def split_list(lst, val):
    return [list(group) for k, group in
            itertools.groupby(lst, lambda x: x==val) if not k]


class ImpactEnum(StrEnum):
    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

def section_text(title, data):
    return f"<h4>{title}</h4><div class='data-desc'>{data.to_html(justify="center", index=False)} </div>"

def add_line_breaks(text):
    return text.replace('\n', '<br>')

def save_as_pdf(data):
    ## Paste the path of WKHTML.exe from Files
    wkhtml_path = pdfkit.configuration(wkhtmltopdf = st.secrets["WKHTMLTOPDF"])
    options = {"enable-local-file-access":""} ## Access local files in .png/.jpeg format
    item = data.selected_item["item_name"]

    report_data = [section_text("2. Asset Identification", data.assets.loc[:, data.assets.columns != "Rationale"])]
    if "damages" in data:
        report_data.append(section_text("3. Damage Scenario Specification", data.damages.loc[:, data.damages.columns != "Rationale"]))
        if "threats" in data:
            report_data.append(section_text("4. Threat Scenario Specification", data.threats.loc[:, data.threats.columns != "Rationale"]))

    report_content = f"""
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TARA Report</title>
            <link rel="stylesheet" href=".\\style.css">
        </head>
        <body>
            <br>
            <h1>TARA Report</h1>
            
            <br>
            <h3>1. Item Definition</h3>
            <p>{item}</p>
            
            {"".join(report_data)}
            
    </body>
    </html>   
    """
    # Save above HTML skeleton into .html file
    with open("report.html", "w") as f:
        f.write(report_content)
    pdfkit.from_file('report.html', 'report.pdf', configuration=wkhtml_path, options=options)

class BaseLogger:
    def __init__(self) -> None:
        self.info = print


ollama_base_url = st.secrets["OLLAMA_BASE_URL"]
embedding_model_name = st.secrets["EMBEDDING_MODEL"]
llm_name = st.secrets["LLM"]


def load_embedding_model(
    embedding_model_name=embedding_model_name,
    logger=BaseLogger(),
    config={"ollama_base_url": ollama_base_url},
):
    if embedding_model_name == "ollama":
        embeddings = OllamaEmbeddings(
            base_url=config["ollama_base_url"], model=llm_name
        )
        dimension = 4096
        logger.info("Embedding: Using Ollama")
    elif embedding_model_name == "openai":
        embeddings = OpenAIEmbeddings()
        dimension = 1536
        logger.info("Embedding: Using OpenAI")
    elif embedding_model_name == "aws":
        embeddings = BedrockEmbeddings()
        dimension = 1536
        logger.info("Embedding: Using AWS")
    else:
        embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2", cache_folder="/embedding_model"
        )
        dimension = 384
        logger.info("Embedding: Using SentenceTransformer")
    return embeddings, dimension


def load_llm(
    llm_name=llm_name, logger=BaseLogger(), config={"ollama_base_url": ollama_base_url}
):
    if llm_name == "gpt-4":
        logger.info("LLM: Using GPT-4")
        return ChatOpenAI(temperature=0, model_name="gpt-4", streaming=True)
    elif llm_name == "gpt-3.5":
        logger.info("LLM: Using GPT-3.5")
        return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True)
    elif llm_name == "claudev2":
        logger.info("LLM: ClaudeV2")
        return BedrockChat(
            model_id="anthropic.claude-v2",
            model_kwargs={"temperature": 0.0, "max_tokens_to_sample": 1024},
            streaming=True,
        )
    elif len(llm_name):
        logger.info(f"LLM: Using Ollama: {llm_name}")
        return ChatOllama(
            temperature=0,
            base_url=config["ollama_base_url"],
            model=llm_name,
            streaming=True,
            # seed=2,
            top_k=10,  # A higher value (100) will give more diverse answers, while a lower value (10) will be more conservative.
            top_p=0.3,  # Higher value (0.95) will lead to more diverse text, while a lower value (0.5) will generate more focused text.
            num_ctx=3072,  # Sets the size of the context window used to generate the next token.
        )
    logger.info("LLM: Using GPT-3.5")
    return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True)

