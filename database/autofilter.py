import re

from config import Config
from logger import LOGGER
from pymongo.errors import BulkWriteError, DuplicateKeyError
from utils.tools import unpack_new_file_id

from .mongoDB import MongoDb

logger = LOGGER('AUTO_FILTER_DB')

class FiltersDb(MongoDb):
    
    def __init__(self):
        super().__init__()
        self.col = self.get_collection(Config.COLLECTION_NAME)
        self.data = []


    async def insert_many(self, media):
        file = await self.file_dict(media)
        self.data.append(file)
        if len(self.data) >= 200:
            try:
                insert = await self.col.insert_many(self.data, ordered=False)
            except BulkWriteError as e:
                inserted = e.details['nInserted']
            else:
                inserted = len(insert.inserted_ids)
            duplicate = len(self.data) - inserted
            self.data.clear()
            return inserted, duplicate
            
        logger.info(f'{getattr(media, "file_name", "NO_FILE")} is updated in database')
        return None, None


    async def file_dict(self, media):
        file_id, _ = unpack_new_file_id(media.file_id)
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        return  dict(
            _id=file_id,
            file_name=file_name,
            file_size=media.file_size,
            chat_id = media.chat_id,
            message_id = media.message_id,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    

    async def save_file(self, media):
        """Save file in database"""
        file = await self.file_dict(media)
        try:
            await self.col.insert_one(file)
        except DuplicateKeyError:
            logger.warning(
                    f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
                )
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1


    async def get_search_results(self, query: str, file_type: str=None, max_results: int =10, offset: int =0, filter: bool =False):
        """For given query return (results, next_offset)"""

        query = query.strip()

        if not query:
            raw_pattern = '.'
        elif ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
        
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []

        if Config.USE_CAPTION_FILTER:
            filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
        else:
            filter = {'file_name': regex}

        if file_type:
            filter['file_type'] = file_type

        total_results = await self.col.count_documents(filter)
        next_offset = offset + max_results

        if next_offset > total_results:
            next_offset = ''

        cursor = self.col.find(filter)
        # Sort by recent
        cursor.sort('$natural', -1)
        # Slice files according to offset and max results
        cursor.skip(offset)
        cursor.limit(max_results)
        # Get list of files
        files = await cursor.to_list(length=max_results)

        return files, next_offset, total_results



    async def get_file_details(self, file_id: str):
        return await self.col.find_one({'_id': file_id})


a_filter = FiltersDb()
