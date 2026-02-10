# server/base_models/hydrodrags.py
from pydantic import BaseModel, Field
from typing import List, Optional

from server.base_models import MongoReadModel


class AssetUpdateResponse(BaseModel):
    field: str
    url: Optional[str]

# -------------------------
# Embedded
# -------------------------

class SponsorBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool = True


class SocialLinkBase(BaseModel):
    platform: str
    url: str


class SpanishContentBase(BaseModel):
    about: Optional[str] = None
    tagline: Optional[str] = None


class SponsorCreate(BaseModel):
    name: str
    logo_url: str
    website_url: Optional[str] = None
    is_active: bool = True


class SponsorUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: Optional[bool] = None

class NewsItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    media_url: Optional[str] = None
    is_active: bool = True


class NewsItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    media_url: Optional[str] = None
    is_active: bool = True


class NewsItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    media_url: Optional[str] = None
    is_active: Optional[bool] = None

# -------------------------
# Main config
# -------------------------

class HydroDragsConfigUpdate(BaseModel):
    # Branding
    headline: Optional[str] = None
    about: Optional[str] = None
    tagline: Optional[str] = None
    es: Optional[SpanishContentBase] = None

    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None
    support_email: Optional[str] = None
    website_url: Optional[str] = None

    # Pricing
    ihra_membership_price: Optional[float] = None
    spectator_single_day_price: Optional[float] = None
    spectator_weekend_price: Optional[float] = None

    # Flags
    is_active: Optional[bool] = None



class HydroDragsConfigBase(MongoReadModel):
    # -------- Branding / About --------
    headline: str
    about: Optional[str] = None
    tagline: Optional[str] = None
    es: Optional[SpanishContentBase] = None
    news: List[NewsItemBase] = []
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None


    # -------- Contact --------
    email: Optional[str] = None
    phone: Optional[str] = None
    support_email: Optional[str] = None
    website_url: Optional[str] = None

    # -------- Pricing --------
    ihra_membership_price: float
    spectator_single_day_price: float
    spectator_weekend_price: float

    # -------- Sponsors / Media --------
    sponsors: List[SponsorBase] = []
    media_partners: List[SponsorBase] = []

    # -------- Social --------
    social_links: List[SocialLinkBase] = []

    # -------- Flags --------
    is_active: bool