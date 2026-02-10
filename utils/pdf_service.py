# core/services/pdf_service.py
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from fastapi import UploadFile


class PDFService:
    BASE_DIR = Path("assets")

    ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png"}
    PDF_EXT = ".pdf"

    # -------------------------
    # Public API
    # -------------------------

    @classmethod
    async def save_pdf(
        cls,
        *,
        owner_type: str,   # "racers", "events", etc
        owner_id: str,
        name: str,         # "waiver", "rules", "banner"
        file: UploadFile,
    ) -> str:
        """
        Save any supported upload as a PDF and return public path.
        """
        target_dir = cls._ensure_dir(owner_type, owner_id)
        pdf_path = target_dir / f"{name}.pdf"

        ext = Path(file.filename).suffix.lower()
        contents = await file.read()

        if ext == cls.PDF_EXT:
            pdf_path.write_bytes(contents)
        elif ext in cls.ALLOWED_IMAGE_TYPES:
            cls._image_bytes_to_pdf(contents, pdf_path)
        else:
            raise ValueError("Unsupported file type for PDF service")

        return f"/{pdf_path.as_posix()}"

    @classmethod
    def get_pdf_path(
        cls,
        *,
        owner_type: str,
        owner_id: str,
        name: str,
    ) -> Optional[Path]:
        """
        Retrieve PDF path if it exists.
        """
        path = cls.BASE_DIR / owner_type / owner_id / f"{name}.pdf"
        return path if path.exists() else None

    # -------------------------
    # Internal helpers
    # -------------------------

    @classmethod
    def _ensure_dir(cls, owner_type: str, owner_id: str) -> Path:
        path = cls.BASE_DIR / owner_type / owner_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _image_bytes_to_pdf(image_bytes: bytes, output_path: Path) -> None:
        """
        Convert image bytes to a single-page PDF.
        """
        with Image.open(BytesIO(image_bytes)) as img:
            img = img.convert("RGB")
            img.save(output_path, "PDF")