import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Url, Click

ALPHABET = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
CODE_LENGTH = 7


def _generate_code() -> str:
    # secrets.choice is cryptographically random — better than random.choice
    # for anything that will be publicly exposed (like a short code).
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


async def create_short_url(db: AsyncSession, original_url: str) -> Url:
    # Keep generating codes until we find one not already in the database.
    # Collisions are extremely rare with 62^7 (~3.5 trillion) possibilities,
    # but handling them correctly is good practice.
    while True:
        code = _generate_code()

        # `select(Url).where(...)` is the SQLAlchemy 2.x way of writing:
        #   SELECT * FROM urls WHERE short_code = :code LIMIT 1
        result = await db.execute(select(Url).where(Url.short_code == code))
        if result.scalar_one_or_none() is None:
            break  # Code is unique — we can use it

    url = Url(original=original_url, short_code=code)
    db.add(url)       # Stage the new row (not written to DB yet)
    await db.commit() # Write to DB and finalize the transaction
    await db.refresh(url)  # Re-read the row so `url.id` and `url.created_at` are populated
    return url


async def get_url_by_code(db: AsyncSession, short_code: str) -> Url | None:
    # Returns the Url object if found, or None if the code doesn't exist.
    # The route handler will return 404 if this comes back as None.
    result = await db.execute(select(Url).where(Url.short_code == short_code))
    return result.scalar_one_or_none()


async def record_click(db: AsyncSession, url_id: int, ip_address: str | None) -> None:
    click = Click(url_id=url_id, ip_address=ip_address)
    db.add(click)
    await db.commit()
    # No refresh needed — we don't use the click object after saving it


async def get_stats(db: AsyncSession, short_code: str) -> dict | None:
    # Step 1: find the URL row
    result = await db.execute(select(Url).where(Url.short_code == short_code))
    url = result.scalar_one_or_none()

    if url is None:
        return None  # Caller will turn this into a 404

    # Step 2: count the clicks for this URL
    # func.count(Click.id) translates to: SELECT COUNT(clicks.id) FROM clicks WHERE url_id = :id
    count_result = await db.execute(
        select(func.count(Click.id)).where(Click.url_id == url.id)
    )
    click_count = count_result.scalar_one()  # scalar_one() unwraps the single integer result

    # Step 3: return a plain dict — the route handler will pass this to StatsResponse(**stats)
    return {
        "original_url": url.original,
        "click_count": click_count,
        "created_at": url.created_at,
        "expires_at": url.expires_at,
    }
