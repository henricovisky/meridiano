
from sqlmodel import Session, create_engine, select
from meridiano.models import Article, Brief
import os

DATABASE_URL = "sqlite:///meridian.db"
engine = create_engine(DATABASE_URL)

def check_articles():
    with Session(engine) as session:
        briefs = session.exec(select(Brief)).all()
        print(f"\nTotal Briefs: {len(briefs)}")
        for b in briefs:
            print(f"  Brief ID {b.id}, Generated At {b.generated_at}, Profile {b.feed_profile}")
        
        articles = session.exec(select(Article)).all()
        total = len(articles)
        summarized = sum(1 for a in articles if a.processed_content)
        embedded = sum(1 for a in articles if a.embedding)
        rated = sum(1 for a in articles if a.impact_score is not None)
        
        print(f"\nTotal articles: {total}")
        print(f"Summarized: {summarized}")
        print(f"Embedded: {embedded}")
        print(f"Rated (Impact Score): {rated}")
        
        # Per profile stats
        profiles = set(a.feed_profile for a in articles)
        print("\nStats per profile:")
        for p in profiles:
            p_articles = [a for a in articles if a.feed_profile == p]
            p_total = len(p_articles)
            p_rated = sum(1 for a in p_articles if a.impact_score is not None)
            print(f"  Profile '{p}': Total {p_total}, Rated {p_rated}")

if __name__ == "__main__":
    check_articles()
