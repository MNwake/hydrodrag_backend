# server/routes/admin/hydrodrags.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from core.controllers.hydrodrags_controller import HydroDragsConfigController
from core.models.hydrodrags import HydroDragsConfig
from server.base_models.hydrodrags import HydroDragsConfigUpdate, SponsorCreate, SponsorUpdate, HydroDragsConfigBase, \
    NewsItemCreate, NewsItemUpdate
from utils.dependencies import require_admin_key  # whatever you already use

router = APIRouter(
    prefix="/hydrodrags",
    tags=["Admin – HydroDrags"],
    dependencies=[Depends(require_admin_key)]
)

@router.put("")
async def update_hydrodrags_config(
    payload: HydroDragsConfigUpdate,
):
    controller = HydroDragsConfigController()
    return controller.update_config(payload)


@router.get("/config", response_model=HydroDragsConfigBase)
async def get_hydrodrags_config():
    cfg = HydroDragsConfig.get()
    return HydroDragsConfigBase.from_mongo(cfg)

@router.post("/sponsors")
def add_sponsor(payload: SponsorCreate):
    return HydroDragsConfigController().add_sponsor(payload.model_dump())

@router.patch("/sponsors/{index}")
def update_sponsor(index: int, payload: SponsorUpdate):
    return HydroDragsConfigController().update_sponsor(
        index, payload.model_dump(exclude_unset=True)
    )

@router.delete("/sponsors/{index}")
def delete_sponsor(index: int):
    return HydroDragsConfigController().delete_sponsor(index)


@router.post("/media-partners")
def add_media_partner(payload: SponsorCreate):
    return HydroDragsConfigController().add_media_partner(payload.model_dump())

@router.patch("/media-partners/{index}")
def update_media_partner(index: int, payload: SponsorUpdate):
    return HydroDragsConfigController().update_media_partner(
        index, payload.model_dump(exclude_unset=True)
    )

@router.delete("/media-partners/{index}")
def delete_media_partner(index: int):
    return HydroDragsConfigController().delete_media_partner(index)

@router.post("/upload/sponsor-image")
async def upload_sponsor_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid image type")

    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"

    save_dir = Path("assets/sponsors")
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / filename

    with file_path.open("wb") as f:
        f.write(await file.read())

    return {
        "logo_url": f"/assets/sponsors/{filename}"
    }

@router.post("/upload/sponsor-image")
async def upload_media_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid image type")

    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"

    save_dir = Path("assets/sponsors")
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / filename

    with file_path.open("wb") as f:
        f.write(await file.read())

    return {
        "logo_url": f"/assets/media/{filename}"
    }


@router.post("/hero-news")
def add_hero_news(payload: NewsItemCreate):
    return HydroDragsConfigController().add_hero_news(payload.model_dump())

@router.patch("/hero-news/{index}")
def update_hero_news(index: int, payload: NewsItemUpdate):
    return HydroDragsConfigController().update_hero_news(
        index, payload.model_dump(exclude_unset=True)
    )

@router.delete("/hero-news/{index}")
def delete_hero_news(index: int):
    return HydroDragsConfigController().delete_hero_news(index)


# server/routes/admin/hydrodrags.py

from fastapi import UploadFile, File
from server.base_models.hydrodrags import AssetUpdateResponse

# -------------------------
# Logo
# -------------------------

@router.post("/logo", response_model=AssetUpdateResponse)
def upload_logo(file: UploadFile = File(...)):
    controller = HydroDragsConfigController()
    url = controller.update_logo(file)
    return {"field": "logo_url", "url": url}


@router.delete("/logo", response_model=AssetUpdateResponse)
def delete_logo():
    controller = HydroDragsConfigController()
    controller.delete_logo()
    return {"field": "logo_url", "url": None}


# -------------------------
# Banner
# -------------------------

@router.post("/banner", response_model=AssetUpdateResponse)
def upload_banner(file: UploadFile = File(...)):
    controller = HydroDragsConfigController()
    url = controller.update_banner(file)
    return {"field": "banner_url", "url": url}


@router.delete("/banner", response_model=AssetUpdateResponse)
def delete_banner():
    controller = HydroDragsConfigController()
    controller.delete_banner()
    return {"field": "banner_url", "url": None}