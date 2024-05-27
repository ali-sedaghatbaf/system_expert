import requests


input = {"elements":["Camera ECU", "Gateway ECU"],
         "security_properties":["Confidentiality", "Integrity"]}
print(requests.post("http://localhost:8000/asset_identification", params=input).json())
