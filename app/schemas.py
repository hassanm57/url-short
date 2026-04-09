from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


# --- Request schema ---
# This is the shape of the JSON body FastAPI expects on POST /api/shorten.
# Pydantic will automatically return HTTP 422 if the body doesn't match.
class ShortenRequest(BaseModel):
    # HttpUrl validates that the value is a proper URL (e.g. has https://, a domain, etc.)
    # Sending "not-a-url" or an empty string will be rejected before your code even runs.
    original_url: HttpUrl


# --- Response schemas ---
# These control what JSON FastAPI sends back to the client.
# Only the fields you declare here will appear in the response — nothing extra leaks out.

class ShortenResponse(BaseModel):
    # Just a plain string — e.g. "http://localhost:8000/xK9mP2"
    short_url: str


class StatsResponse(BaseModel):
    original_url: str
    click_count: int
    created_at: datetime
    # Optional — links without an expiry will return null in the JSON
    expires_at: datetime | None

    # This tells Pydantic: "you might be handed a SQLAlchemy model object, not a plain dict.
    # Read attributes off the object instead of looking for dict keys."
    # Without this, doing StatsResponse.model_validate(url_orm_object) would fail.
    model_config = ConfigDict(from_attributes=True)
