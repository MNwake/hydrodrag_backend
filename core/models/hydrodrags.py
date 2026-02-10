from mongoengine import (
    StringField,
    FloatField,
    BooleanField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)
from core.models import BaseDocument


# -------------------------
# Embedded documents
# -------------------------

class Sponsor(EmbeddedDocument):
    name = StringField(required=True)
    logo_url = StringField()
    website_url = StringField()
    is_active = BooleanField(default=True)

class SocialLink(EmbeddedDocument):
    platform = StringField(required=True)  # "instagram", "facebook", etc
    url = StringField(required=True)


class SpanishContent(EmbeddedDocument):
    about = StringField()
    tagline = StringField()


class NewsItem(EmbeddedDocument):
    title = StringField(required=True)
    description = StringField()
    media_url = StringField()  # image OR video (admin decides)
    is_active = BooleanField(default=True)
# -------------------------
# Main config document
# -------------------------

class HydroDragsConfig(BaseDocument):
    """
    Singleton document holding HydroDrags company-wide configuration.
    """

    # -------- Branding / About --------
    headline = StringField(default="HydroDrags")
    about = StringField()
    tagline = StringField()

    logo_url = StringField()
    banner_url = StringField()

    es = EmbeddedDocumentField(SpanishContent)

    news = ListField(EmbeddedDocumentField(NewsItem))
    # -------- Contact --------
    email = StringField()
    phone = StringField()
    support_email = StringField()
    website_url = StringField()

    # -------- Pricing (GLOBAL) --------
    ihra_membership_price = FloatField(default=85.00)

    spectator_single_day_price = FloatField(default=0.00)
    spectator_weekend_price = FloatField(default=35.00)

    # -------- Sponsors --------
    sponsors = ListField(EmbeddedDocumentField(Sponsor))
    media_partners = ListField(EmbeddedDocumentField(Sponsor))

    # -------- Social --------
    social_links = ListField(EmbeddedDocumentField(SocialLink))
    # -------- Flags --------
    is_active = BooleanField(default=True)

    meta = {
        "collection": "hydrodrags_config",
    }

    @classmethod
    def get(cls) -> "HydroDragsConfig":
        """
        Always return the single active config.
        Creates one if missing.
        """
        config = cls.objects(is_active=True).first()
        if not config:
            config = cls().save()
        return config