
from meridiano.database import get_session
from meridiano.models import Article, Brief
from sqlmodel import select, func, and_
from datetime import datetime, timedelta

def check_db():
    with get_session() as session:
        # Count total articles
        total_articles = session.exec(select(func.count(Article.id))).one()
        print(f"Total articles: {total_articles}")

        # Count articles with impact score
        rated_articles = session.exec(select(func.count(Article.id)).where(Article.impact_score != None)).one()
        print(f"Articles with Impact Score: {rated_articles}")

        # Count articles processed but not rated
        processed_unrated = session.exec(select(func.count(Article.id)).where(Article.processed_at != None).where(Article.impact_score == None)).one()
        print(f"Processed but Unrated articles: {processed_unrated}")

        # Check last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        recent_processed = session.exec(select(func.count(Article.id)).where(Article.processed_at >= cutoff)).one()
        print(f"Articles processed in last 24h: {recent_processed}")

        recent_with_embedding = session.exec(select(func.count(Article.id)).where(and_(Article.processed_at >= cutoff, Article.embedding != None))).one()
        print(f"Articles with embedding in last 24h: {recent_with_embedding}")

        # Count briefs
        total_briefs = session.exec(select(func.count(Brief.id))).one()
        print(f"Total Briefs: {total_briefs}")

        # Profiles
        profiles = session.exec(select(Article.feed_profile).distinct()).all()
        print(f"Profiles in articles: {profiles}")

        for profile in profiles:
            count = session.exec(select(func.count(Article.id)).where(and_(Article.feed_profile == profile, Article.processed_at >= cutoff, Article.embedding != None))).one()
            print(f"  Profile '{profile}' has {count} articles for briefing (last 24h)")

if __name__ == "__main__":
    check_db()
