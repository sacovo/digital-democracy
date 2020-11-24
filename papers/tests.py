"""
Tests for app papers
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from papers import models, utils

# Create your tests here.


class PaperTestCase(TestCase):
    """
    Test case for the paper and related models
    """

    def setUp(self):
        models.Paper.objects.create(
            amendmend_deadline=timezone.now() + timedelta(days=10),
            working_title="Test Paper",
            state="draft",
        )

    def test_missing_translations(self):
        """
        Paper has no translation, so list of missing translations
        should be equal to all configured translations.
        """
        paper = models.Paper.objects.create(
            amendmend_deadline=timezone.now() + timedelta(days=10),
            working_title="Test missing translations",
            state="public",
        )

        self.assertEqual(
            list(paper.missing_translations()),
            settings.LANGUAGES,
            msg="All translations are missing.",
        )

    def test_add_translation(self):
        """
        After craeting a translation the language should not be in the list
        of missing translations anymore.
        """
        paper = models.Paper.objects.create(
            amendmend_deadline=timezone.now() + timedelta(days=10),
            working_title="Test add translation",
            state="public",
        )

        language_under_test = settings.LANGUAGES[0]
        language_code = language_under_test[0]

        models.PaperTranslation.objects.create(
            paper=paper,
            language_code=language_code,
            title="Translation of paper",
            content="Content of translation",
        )

        self.assertNotIn(
            language_under_test,
            paper.missing_translations(),
            msg="Added translation is not missing.",
        )


class ExtractorTestCase(TestCase):
    """
    Test cases for the extraction feature
    """

    def test_extraction(self):
        """
        The extracted text should be shorter than the original and it shouldn't contain
        the first and the last sentences
        """
        text = """<p>Hallo, ich bin ein Test. Hier ein zweiter Satz.</p>

<p>Ut aperiam animi cumque minima.Temporibus rerum sed et repudiandae nulla reprehenderit ex ipsam.<del class="ice-del ice-cts" data-changedata="" data-cid="2" data-last-change-time="1606126946149" data-time="1606126946149" data-userid="" data-username=""> Iste</del> iusto omnis dignissimos quia.</p>

<p>Ipsa nobis reprehenderit voluptas neque fugiat et placeat. Repellat aspernatur rerum dolore voluptas corporis exercitationem accusantium eveniet.
        </p><p>Hier ein Satz. Hier kommt nochmals Text</p>"""

        extracted = utils.extract_content(text)

        self.assertTrue(len(text) > len(extracted))

        self.assertEqual(extracted.find("Hallo, ich bin ein Test"), -1)
        self.assertEqual(extracted.find("Hier kommt nochmals Text"), -1)


class AmendmentSupporterTestCase(TestCase):
    """
    Test case for the supporting amendments feature
    """

    def test_amount_supporters(self):
        """
        An amendment should have zero supporters upon creation
        """
        user = get_user_model().objects.create_user(username="testuser")

        author = models.Author.objects.create(user=user)

        paper = models.Paper.objects.create(
            amendmend_deadline=timezone.now() + timedelta(days=10),
            working_title="Test missing translations",
            state="public",
        )

        amendment = models.Amendmend.objects.create(
            author_id=author.id, paper_id=paper.id, state="Draft", reason="Some Reason"
        )

        self.assertEqual(amendment.num_supporters(), 0)


class LikeCommentTestCase(TestCase):
    """
    Test case for the like comment feature
    """

    def test_amount_supporters(self):
        """
        A comment should have zero likes upon creation
        """
        user = get_user_model().objects.create_user(username="testuser")

        author = models.Author.objects.create(user=user)

        paper = models.Paper.objects.create(
            amendmend_deadline=timezone.now() + timedelta(days=10),
            working_title="Test missing translations",
            state="public",
        )

        amendment = models.Amendmend.objects.create(
            author_id=author.id, paper_id=paper.id, state="Draft", reason="Some Reason"
        )

        comment = models.Comment.objects.create(
            amendment_id=amendment.id,
            author_id=author.id,
            body="Ein Kommentar zum testen",
        )

        self.assertEqual(comment.num_likes(), 0)
