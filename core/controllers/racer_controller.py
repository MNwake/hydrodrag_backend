# core/controllers/racer_controller.py
from pathlib import Path

from fastapi import UploadFile

from core.models.racer import Racer
from utils import utcnow
from utils.pdf_service import PDFService


class RacerController:
    PROFILE_IMAGE_DIR = Path("assets/racers/profile")
    BANNER_IMAGE_DIR = Path("assets/racers/banner")

    def __init__(self, model: Racer):
        self.model = model

    @classmethod
    async def create_racer(self, payload: 'RacerCreate') -> Racer:
        racer = Racer.objects(email=payload.email).first()

        data = payload.model_dump(exclude_unset=True)

        if racer:
            for field, value in data.items():
                setattr(racer, field, value)
        else:
            racer = Racer(**data)

        racer.save()

        return racer

    async def update_racer(self, payload: 'RacerUpdate') -> Racer:
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(self.model, field, value)

        self.model.save()

        return self.model

    async def update_profile_image(self, file: UploadFile) -> Racer:
        racer_dir = Path(f"assets/racers/{self.model.id}")
        racer_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix.lower() or ".jpg"
        file_path = racer_dir / f"profile{ext}"

        contents = await file.read()
        file_path.write_bytes(contents)

        self.model.profile_image_path = f"assets/racers/{self.model.id}/profile{ext}"
        self.model.profile_image_updated_at = utcnow()
        self.model.save()

        return self.model

    async def update_banner_image(self, file: UploadFile) -> Racer:
        racer_dir = Path(f"assets/racers/{self.model.id}")
        racer_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix.lower() or ".jpg"
        file_path = racer_dir / f"banner{ext}"

        contents = await file.read()
        file_path.write_bytes(contents)

        self.model.banner_image_path = f"assets/racers/{self.model.id}/banner{ext}"
        self.model.banner_image_updated_at = utcnow()
        self.model.save()

        return self.model


    async def upload_waiver(self, file: UploadFile) -> Racer:
        pdf_path = await PDFService.save_pdf(
            owner_type="racers",
            owner_id=str(self.model.id),
            name="waiver",
            file=file,
        )

        self.model.waiver_path = pdf_path
        self.model.waiver_signed_at = utcnow()
        self.model.save()

        return self.model

    async def add_pwc(self, pwc_id: str) -> Racer:
        pwc_id = pwc_id.strip()

        if not pwc_id:
            raise ValueError("PWC ID cannot be empty")

        if self.model.pwc_id and pwc_id in self.model.pwc_id:
            raise ValueError(f"PWC ID '{pwc_id}' already added")

        # initialize list if missing
        if not self.model.pwc_id:
            self.model.pwc_id = []

        self.model.pwc_id.append(pwc_id)
        self.model.save()

        return self.model



