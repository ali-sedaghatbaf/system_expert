import requests
import json
import xmltodict
import re
from xml.etree.ElementTree import ElementTree
import clr
clr.AddReference("SystemWeaverClientAPI")
from functools import cache
from SystemWeaverAPI import *
from SystemWeaver.Common import *

@cache
class SWClient:
    def __init__(self, server, port) -> None:
        self.server = server
        self.port = port

    def authenticate(self, auth_data):       
        
        
        SWConnection.Instance.LoginName = auth_data["username"]
        SWConnection.Instance.Password = auth_data["password"]
        SWConnection.Instance.ServerMachineName = self.server
        SWConnection.Instance.ServerPort = self.port
        SWConnection.Instance.AuthenticationMethod = AuthenticationMethod.NetworkAuthentication
        
        SWConnection.Instance.Login(getattr(EventSynchronization,'None'))
        

    def import_data(self, item_handle):
        
        if SWConnection.Instance.Connected:
            handle = SWHandleUtility.ToHandle(item_handle)
            item = SWConnection.Instance.Broker.GetItem(handle)
            item_data = {"handle": item_handle}
            items = {item_handle: item_data}
            item_data["name"] = item.Name
            item_data["description"] = SWDescription.DescriptionToPlainText(item.Description, item.Broker);
            item_data["type"] = "Item:" + format_sw_type(item.swType.Name) 
            item_data["attributes"] = []
            for attr in item.Attributes:
                attr_data = {}
                attr_data["name"] = attr.AttributeType.Name.replace(" ", "_")
                attr_data["value"] = attr.ValueAsString
                item_data["attributes"].append(attr_data)
            item_data["parts"] = {}
            parts =  item.GetAllParts()
            
            for p in parts:
                part = IswPart(p)
                child_handle = part.DefObj.HandleStr

                items.update(self.import_data(child_handle))
                part_type = format_sw_type(part.swType.Name)

                item_data["parts"][child_handle] = part_type
          
        return items
    
    def export_data(self, data):
        
        if SWConnection.Instance.Connected:
            if "assets" in data:       
                parent_item = self.__get_item_by_handle(data["item_handle"])         
                for a in data["assets"].values():
                    asset_item = self.__get_item_by_handle(a[0])                          
                    self.__add_item(parent_item, asset_item, "SP0261")
                if "damages" in data:                    
                    for d in data["damages"]:
                        damage_item = self.__create_item(parent_item, "Damage scenario for "+d[0], "SI0168","SP0270")
                        asset_name = d[0]
                        asset_item = self.__get_item_by_handle(data["assets"][asset_name])      
                        self.__add_item(damage_item, asset_item, "SP0260")      
                        for default_attr in damage_item.swItemType.GetAllDefaultAttributes():
                            attrObj = IswDefaultAttribute(default_attr).AttrType
                            if attrObj.DataType.ToString().lower() != "computed":
                                dynType = self.__get_attrtype_by_handle(attrObj.HandleStr)
                                attr = damage_item.GetOrMakeAttributeOfType(dynType)
                                if attr.AttributeType.SID == "SA0054":#safety impact
                                    attr.ValueAsString = d[2]
                                elif attr.AttributeType.SID == "SA0055":# privacy impact
                                    attr.ValueAsString = d[3]
                                elif attr.AttributeType.SID == "SA0053":#finncial impact
                                    attr.ValueAsString = d[4]
                                elif attr.AttributeType.SID == "SA0052":# operational impact
                                    attr.ValueAsString = d[5]
                        for attr in damage_item.Attributes:                            
                            if attr.AttributeType.SID == "SA0520":
                                attr.ValueAsString = d[1]
                            

    def __get_attrtype_by_handle(self, attr_handle):
        handle = SWHandleUtility.ToHandle(attr_handle)
        return SWConnection.Instance.Broker.GetAttributeType(handle)
    
    def __get_item_by_handle(self, item_handle):
        handle = SWHandleUtility.ToHandle(item_handle)
        return SWConnection.Instance.Broker.GetItem(handle)
    
    def __add_item(self, p_item, item, part_SID):        
        part_type = p_item.Broker.FindPartTypeWithSID(part_SID)
        if part_type.Multiplicity == SWMultiplicity.Single:
            p_item.SetPartObj(part_SID, item)
        else:
            p_item.AddPart(part_SID, item)
                
    def __create_item(self, p_item, item_name, item_SID, part_SID):
        cyberLib = SWConnection.Instance.Broker.GetLibrary(SWHandleUtility.ToHandle("x1300000000000CDE"))                
        item = cyberLib.CreateItem(item_SID, item_name)        
        
        part_type = p_item.Broker.FindPartTypeWithSID(part_SID)
        if part_type.Multiplicity == SWMultiplicity.Single:
            p_item.SetPartObj(part_SID, item)
        else:
            p_item.AddPart(part_SID, item)
        return item

@cache
class SWREST:
    def __init__(self, server, port) -> None:
        self.server = server
        self.port = port

    def authenticate(self, auth_data):
        auth_response = requests.post(
            f"http://{self.server}:{self.port}/token", data=auth_data
        ).json()
        
        self.auth_token = auth_response["access_token"]

    def import_data(self, item_handle):

        headers = {"Authorization": "Bearer " + self.auth_token}
        input_data = requests.get(
            f"http://{self.server}:{self.port}/restapi/items/" + item_handle,
            headers=headers,
        ).json()
        if "exceptionType" in input_data:
            raise Exception("item with the specified handle not found.")
        item_data = {"handle": item_handle}

        items = {item_handle: item_data}

        item_data["name"] = input_data["name"]
        item_data["description"] = requests.get(
            f"http://{self.server}:{self.port}/restapi/descriptions/" + item_handle,
            headers=headers,
        ).json()["description"]
        item_data["type"] = "Item:" + format_sw_type(input_data["type"]["name"])
        # item_types = [input_data["type"]["name"]]

        # item_types.extend(self.__get_type_hierrchy(input_data["type"]["sid"]))

        # item_data["type"] = ":".join(
        #    [format_sw_type(item_type) for item_type in item_types]
        # )
        # print(item_data["type"])
        # embedding_text = (
        #    f"handle: {item_handle}\nname:{item_data['name']}\ntype:{item_data['type']}\n"
        # )
        item_data["attributes"] = []
        for attr in input_data["attributes"]:
            attr_data = {}
            attr_data["name"] = attr["attributeType"]["name"].replace(" ", "_")
            attr_data["value"] = attr["value"]
            item_data["attributes"].append(attr_data)
        #    embedding_text += f"{attr_data['name']}: {attr_data['value']}\n"
        item_data["parts"] = {}
        for part in input_data["parts"]:
            child_handle = part["defObject"]["handle"]

            items.update(self.import_data(child_handle))
            part_type = format_sw_type(part["type"]["name"])

            item_data["parts"][child_handle] = part_type
        #    embedding_text += f"{part["defObject"]["name"]}: {part_type}\n"

        # item_data['embedding'] = embeddings.embed_query(embedding_text)

        return items

    def __get_type_hierrchy(self, type_sid):

        type_list = []

        if self.item_types and type_sid in self.item_types:

            cur_sid = type_sid
            while True:

                cur_sid = self.item_types[cur_sid]["parent"]
                if cur_sid and cur_sid in self.item_types:
                    cur_type = self.item_types[cur_sid]["name"]

                    type_list.append(cur_type)
                else:
                    break

        return type_list

    def get_item_types(self, metamodel):

        tree = ElementTree()
        tree.parse(metamodel)
        root = tree.getroot()
        types_element = root[1][0][1]
        self.item_types = {}
        if types_element.tag == "ItemTypes":
            for type_element in types_element:
                name = type_element[0].text
                sid = type_element.attrib["sid"]
                parent = type_element.attrib["parent"]
                self.item_types[sid] = {"name": name, "parent": parent}


def format_sw_type(sw_type):
    # return "`" + sw_type + "`"

    return re.sub(
        r"\([^)]*\)",
        "",
        sw_type
    ).strip().replace(" ", "_").replace("/", "_or_").replace("-", "_").replace("&", "_and_")


def dump_xml(items):
    for item in items.values():
        xml_data = xmltodict.unparse({"item": item}, pretty=True)
        with open("./xml_data/" + item["handle"] + ".xml", "w") as xml_file:
            xml_file.write(xml_data)


def dump_json(items):
    file_name = "data.json"

    with open(file_name, "w") as json_file:
        json.dump(items.values(), json_file)
