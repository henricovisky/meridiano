
from meridiano import database, config_base as config
from datetime import datetime, timedelta

lookback = config.BRIEFING_ARTICLE_LOOKBACK_HOURS
profile = "brasil"
articles = database.get_articles_for_briefing(lookback, profile)

print(f"Lookback: {lookback} hours")
print(f"Profile: {profile}")
print(f"Articles found: {len(articles)}")

if articles:
    print(f"First article processed_at: {articles[0]['processed_at']}")
    print(f"Last article processed_at: {articles[-1]['processed_at']}")

cutoff_time = datetime.now() - timedelta(hours=lookback)
print(f"Cutoff time: {cutoff_time}")
