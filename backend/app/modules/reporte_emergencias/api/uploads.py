import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

router = APIRouter(prefix="/upload", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")


@router.post("", status_code=status.HTTP_201_CREATED)
def upload_file(request: Request, file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Generate a safe, unique filename
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not save file: {exc}") from exc

    # Return full URL
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/uploads/{unique_name}"

    return {"file_url": file_url}
