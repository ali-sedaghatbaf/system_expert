import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
from adapters.neo4j_adapter import SWNeo4j

import traceback
from llm.tara_agent import TaraAgent
import ast
import utils

st.set_page_config("TARA Assistant", page_icon=":copilot:", layout="wide")


logger = get_logger(__name__)


def get_item_defs():
    neo4j = SWNeo4j()
    # neo4j.add_attack_graph()

    st.session_state.item_defs = [
        {
            "item_name": d["item_name"],
            "item_handle": d["item_handle"],
            "tara_name": d["tara_name"],
            "tara_handle": d["tara_handle"],
        }
        for d in neo4j.find_item_definitions()
    ]


def get_assets():
    neo4j = SWNeo4j()  # cached
    tara_handle = st.session_state.selected_item["tara_handle"]
    st.session_state.security_properties = [
        p["p_name"].capitalize() for p in neo4j.find_security_properties(tara_handle)
    ]

    cols = ["Element Name", "Is Asset"]
    cols.extend(st.session_state.security_properties)
    cols.append("Rationale")

    data_df = pd.DataFrame(columns=cols)
    query_results = [
        d for d in neo4j.find_item_elements(st.session_state.selected_item["item_name"])
    ][:1]
    st.session_state.system_elements = {
        n["node_id"]: {
            "element_name": n["node_name"],
            "element_description": n["node_description"],
        }
        for n in query_results
    }

    st.session_state.system_relations = [
        dict(
            source_element=result["rel_start"],
            relation_type=result["rel_type"],
            target_element=result["rel_end"],
        )
        for result in query_results
    ]
    tara_agent = TaraAgent()
    llm_feedback_str = tara_agent.generate_response(
        f"""Identify assets whithin the following list of elements {st.session_state.system_elements.values()} 
        considering {st.session_state.system_relations} as the thir relationships and {st.session_state.security_properties} as security properties
        """
    )

    llm_feedback = ast.literal_eval(llm_feedback_str)["elements"]

    for el in llm_feedback:
        data_els = [el["name"], el["is_asset"]]
        reason_str = "Asset: " + el["asset_reason"]
        for p in st.session_state.security_properties:
            p_l = p.lower().replace("-", "_")
            data_els.append(el[p_l])
            reason_str += "\n" + p + ": " + el[p_l + "_reason"]
        data_els.append(reason_str)

        data_df.loc[len(data_df.index)] = data_els
    st.session_state.assets = data_df


def get_threats():
    data_df = pd.DataFrame(
        columns=[
            "Asset Name",
            "Threat Scenario",
            "Affected Properties",
        ]
    )
    tara_agent = TaraAgent()
    llm_feedback = tara_agent.generate_response(
        f"Specify cyber threat scenarios for each of the following assets {st.session_state.assets}."
    )

    llm_feedback = ast.literal_eval(llm_feedback)["scenarios"]

    for el in llm_feedback:
        data_df.loc[len(data_df.index)] = [
            el["asset_name"],
            el["scenario_description"],
            el["affected_properties"],
        ]
    st.session_state.threats = data_df


def get_damages():
    data_df = pd.DataFrame(
        columns=[
            "Asset Name",
            "Threat Scenario",
            "Damage Scenario",
            "Safety Impact",
            "Privacy Impact",
            "Financial Impact",
            "Operational Impact",
            "Rationale",
        ]
    )
    tara_agent = TaraAgent()
    llm_feedback = tara_agent.generate_response(
        f"Specify damage scenarios for each of the following threats {st.session_state.threats}."
    )

    llm_feedback = ast.literal_eval(llm_feedback)["scenarios"]
    for el in llm_feedback:
        data_df.loc[len(data_df.index)] = [
            el["asset_name"],
            el["threat_scenario"],
            el["damage_scenario"],
            el["safety_impact"],
            el["privacy_impact"],
            el["financial_impact"],
            el["operational_impact"],
            "Safety: "
            + el["safety_reason"]
            + "\nPrivacy: "
            + el["privacy_reason"]
            + "\nFinancial: "
            + el["fin_reason"]
            + "\nOperational: "
            + el["op_reason"],
        ]
    st.session_state.damages = data_df


def get_attack_paths():
    data_df = pd.DataFrame(
        columns=[
            "Asset Name",
            "Threat Scenario",
            "Attack Path",
            "Elapsed Time",
            "Equipment",
            "Knowledge",
            "Expertise",
            "Window of Opportunity",
            "Rationale",
        ]
    )
    tara_agent = TaraAgent()
    llm_feedback = tara_agent.generate_response(
        f"Specify worst-case attack paths for each of the following cyber threats {st.session_state.threats}."
    )

    llm_feedback = ast.literal_eval(llm_feedback)["paths"]

    for el in llm_feedback:
        data_df.loc[len(data_df.index)] = [
            el["asset_name"],
            el["threat_scenario"],
            el["attack_path"],
            el["elapsed_time"],
            el["equipment"],
            el["knowledge"],
            el["expertise"],
            el["window"],
            "Elapsed Time: "
            + el["elapsed_time_reason"]
            + "\nEquipment: "
            + el["equipment_reason"]
            + "\nKnowledge: "
            + el["knowledge_reason"]
            + "\nExpertise: "
            + el["expertise_reason"]
            + "\nWindow: "
            + el["window_reason"],
        ]
    st.session_state.attack_paths = data_df


def get_goals():
    data_df = pd.DataFrame(
        columns=[
            "Asset Name",
            "Threat Scenario",
            "Goal",
            "Requirements",
        ]
    )
    tara_agent = TaraAgent()
    llm_feedback = tara_agent.generate_response(
        f"Specify cyber security goals for reducing the risl of each of the following threats {st.session_state.threats}."
    )

    llm_feedback = ast.literal_eval(llm_feedback)["goals"]

    for el in llm_feedback:
        data_df.loc[len(data_df.index)] = [
            el["asset_name"],
            el["threat_scenario"],
            el["goal"],
            el["requirements"],
        ]
    st.session_state.goals = data_df


def render_page():

    st.header("TARA Assistant")
    st.divider()
    col1, _ = st.columns(2)
    col1.markdown(
        """<span style="word-wrap:break-word;">TARA stands for Threat Analysis and Risk Assessment, and it's one of the key components of ISO 21434. 
        TARA includes several activities that help us identify security threats to road vehicles and develop appropriate protective measures.
        SystemExpert's TARA Assistant helps you perform those activities efficientily.</span>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("1. Item Definition")

    if "item_defs" not in st.session_state:
        with st.spinner("Loading item definitions..."):
            try:
                get_item_defs()

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

    st.markdown("Pleae select an item definition from the list below.")
    st.session_state.selected_item = get_item()
    if st.session_state.selected_item:
        st.subheader("2. Asset Identification")

        if "assets" not in st.session_state:

            with st.spinner("Identifying assets..."):

                try:

                    get_assets()

                except Exception as e:
                    st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                    return
        st.markdown(
            "SystemExpert has come up with the following list of assets for the selected item.\nPlease make appropriate adjustments and approve the list to move to the next step."
        )

        st.session_state.assets = view_assets()

        st.session_state.assets_confirmed = st.checkbox(
            "I approve the results and would like to go to the next step.",
            value="assets_confirmed" in st.session_state
            and st.session_state.assets_confirmed,
            key="confirm_assets",
        )
        if st.session_state.assets_confirmed:

            st.subheader("3. Threat Identification")

            if "threats" not in st.session_state:

                with st.spinner("Specifying threat scenarios..."):

                    try:

                        get_threats()

                    except Exception as e:
                        st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                        return
            st.markdown(
                "SystemExpert has come up with the following list of threat scenarios for the assets.\nPlease make appropriate adjustments and approve the list to move to the next step."
            )
            st.session_state.threats = view_threats()
            st.session_state.threats_confirmed = st.checkbox(
                "I approve the results and would like to go to the next step.",
                value="threats_confirmed" in st.session_state
                and st.session_state.threats_confirmed,
                key="confirm_threats",
            )
            if st.session_state.threats_confirmed:

                st.subheader("4. Impact Analysis")

                if "damages" not in st.session_state:

                    with st.spinner(
                        " Specifying damage scenarios and analyzing their impacts..."
                    ):

                        try:

                            get_damages()

                        except Exception as e:
                            st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                            return
                st.markdown(
                    "SystemExpert has come up with the following list of damage scenarios for the assets.\nPlease make appropriate adjustments and approve the list to move to the next step."
                )
                st.session_state.damages = view_damages()
                st.session_state.damages_confirmed = st.checkbox(
                    "I approve the results and would like to go to the next step.",
                    value="damages_confirmed" in st.session_state
                    and st.session_state.damages_confirmed,
                    key="confirm_damages",
                )
                if st.session_state.damages_confirmed:

                    st.subheader("5. Attack Path Analysis")

                    if "attack_paths" not in st.session_state:

                        with st.spinner("Identifying attack paths..."):

                            try:

                                get_attack_paths()

                            except Exception as e:
                                st.error(
                                    f"Error: {e}\n{traceback.format_exc()}", icon="🚨"
                                )
                                return
                    st.markdown(
                        "SystemExpert has come up with the following list of attack paths for the threat scenarios.\nPlease make appropriate adjustments and approve the list to move to the next step."
                    )
                    st.session_state.attack_paths = view_attack_paths()
                    st.session_state.attack_paths_confirmed = st.checkbox(
                        "I approve the results and would like to go to the next step.",
                        value=False,
                        key="confirm_paths",
                    )
                    if st.session_state.attack_paths_confirmed:
                        st.subheader("6. Goal Identification")

                        if "goals" not in st.session_state:

                            with st.spinner("Specifying goals..."):

                                try:

                                    get_goals()

                                except Exception as e:
                                    st.error(
                                        f"Error: {e}\n{traceback.format_exc()}",
                                        icon="🚨",
                                    )
                                    return
                        st.markdown(
                            "SystemExpert has come up with the following list of goals for the assets."
                        )
                        st.session_state.goals = view_goals()
                    elif "goals" in st.session_state:
                        del st.session_state.goals
                elif "attack_paths" in st.session_state:
                    del st.session_state.attack_paths
            elif "damages" in st.session_state:
                del st.session_state.damages
        elif "threats" in st.session_state:
            del st.session_state.threats
        st.divider()

        utils.save_as_pdf(st.session_state)
        st.markdown(
            """
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            with open("report.pdf", "rb") as file:
                st.download_button(
                    label="Save as PDF", file_name="report.pdf", data=file
                )
        with col2:
            if st.button("Export to SystemWeaver"):

                st.switch_page("pages/7_SystemWeaver_Data_Exporter.py")

    elif "assets" in st.session_state:
        del st.session_state.assets


def view_attack_paths():
    return st.data_editor(
        st.session_state.attack_paths,
        column_config={
            "Asset Name": st.column_config.TextColumn("Asset Name", required=True),
            "Threat Scenario": st.column_config.TextColumn(
                "Threat Scenario", required=True
            ),
            "Attack Path": st.column_config.TextColumn("Attack Path", required=True),
            "Elapsed Time": st.column_config.SelectboxColumn(
                "Elapsed Time", required=True, options=utils.ElapsedTimeEnum.list()
            ),
            "Equipment": st.column_config.SelectboxColumn(
                "Equipment", required=True, options=utils.EquipmentEnum.list()
            ),
            "Knowledge": st.column_config.SelectboxColumn(
                "Knowledge", required=True, options=utils.KnowledgeEnum.list()
            ),
            "Expertise": st.column_config.SelectboxColumn(
                "Expertise", required=True, options=utils.ExpertiseEnum.list()
            ),
            "Window of Opportunity": st.column_config.SelectboxColumn(
                "Window of Opportunity", required=True, options=utils.WindowEnum.list()
            ),
        },
        hide_index=True,
        # num_rows="dynamic",
    )


def view_goals():

    return st.data_editor(
        st.session_state.goals,
        column_config={
            "Asset Name": st.column_config.TextColumn("Asset Name", required=True),
            "Threat Scenario": st.column_config.TextColumn(
                "Threat Scenario", required=True
            ),
            "Goals": st.column_config.TextColumn("Goals", required=True),
        },
        hide_index=True,
        # num_rows="dynamic",
    )


def view_threats():

    return st.data_editor(
        st.session_state.threats,
        column_config={
            "Asset Name": st.column_config.TextColumn("Asset Name", required=True),
            "Threat Scenario": st.column_config.TextColumn(
                "Threat Scenario", required=True
            ),
            "Affected Properties": st.column_config.TextColumn(
                "Affected Properties", required=True
            ),
        },
        hide_index=True,
        # num_rows="dynamic",
    )


def view_damages():

    return st.data_editor(
        st.session_state.damages,
        column_config={
            "Asset Name": st.column_config.TextColumn("Asset Name", required=True),
            "Damage Scenario": st.column_config.TextColumn(
                "Damage Scenario", required=True
            ),
            "Safety Impact": st.column_config.SelectboxColumn(
                "Safety Impact", required=True, options=utils.ImpactEnum.list()
            ),
            "Privacy Impact": st.column_config.SelectboxColumn(
                "Privacy Impact", required=True, options=utils.ImpactEnum.list()
            ),
            "Financial Impact": st.column_config.SelectboxColumn(
                "Financial Impact", required=True, options=utils.ImpactEnum.list()
            ),
            "Operational Impact": st.column_config.SelectboxColumn(
                "Operational Impact", required=True, options=utils.ImpactEnum.list()
            ),
        },
        hide_index=True,
        # num_rows="dynamic",
    )


def view_assets():
    config = {
        "Element Name": st.column_config.TextColumn(
            "Element Name", required=True, help="Name of the element"
        ),
        "Is Asset": st.column_config.CheckboxColumn(
            "Is Asset", required=True, help="Is the element an asset"
        ),
        "Rationale": st.column_config.TextColumn(
            "Rationale", required=True, help="Reasons provided by the AI agent"
        ),
    }

    for sp in st.session_state.security_properties:
        config[sp] = st.column_config.CheckboxColumn(
            sp,
            help="Specify whether " + sp + " is a security property of the asset",
            default=False,
        )

    return st.data_editor(
        st.session_state.assets,
        column_config=config,
        hide_index=True,
        # num_rows="dynamic",
    )


def item_changed():
    if "assets" in st.session_state:
        # if "selected_item" in st.session_state and option != st.session_state.selected_item["item_name"]:
        del st.session_state.assets


def get_item():

    col1, _, _, _ = st.columns(4)
    with col1:
        option = st.selectbox(
            "Available item definitions",
            [d["item_name"] for d in st.session_state.item_defs],
            index=(
                st.session_state.item_defs.index(st.session_state.selected_item)
                if "selected_item" in st.session_state
                and st.session_state.selected_item
                else None
            ),
            placeholder="Select item...",
            on_change=item_changed,
        )

    return (
        [df for df in st.session_state.item_defs if df["item_name"] == option][0]
        if option
        else None
    )


render_page()
