"""
Misc. functions that are used by the project
"""
import csv
import io
import re
import secrets
from itertools import zip_longest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils.translation import gettext as _

# Imports for PP genaration feature
from pptx import Presentation

from papers import models


def index_of_first_change(content):
    """
    Returns the index of the first occurrence of a change
    """
    first_insert = content.find("<ins")
    first_deletion = content.find("<del")

    if first_insert == -1:
        return first_deletion

    if first_deletion == -1:
        return first_insert

    return min(first_deletion, first_insert)


def index_of_last_change(content):
    """
    Returns the index where the last change ends.
    """
    return max(content.rfind("</ins>"), content.rfind("</del>"))


def extract_content(content):
    """
    Takes a string with markup for changes (<ins> and <del> tags) and returns
    a string that contains these tags plus some context
    """
    start_index = index_of_first_change(content)

    end_index = index_of_last_change(content) + 6

    content_before = content[0:start_index]

    sentences = re.split(r"(\.|\?|\!)", content_before)

    sentences = list(zip_longest(sentences[::2], sentences[1::2], fillvalue=""))

    sentence_before = ""

    for sentence in reversed(sentences[-3:]):
        sentence_before = sentence[0] + sentence[1] + sentence_before

    content_after = content[end_index:]

    sentences = re.split(r"(\.|\?|\!)", content_after)

    sentences = list(zip_longest(sentences[::2], sentences[1::2], fillvalue=""))

    sentence_after = ""

    for sentence in sentences[:3]:
        sentence_after = sentence_after + sentence[0] + sentence[1]

    return sentence_before + content[start_index:end_index] + sentence_after


def import_users_from_csv(csv_file):
    """
    Import the given csv file into the database
    """
    csv_file = io.TextIOWrapper(csv_file)
    csv_reader = csv.DictReader(csv_file)

    imported_users = [get_user_model()(**row) for row in csv_reader]

    for new_user in imported_users:
        validate_email(new_user.email)

    for new_user in imported_users:
        password = secrets.token_urlsafe(17)
        new_user.set_password(password)
        new_user.save()

        new_user.email_user(
            _("New digital-democracy account"),
            settings.NEW_USER_MAIL.format(user=new_user, password=password),
        )

    return imported_users


def generate_powerpoint(paper):
    """
    Generates a pp-presentation based on all current papers.
    """

    # Create new presentation
    prs = Presentation()

    # Set the title

    title_layout = prs.slide_layouts[0]

    title_slide = prs.slides.add_slide(title_layout)
    title_slide.shapes.title.text = "\n".join(
        (translation.title for translation in paper.translation_set.all())
    )
    regular_slide_layout = prs.slide_layouts[1]

    paper_title = " / ".join(
        (translation.title for translation in paper.translation_set.all())
    )

    for i, amendment in enumerate(
        paper.amendment_set.filter(
            language_code=paper.translation_set.first().language_code
        )
    ):
        amendment_slide = prs.slides.add_slide(regular_slide_layout)
        amendment_slide.shapes.title.text = paper_title + f"\nA{i+1}"
        body = amendment_slide.shapes.placeholders[1]
        body.text_frame.text = amendment.title

        for translation in amendment.translation_list():
            bullet = body.text_frame.add_paragraph()
            bullet.text = translation.title

    return prs
