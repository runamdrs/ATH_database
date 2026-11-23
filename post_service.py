import mysql.connector

from database import get_all_posts, get_comments_for_post, insert_post, insert_comment


def list_posts():
    return get_all_posts()


def list_comments(post_id):
    return get_comments_for_post(post_id)


def add_post(athlete_id, content, media_url):
    """Validate, then insert. Returns (success, message)."""
    content = (content or "").strip()
    media_url = (media_url or "").strip() or None  # optional: blank -> NULL

    if athlete_id is None:
        return False, "Please choose an athlete."
    if not content:
        return False, "Post content is required."
    if media_url and len(media_url) > 500:
        return False, "Media URL must be 500 characters or fewer."

    try:
        insert_post(athlete_id, content, media_url)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete no longer exists."
        return False, f"Could not add post: {e.msg}"
    return True, "Added post."


def add_comment(athlete_id, post_id, text):
    """Validate, then insert. Returns (success, message)."""
    text = (text or "").strip()

    if athlete_id is None or post_id is None:
        return False, "Please choose an athlete and a post."
    if not text:
        return False, "Comment text is required."

    try:
        insert_comment(athlete_id, post_id, text)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or post no longer exists."
        return False, f"Could not add comment: {e.msg}"
    return True, "Added comment."
