import os
import requests
from dotenv import load_dotenv, find_dotenv
from langchain_community.graphs import Neo4jGraph
import streamlit as st
from streamlit.logger import get_logger

from st_pages import add_page_title, add_indentation
from adapters.neo4j_adapter import SWNeo4j
from adapters.sw_adapter import SWREST, SWClient
import traceback

st.set_page_config("SystemWeaver Data Loader", page_icon=":copilot:",layout="wide")


logger = get_logger(__name__)


# Streamlit
# add_indentation()


def get_server():
    col1, col2, _,_ = st.columns(4)
    with col1:
        address = st.text_input("Server address", value=st.secrets["SW_SERVER"])
    with col2:
        port = st.number_input("Server port", step=1, value=st.session_state.default_port)

    return address, int(port)


def get_credentials():
    col1, col2, _, _ = st.columns(4)
    with col1:
        username = st.text_input("Username", value=st.secrets["SW_USERNAME"])
    with col2:
        password = st.text_input("Password", type="password", value="SW_PASSWORD")
    
    return username, password


    

def get_api_handle():
    col1,col2,_,_ = st.columns(4)
    with col1:
        option = st.selectbox(
            "SystemWeaver API",
            ["Client API", "REST API"],
            placeholder="Select API...",
            
        )
    with col2:
        handle = st.text_input("Item handle").split("/")[-1]
    return option, handle



def render_page():
    st.session_state.default_port = st.secrets["SW_PORT"]
    st.header("SystemWeaver Data Loader")
    st.divider()
    st.subheader("Connect to SystemWeaver and load data into SystemExpert")
    api, item_handle = get_api_handle()
    if api == "REST API":
        st.session_state.default_port = st.secrets["SW_REST_PORT"]
    
    server, port = get_server()

    username, password = get_credentials()
    
    
    auth_data = {
        "username": username,
        "windowsauthentication": "true",
        "password": password,
        "grant_type": "password",
    }
    
    
    if st.button("Import data"):
        sw_items = None
        neo4j = None
        with st.spinner("Connecting to SystemWeaver"):
            try:
                if api == "REST API":
                    sw_endpoint = SWREST(server, port)
                else:
                    sw_endpoint = SWClient(server, port)
                sw_endpoint.authenticate(auth_data)

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return
        with st.spinner("Fetching data from SystemWeaver"):
            
            try:               

                sw_items = sw_endpoint.import_data(item_handle)
               


            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Connecting to Neo4j"):
            try:

                neo4j = SWNeo4j()

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Inserting data into Neo4j"):
            try:

                neo4j.insert_data(sw_items)
                col1,_ = st.columns(2)
                with col1:
                    st.success("Import successful", icon="✅")

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")


render_page()
