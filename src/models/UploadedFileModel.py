from .BaseDataModel import BaseDataModel
from .db_schemes.uploaded_file import UploadedFile
from .enums.DatabaseEnums import DataBaseEnum


class UploadedFileModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_FILE_NAME.value]

    async def create_file_record(self, uploaded_file: UploadedFile):
        result = await self.collection.insert_one(uploaded_file.model_dump())
        uploaded_file._id = result.inserted_id
        return uploaded_file
