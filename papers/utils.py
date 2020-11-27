"""
Misc. functions that are used by the project
"""
import re
from itertools import zip_longest


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
