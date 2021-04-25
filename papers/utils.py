"""
Misc. functions that are used by the project
"""
import csv
import io
import re
import secrets
from itertools import zip_longest
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils.translation import gettext as _
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.dml.line import LineFormat
from pptx.enum.shapes import MSO_CONNECTOR_TYPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_PARAGRAPH_ALIGNMENT
from pptx.util import Cm, Pt


class Change:
    start: int
    end: int
    content: str  # eg: <ins>...</ins> or <del>...</del>


def apply_change(original_text: str, change: Change) -> str:
    return "".join(
        original_text[: change.start], change.content, original_text[change.end :]
    )


def update_change(change: Change, applied: Change):
    if change.start < applied.start:
        return
    delta = len(applied.content) - (applied.end - applied.start)
    change.start += delta
    change.end += delta


def create_changes_of_amendment(text: str) -> List[Change]:
    """text contains changes marked up with <del> or <ins> tags."""
    pass


def create_modified_text(original_text: str, amendments) -> str:
    changes = []
    for amendment in amendments:
        changes += create_changes_of_amendment(amendment.content)
    modified_text = original_text

    while changes:
        change = changes.pop()
        modified_text = apply_change(modified_text, change)
        for other in changes:
            update_change(other, change)
    return modified_text


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

    # Create layouts
    title_layout = prs.slide_layouts[5]
    amendment_layout = prs.slide_layouts[1]

    # Add the title slide to the prs
    title_slide = prs.slides.add_slide(title_layout)

    # Add title text to slide
    title_slide.shapes.title.text = "\n".join(
        (translation.title for translation in paper.translation_set.all())
    )
    shape = title_slide.shapes
    title_shape = shape.title
    title = title_slide.shapes.title
    title.top = Cm(10)
    title.left = Cm(2)

    x = 0
    for translation in paper.translation_set.all():
        title_shape.text_frame.paragraphs[x].font.size = Pt(18)
        title_shape.text_frame.paragraphs[x].font.bold = True
        title_shape.text_frame.paragraphs[x].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        x += 1

    title_shape.text_frame.paragraphs[0].alignment = PP_PARAGRAPH_ALIGNMENT.LEFT

    # Underline title
    underline = title_slide.shapes.add_connector(
        MSO_CONNECTOR_TYPE.STRAIGHT, Cm(23), Cm(9.5), Cm(2.25), Cm(9.5)
    )
    line = LineFormat(underline)
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(255, 255, 255)

    # Set background
    background = title_slide.background
    background.fill.solid()
    background.fill.fore_color.rgb = RGBColor(255, 0, 0)

    # Set title slide
    title_textbox = title_slide.shapes.add_textbox(Cm(5.25), Cm(6), Cm(5), Cm(20))
    title_tf = title_textbox.text_frame
    p = title_tf.add_paragraph()
    p.text = " PAPER TITLE:"
    p.font.size = Pt(45)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Generating amendment slides
    for i, amendment in enumerate(
        paper.amendment_set.filter(
            language_code=paper.translation_set.first().language_code
        )
    ):
        amendment_slide = prs.slides.add_slide(amendment_layout)

        amendment_nr_textbox = amendment_slide.shapes.add_textbox(
            Cm(0.25), Cm(0.25), Cm(5), Cm(4)
        )
        paper_title_textbox = amendment_slide.shapes.add_textbox(
            Cm(10), Cm(0.6), Cm(7), Cm(5)
        )

        txz_frame = amendment_nr_textbox.text_frame
        amendment_nr_paragraph = txz_frame.paragraphs[0]
        amendment_nr_paragraph.text = f"A{i + 1}:"
        amendment_nr_paragraph.font.size = Pt(60)
        amendment_nr_paragraph.font.bold = True
        amendment_nr_paragraph.font.color.rgb = RGBColor(0x0, 0x0, 0x0)

        # Paper title on amendment page
        title_textframe = paper_title_textbox.text_frame
        amendment_paper_title_paragraph1 = title_textframe.paragraphs[0]

        amendment_paper_title_paragraph1.text = "\n".join(
            (translation.title for translation in paper.translation_set.all())
        )
        amendment_paper_title_paragraph1.font.size = Pt(14)
        amendment_paper_title_paragraph1.font.bold = True
        amendment_paper_title_paragraph1.font.color.rgb = RGBColor(0x0, 0x0, 0x0)
        amendment_paper_title_paragraph1.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
        amendment_paper_title_paragraph1.alignment = PP_PARAGRAPH_ALIGNMENT.LEFT

        # Underline title
        underline2 = amendment_slide.shapes.add_connector(
            MSO_CONNECTOR_TYPE.STRAIGHT, Cm(25), Cm(3), Cm(0.5), Cm(3)
        )
        underline2 = LineFormat(underline2)
        underline2.fill.solid()
        underline2.fill.fore_color.rgb = RGBColor(0, 0, 0)

        # Removing unused placeholder
        textbox = amendment_slide.shapes[0]
        sp = textbox.element
        sp.getparent().remove(sp)

        # Adding body bullet points
        body = amendment_slide.shapes.placeholders[1]
        body.text_frame.text = amendment.title + "\n"

        for translation in amendment.translation_list():
            bullet = body.text_frame.add_paragraph()
            bullet.text = translation.title + "\n"

    return prs
