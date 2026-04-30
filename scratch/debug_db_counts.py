import sys

sys.path.append('src')
from sqlmodel import func, select

from meridiano.database import get_session
from meridiano.models import Article, Brief

with get_session() as session:
    total_count = session.exec(select(func.count(Article.id))).one()
    briefs_count = session.exec(select(func.count(Brief.id))).one()
    processed_count = session.exec(select(func.count(Article.id)).where(Article.processed_at.is_not(None))).one()
    rated_count = session.exec(select(func.count(Article.id)).where(Article.impact_score.is_not(None))).one()
    summarized_no_score = session.exec(
        select(func.count(Article.id))
        .where(Article.processed_at.is_not(None))
        .where(Article.impact_score.is_(None))
    ).one()

    print(f"Total articles: {total_count}")
    print(f"Processed (summarized): {processed_count}")
    print(f"Briefs count: {briefs_count}")
    print(f"Articles with impact score: {rated_count}")
    print(f"Articles summarized but no score: {summarized_no_score}")
