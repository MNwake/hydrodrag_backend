# core/controllers/hydrodrags_config_controller.py
from pathlib import Path

from fastapi import UploadFile

from core.models.hydrodrags import (
    HydroDragsConfig,
    Sponsor,
    SocialLink,
    SpanishContent, NewsItem,
)
ASSETS_DIR = Path("assets")

class HydroDragsConfigController:
    def __init__(self):
        self.config: HydroDragsConfig = HydroDragsConfig.get()

    def update_config(self, payload: "HydroDragsConfigUpdate") -> HydroDragsConfig:
        data = payload.model_dump(exclude_unset=True)

        for field in [
            "headline",
            "about",
            "tagline",
            "email",
            "phone",
            "support_email",
            "website_url",
            "ihra_membership_price",
            "spectator_single_day_price",
            "spectator_weekend_price",
            "is_active",
        ]:
            if field in data:
                setattr(self.config, field, data[field])

        if "es" in data:
            es_data = data["es"]
            self.config.es = SpanishContent(**es_data) if es_data else None

        self.config.save()
        return self.config

    # -------------------------
    # Sponsors
    # -------------------------

    def add_sponsor(self, data: dict):
        sponsor = Sponsor(**data)
        self.config.sponsors.append(sponsor)
        self.config.save()
        return sponsor

    def update_sponsor(self, index: int, data: dict):
        if index < 0 or index >= len(self.config.sponsors):
            raise ValueError("Invalid sponsor index")

        sponsor = self.config.sponsors[index]
        for key, value in data.items():
            setattr(sponsor, key, value)

        self.config.save()
        return sponsor

    def delete_sponsor(self, index: int):
        if index < 0 or index >= len(self.config.sponsors):
            raise ValueError("Invalid sponsor index")

        removed = self.config.sponsors.pop(index)
        self.config.save()
        return removed

    # -------------------------
    # Media Partners
    # -------------------------

    def add_media_partner(self, data: dict):
        partner = Sponsor(**data)
        self.config.media_partners.append(partner)
        self.config.save()
        return partner

    def update_media_partner(self, index: int, data: dict):
        if index < 0 or index >= len(self.config.media_partners):
            raise ValueError("Invalid media partner index")

        partner = self.config.media_partners[index]
        for key, value in data.items():
            setattr(partner, key, value)

        self.config.save()
        return partner

    def delete_media_partner(self, index: int):
        if index < 0 or index >= len(self.config.media_partners):
            raise ValueError("Invalid media partner index")

        removed = self.config.media_partners.pop(index)
        self.config.save()
        return removed

    def add_hero_news(self, data: dict):
        item = NewsItem(**data)
        self.config.news.append(item)
        self.config.save()
        return item

    def update_hero_news(self, index: int, data: dict):
        if index < 0 or index >= len(self.config.news):
            raise ValueError("Invalid hero news index")

        item = self.config.news[index]
        for key, value in data.items():
            setattr(item, key, value)

        self.config.save()
        return item

    def delete_hero_news(self, index: int):
        if index < 0 or index >= len(self.config.news):
            raise ValueError("Invalid hero news index")

        removed = self.config.news.pop(index)
        self.config.save()
        return removed


    # -------------------------
    # Logo
    # -------------------------

    def update_logo(self, file: UploadFile) -> str:
        path = ASSETS_DIR / "logo.png"

        with path.open("wb") as f:
            f.write(file.file.read())

        self.config.logo_url = "/assets/logo.png"
        self.config.save()
        return self.config.logo_url

    def delete_logo(self):
        self.config.logo_url = None
        self.config.save()

    # -------------------------
    # Banner
    # -------------------------

    def update_banner(self, file: UploadFile) -> str:
        path = ASSETS_DIR / "banner.png"

        with path.open("wb") as f:
            f.write(file.file.read())

        self.config.banner_url = "/assets/banner.png"
        self.config.save()
        return self.config.banner_url

    def delete_banner(self):
        self.config.banner_url = None
        self.config.save()