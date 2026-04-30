from meridiano.models import get_session, Brief
from sqlmodel import select

def check():
    with get_session() as session:
        briefs = session.exec(select(Brief)).all()
        print(f"Total briefs: {len(briefs)}")
        for b in briefs:
            print(f"ID: {b.id}, Profile: {b.feed_profile}, Date: {b.generated_at}")

if __name__ == "__main__":
    check()
