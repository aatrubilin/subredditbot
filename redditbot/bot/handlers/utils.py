from collections import namedtuple

Subreddit = namedtuple('Subreddit', ['text', 'html', 'link'])


def build_message(data):
    message = ""
    for item in data.get('data', {}).get('children', []):
        score = item["data"]["score"]
        title = item["data"]["title"]
        url = item["data"]["url"]
        message += f"<b>{score}</b> <a href='{url}'>{title}</a>\n"

    return message


def get_subreddit_link(subreddit):
    return f"<a href='https://www.reddit.com/r/{subreddit}/top/'>{subreddit}</a>"


def get_subreddit_from_context(context):
    subreddit = context.args[0].lower()
    if subreddit.startswith('-'):
        subreddit = subreddit[1:]

    res = Subreddit(
        subreddit,
        f"<b>{subreddit}</b>",
        get_subreddit_link(subreddit)
    )
    return res
