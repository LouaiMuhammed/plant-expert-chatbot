from fastapi import APIRouter, Depends, UploadFile, status, Request
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController # straight from init
from fastapi.responses import JSONResponse
import os 
import aiofiles
from pathlib import Path
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.db_schemes.uploaded_file import UploadedFile
from models.enums.DatabaseEnums import DataBaseEnum
from models.UploadedFileModel import UploadedFileModel
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk, Asset
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
) 
@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    uploaded_file_model = UploadedFileModel(
        db_client=request.app.db_client
    )
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : result_signal,

            } 
        )

    file_path = data_controller.generate_unique_filename(
        orig_file_name=file.filename,
        project_id=project_id
    )
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        
        logger.error(f'Error while uploading file: {e}')
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : ResponseSignal.FILE_UPLOAD_FAILED.value,
                "project_id": str(project.id)
            
            } 
        )

    stored_file_name = Path(file_path).name
    try:
        uploaded_file = await uploaded_file_model.create_file_record(
            UploadedFile(
                project_id=project.id,
                original_file_name=file.filename,
                stored_file_name=stored_file_name,
                file_path=file_path
            )
        )
    except Exception as e:
        logger.error(f'Error while saving uploaded file record: {e}')
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
                "project_id": str(project.id)
            }
        )
    # store assets into the database

    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type= AssetTypeEnum.FILE.value,
        asset_name=uploaded_file.stored_file_name,
        asset_size=os.path.getsize(file_path)

    )

    asset_record = await asset_model.create_asset(asset=asset_resource)
    return JSONResponse(
            content={
                "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": uploaded_file.stored_file_name,
                "project_id": str(project.id),
                "upload_id": str(uploaded_file._id)
            } 
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset


    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )

    project_file_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                content={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "signal": ResponseSignal.FILE_ID_ERROR.value

                }
            )

        project_file_ids = {
            asset_record.id: asset_record.asset_name
        }
   
    else:
        
        
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
        )
        project_file_ids = {
            record.id: record.asset_name
            for record in project_files
        }

        if len(project_file_ids) == 0:
            return JSONResponse(
                content={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "signal": ResponseSignal.NO_FILES_ERROR.value
                }
            )
        



    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
        )
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
            
        )
    for asset_id, file_id in project_file_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file:{file_id}")
            continue

        if file_content is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
                }
            )

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id

            )
            for i, chunk in enumerate(file_chunks)
        ]





        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCEEDED.value,
            "project_id": str(project.id),
            "file_id": file_id,
            "chunks_created": no_records,
            "processed_files": no_files
        }
    )
