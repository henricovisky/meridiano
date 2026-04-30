import sys

sys.path.append('src')
from datetime import timedelta

from sqlmodel import func, select

from meridiano.database import get_session
from meridiano.models import Article

with get_session() as session:
    last_processed = session.exec(select(func.max(Article.processed_at))).one()
    print(f"Last processed: {last_processed}")

    if last_processed:
        count_processed_last_24 = session.exec(
            select(func.count(Article.id)).where(Article.processed_at >= (last_processed - timedelta(hours=24)))
        ).one()
        print(f"Articles processed in last 24h of last processed: {count_processed_last_24}")
    else:
        print("No processed articles found.")
