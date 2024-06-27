from fastapi import FastAPI, Query
from pydantic import Field, BaseModel
from llm.tara_agent import TaraAgent
import ast
from typing import Dict, Annotated


class Description(BaseModel):
    PlainText: str
    Text: str


class Attribute(BaseModel):
    Sid: str
    PlainText: str
    Text: str


class DefObj(BaseModel):
    Handle: str


class Part(BaseModel):
    Handle: str
    Ancestor: str
    Name: str
    No: int
    DefObj: DefObj
    Attributes: list[Attribute] | None


class PartGroup(BaseModel):
    Sid: str
    Name: str
    Parts: list[Part]


class Item(BaseModel):
    Handle: str
    Sid: str
    Type: str
    Ancestor: str
    Name: str
    VersionText: str | None
    VersionNumber: int
    Status: str
    Description: Description
    Attributes: list[Attribute] | None
    PartGroups: list[PartGroup] | None


class SecurityProperties(BaseModel):
    Confidentiality: bool
    Integrity: bool
    Availability: bool
    NonRepudiation: bool


class Parameters(BaseModel):
    SecurityProperties: SecurityProperties


class ItemDefinition(BaseModel):
    Items: list[Item]
    Parameters: Parameters


class SystemModel(BaseModel):
    Handle: str


class Asset(BaseModel):
    Handle: str
    Name: str
    IsAsset: bool
    Properties: Dict[str, bool]
    Rationale: str


class AssetIdentification(BaseModel):
    SystemModel: SystemModel
    Assets: list[Asset]


app = FastAPI(debug=True)
app.item_def = None


@app.post("/item_definition")
def post_item(input_data: ItemDefinition):
    app.item_def = input_data
    return {}


@app.get("/asset_identification", response_model=AssetIdentification)
def get_assets():
    items = [
        item
        for item in app.item_def.Items
        if item.Type == "Conceptual System/Component"
    ]
    security_properties = [
        p for p, v in app.item_def.Parameters.SecurityProperties if v == True
    ]
    elements = [{"name": d.Name, "description": d.Description.Text} for d in items]

    tara_agent = TaraAgent()
    llm_feedback_str = tara_agent.generate_response(
        f"Identify assets whithin the following list of elements {elements} considering {security_properties} as security properties"
    )
    llm_feedback = ast.literal_eval(llm_feedback_str)["elements"]

    output_data = AssetIdentification(
        SystemModel=SystemModel(Handle=app.item_def.Items[0].Handle), Assets=[]
    )

    for ind, el in enumerate(llm_feedback):
        asset = Asset(
            Handle=app.item_def.Items[ind + 1].Handle,
            Name=el["name"],
            IsAsset=el["is_asset"],
            Properties=dict(),
            Rationale="",
        )

        reason_str = "Asset: " + el["asset_reason"]
        for p in security_properties:
            p_l = p.lower().replace("-", "_")
            asset.Properties[p] = el[p_l]
            reason_str += "\n" + p + ": " + el[p_l + "_reason"]
        asset.Rationale = reason_str

        output_data.Assets.append(asset)

    return output_data
