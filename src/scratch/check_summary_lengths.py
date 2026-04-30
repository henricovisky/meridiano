
from sqlmodel import select

from meridiano.database import get_session
from meridiano.models import Article


def check_summary_lengths():
    with get_session() as session:
        statement = select(Article).where(Article.processed_content.is_not(None))
        articles = session.exec(statement).all()
        if not articles:
            print("No processed articles found.")
            return

        lengths = [len(a.processed_content) for a in articles]
        avg_len = sum(lengths) / len(lengths)
        print(f"Number of articles: {len(articles)}")
        print(f"Average summary length (chars): {avg_len:.1f}")
        print(f"Max summary length (chars): {max(lengths)}")
        print(f"Min summary length (chars): {min(lengths)}")


if __name__ == "__main__":
    check_summary_lengths()
