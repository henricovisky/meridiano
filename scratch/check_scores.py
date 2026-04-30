from sqlmodel import select

from meridiano.models import Article, get_session


def check():
    with get_session() as session:
        statement = select(Article).where(Article.impact_score.is_not(None))
        articles = session.exec(statement).all()
        print(f"Total articles with impact scores: {len(articles)}")
        for i, a in enumerate(articles[:10]):
            print(f"ID: {a.id}, Title: {a.title[:50]}..., Score: {a.impact_score}")


if __name__ == "__main__":
    check()
