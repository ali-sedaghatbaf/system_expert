

from fastapi import FastAPI, Query
from pydantic import BaseModel
from llm.tara_agent import generate_response
import ast
from typing import Dict, Annotated
app = FastAPI(debug=True)
@app.get("/")
def index():
    return {"hello":"world"}

@app.post("/asset_identification")
def identify_assets(elements:Annotated[list[str] | None, Query()], security_properties:Annotated[list[str] | None, Query()]):  
    llm_feedback_str = generate_response(f"Identify assets whithin the following list of elements {elements} considering {security_properties} as security properties")                   
    llm_feedback = ast.literal_eval(llm_feedback_str)["elements"]
    result = []
    for el in llm_feedback:
        data_els = {"Name":el["name"],"Is Asset": el["is_asset"]}        
        for p in security_properties:
            p_l = p.lower().replace("-","_")                         
            data_els[p] = el[p_l]           
        result.append(data_els)   
    return result       
    