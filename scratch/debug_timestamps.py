import sys
sys.path.append('src')
from meridiano.database import get_session
from meridiano.models import Article
from sqlmodel import select, func
from datetime import timedelta

with get_session() as session:
    last_fetched = session.exec(select(func.max(Article.fetched_at))).one()
    print(f"Last fetched: {last_fetched}")
    
    if last_fetched:
        count_last_24 = session.exec(select(func.count(Article.id)).where(Article.fetched_at >= (last_fetched - timedelta(hours=24)))).one()
        print(f"Articles in last 24h of last fetch: {count_last_24}")
        
        # Check by profile
        profiles = session.exec(select(Article.feed_profile).distinct()).all()
        for profile in profiles:
            count = session.exec(select(func.count(Article.id)).where(Article.feed_profile == profile).where(Article.fetched_at >= (last_fetched - timedelta(hours=24)))).one()
            print(f"  Profile '{profile}': {count} articles in last 24h")
    else:
        print("No articles found.")
