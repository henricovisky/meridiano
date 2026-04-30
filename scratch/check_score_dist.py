from meridiano.models import get_session, Article
from sqlmodel import select, func

def check_scores():
    with get_session() as session:
        # Total articles
        total = session.query(func.count(Article.id)).scalar()
        # Summarized
        summarized = session.query(func.count(Article.id)).where(Article.processed_content != None).scalar()
        # Rated
        rated = session.query(func.count(Article.id)).where(Article.impact_score != None).scalar()
        # Non-null but zero?
        zeros = session.query(func.count(Article.id)).where(Article.impact_score == 0).scalar()
        
        print(f"Total: {total}")
        print(f"Summarized: {summarized}")
        print(f"Rated (Non-NULL): {rated}")
        print(f"Rated as 0: {zeros}")
        
        if rated > 0:
            statement = select(Article.impact_score).where(Article.impact_score != None)
            scores = session.exec(statement).all()
            from collections import Counter
            counts = Counter(scores)
            print("Score Distribution:")
            for score in sorted(counts.keys()):
                print(f"  Score {score}: {counts[score]} articles")

if __name__ == "__main__":
    check_scores()
