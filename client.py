import logging
import random
from datetime import datetime

import praw
import praw.models
from rich.console import Console
from rich.prompt import Prompt, Confirm

from credentials import CREDENTIALS
from subreddits import SUBREDDITS

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('script')

console = Console()

# create reddit API connection
reddit_client = praw.Reddit(
    client_id=CREDENTIALS['CLIENT_ID'],
    client_secret=CREDENTIALS['CLIENT_SECRET'],
    password=CREDENTIALS['PASSWORD'],
    user_agent=CREDENTIALS['USERAGENT'],
    username=CREDENTIALS['USERNAME']
)
log.info('connected to reddit API')

num_viewed_posts = 0
num_actioned_posts = 0


def main_loop():
    while True:
        post: praw.models.Submission = get_random_post()
        global num_viewed_posts
        global num_actioned_posts
        num_viewed_posts += 1
        display(post)
        
        skip_flag = False
        exit_flag = False
        while True:
            reply_body = Prompt.ask('reply (\'n\' to skip, \'c\' to exit)')
            if reply_body.lower() == 'n':
                skip_flag = True
                break
            if reply_body.lower() == 'c':
                exit_flag = True
                break
            
            if Confirm.ask(f'you inputted \"{reply_body}\". Send?'):
                break
        if skip_flag:
            continue
        if exit_flag:
            break

        reply = send_reply(post, reply_body)     
        log.debug('created comment %s with body \"%s\" in subreddit %s', reply, reply.body, reply.subreddit)   

        random_vote = random.choice([-1, 0, 1])
        vote_reply(reply, random_vote)
        log.debug('gave comment %s random vote of %i', reply, random_vote)
        num_actioned_posts += 1


def get_random_post() -> praw.models.Submission:
    subreddit_name = random.choice(SUBREDDITS)
    subreddit = reddit_client.subreddit(display_name=subreddit_name)
    posts = [post for post in subreddit.new(limit=25)]
    post: praw.models.Submission = random.choice(posts)
    log.debug('recieved post %s was created %s UTC', post, datetime.fromtimestamp(post.created_utc))
    return post


def display(post: praw.models.Submission):
    console.rule(f'post #{num_viewed_posts} ({num_actioned_posts} posts actioned on)')
    time_offset = (datetime.now() - datetime.fromtimestamp(post.created_utc))
    console.print(f'r/{post.subreddit.display_name}: {time_offset.seconds // 3600} hours ago: {post.permalink}')
    console.print(post.title, style='bold')
    if post.over_18:
        console.print('NSFW', style='bold red')
    if post.is_self:
        console.print(post.selftext, style='grey74')
    else:
        console.print(post.url)


def send_reply(post: praw.models.Submission, reply_body: str) -> praw.models.Comment:
    return post.reply(reply_body)


def vote_reply(reply: praw.models.Comment, vote: int):
    if vote == 1:
        reply.upvote()
    elif vote == 0:
        reply.clear_vote()
    elif vote == -1:
        reply.downvote()


if __name__ == '__main__':
    main_loop()
