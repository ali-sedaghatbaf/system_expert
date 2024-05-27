from functools import cache
import nvdlib
import datetime
@cache
class NVD:

    def __init__(self, database="CVE") -> None:
        self.db = database

    def fetch_data(self, timestamp):
        
        endDate = timestamp+datetime.timedelta(days=7)
        if self.db == "CVE":
            data = nvdlib.searchCVE(lastModStartDate =timestamp.strftime("%Y-%m-%d %H:%M"),lastModEndDate = endDate.strftime("%Y-%m-%d %H:%M"), verbose=True)
            return [{"id":d.id, "description":d.descriptions[0].value} for d in data]
        
        data = nvdlib.searchCPE(lastModStartDate =timestamp.strftime("%Y-%m-%d %H:%M"), lastModEndDate = endDate.strftime("%Y-%m-%d %H:%M"), verbose=True)
        print(data[:3])
        return [{"id":d.cpeName, "description":d.titles[0].title} for d in data]
        
        
        
