import praw
from credentials import CREDENTIALS

def run():
    reddit_client = praw.Reddit(
        client_id=CREDENTIALS['CLIENT_ID'],
        client_secret=CREDENTIALS['CLIENT_SECRET'],
        password=CREDENTIALS['PASSWORD'],
        user_agent=CREDENTIALS['USERAGENT'],
        username=CREDENTIALS['USERNAME']
    )

    for submission in reddit_client.front.new(limit=5):
        print(f'{submission.title} (by u/{submission.author}): {submission.selftext}')

if __name__ == '__main__':
    run()