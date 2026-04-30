import sys
sys.path.append('src')
from meridiano.database import get_session
from meridiano.models import Brief, Article
from sqlmodel import select, func

with get_session() as session:
    total_count = session.exec(select(func.count(Article.id))).one()
    briefs_count = session.exec(select(func.count(Brief.id))).one()
    processed_count = session.exec(select(func.count(Article.id)).where(Article.processed_at != None)).one()
    rated_count = session.exec(select(func.count(Article.id)).where(Article.impact_score != None)).one()
    summarized_no_score = session.exec(select(func.count(Article.id)).where(Article.processed_at != None).where(Article.impact_score == None)).one()
    
    print(f"Total articles: {total_count}")
    print(f"Processed (summarized): {processed_count}")
    print(f"Briefs count: {briefs_count}")
    print(f"Articles with impact score: {rated_count}")
    print(f"Articles summarized but no score: {summarized_no_score}")
