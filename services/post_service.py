import mysql.connector

from db.database import (
    get_all_posts, get_comments_for_post, get_comment_by_id,
    insert_post, insert_comment, update_comment, delete_comment,
)
from services.delete_summary import describe_related
from services.ownership import check_owner


def list_posts():
    """Return every post with its author's name and comment count."""
    return get_all_posts()


def get_post_options():
    """Map PostID -> "Author: first words" for the comments dropdown,
    so users pick a post instead of typing its ID."""
    return {p["PostID"]: f"{p['Athlete']}: {p['Content'][:40]}" for p in get_all_posts()}


def list_comments(post_id):
    """Return the comments on one post, oldest first."""
    return get_comments_for_post(post_id)


def check_post_input(athlete_id, content, media_url):
    """Validation for a new post.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (content, media_url)."""
    content = (content or "").strip()
    media_url = (media_url or "").strip() or None  # optional: blank -> NULL
    values = (content, media_url)

    if athlete_id is None:
        return "Please choose an athlete.", values
    if not content:
        return "Post content is required.", values
    if media_url and len(media_url) > 500:  # post.MediaURL is VARCHAR(500)
        return "Media URL must be 500 characters or fewer.", values

    return None, values


def add_post(athlete_id, content, media_url):
    """Validate the input, then insert it. Returns (success, message)."""
    error, (content, media_url) = check_post_input(athlete_id, content, media_url)
    if error:
        return False, error

    try:
        insert_post(athlete_id, content, media_url)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete no longer exists."
        return False, f"Could not add post: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add post: {e.msg}"

    return True, "Added post."


def get_comment_options(post_id, athlete_id):
    """Map CommentID -> "Author: first words" for the manage form's
    dropdown, limited to the current user's comments on one post."""
    return {
        c["CommentID"]: f"{c['Athlete']}: {c['Text'][:40]}"
        for c in get_comments_for_post(post_id) if c["AthleteID"] == athlete_id
    }


def get_comment_details(comment_id):
    """Return one comment's current values (to pre-fill the update form)."""
    return get_comment_by_id(comment_id)


def check_comment_input(text):
    """Shared validation for add and update. Only the text is typed in;
    the author and the post come from dropdowns.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (text,)."""
    text = (text or "").strip()
    values = (text,)

    if not text:
        return "Comment text is required.", values

    return None, values


def add_comment(athlete_id, post_id, text):
    """Validate the input, then insert it. Returns (success, message)."""
    if athlete_id is None or post_id is None:
        return False, "Please choose an athlete and a post."
    error, (text,) = check_comment_input(text)
    if error:
        return False, error

    try:
        insert_comment(athlete_id, post_id, text)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or post no longer exists."
        return False, f"Could not add comment: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add comment: {e.msg}"

    return True, "Added comment."


def edit_comment(comment_id, athlete_id, text):
    """Validate the text, then update the comment. athlete_id is the
    current user, who must have written it. Returns (success, message)."""
    error, (text,) = check_comment_input(text)
    if error:
        return False, error
    error = check_owner(get_comment_by_id(comment_id), athlete_id, "comment", "comments")
    if error:
        return False, error

    # comment has no UNIQUE column and only Text changes here, so no
    # IntegrityError can come back - only the general branch is needed.
    try:
        updated = update_comment(comment_id, text)
    except mysql.connector.Error as e:
        return False, f"Could not update comment: {e.msg}"

    if updated == 0:
        return False, "No matching comment found."
    return True, "Updated comment."


def remove_comment(comment_id, athlete_id):
    """Delete the comment, if the current user (athlete_id) wrote it.
    Nothing references it, so nothing else goes with it.
    Returns (success, message)."""
    error = check_owner(get_comment_by_id(comment_id), athlete_id, "comment", "comments")
    if error:
        return False, error

    try:
        deleted = delete_comment(comment_id)
    except mysql.connector.Error as e:
        return False, f"Could not delete comment: {e.msg}"

    if deleted["comment"] == 0:
        return False, "No matching comment found."
    return True, "Deleted comment." + describe_related(deleted, "comment")
