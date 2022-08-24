from .mongoDB import MongoDb

class ConfigDB(MongoDb):
    
    def __init__(self):
        super().__init__()
        self.col = self.get_collection('configs')
    
    
    def new_config(self, key : str, value: str):
        return dict(
            key = key,
            value = value
        )
    
    
    async def update_config(self, key, value):
        return await self.col.update_one({'key': key}, {'$set': {'value': value}}, upsert=True)
    

    async def get_settings(self, key):
        config = await self.col.find_one({'key': key})
        if config:
            return config['value']
        return {}
    
config_db = ConfigDB()