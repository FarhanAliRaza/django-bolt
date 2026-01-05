from typing import Annotated

import msgspec

from core.models import Blog, Document
from django_bolt import BoltAPI, FileSize, UploadFile
from django_bolt.params import File, Form

api = BoltAPI(prefix="/blogs")


class BlogSerializer(msgspec.Struct):
    name: str
    description: str
    status: str


@api.get("/")
async def get_blogs() -> list[BlogSerializer]:
    return Blog.objects.filter(status="published")


@api.post("/")
async def create_blog(blog: BlogSerializer):
    return {"blog": blog}


# ============ File Upload APIs ============

files_api = BoltAPI()


class DocumentResponse(msgspec.Struct):
    id: int
    title: str
    url: str


@files_api.post("/upload")
async def upload_document(
    title: Annotated[str, Form()],
    file: Annotated[UploadFile, File(max_size=FileSize.MB_30, allowed_types=["application/pdf", "image/*"])],
) -> DocumentResponse:
    """
    Upload a document with validation.

    - Max size: 1MB
    - Allowed types: PDF and images
    """
    doc = Document(title=title)
    doc.file.save(file.filename, file.file, save=False)
    await doc.asave()

    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        url=doc.file.url,
    )


class MultiUploadResponse(msgspec.Struct):
    count: int
    filenames: list[str]
    total_size: int


@files_api.post("/upload-multiple")
async def upload_multiple_files(
    files: Annotated[list[UploadFile], File(max_files=5, max_size=FileSize.MB_1)],
) -> MultiUploadResponse:
    """
    Upload multiple files at once.

    - Max 5 files
    - Max 1MB per file
    """
    filenames = []
    total_size = 0

    for f in files:
        filenames.append(f.filename)
        total_size += f.size

    return MultiUploadResponse(
        count=len(files),
        filenames=filenames,
        total_size=total_size,
    )


api.mount("/files", files_api)
