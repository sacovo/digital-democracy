"""
Tests for app papers
"""
from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from papers import models, utils

# Create your tests here.
workingTitle = "Test missing translations"


class PaperTestCase(TestCase):
    """
    Test case for the paper and related models
    """

    def setUp(self):
        self.paper = models.Paper.objects.create(
            amendment_deadline=timezone.now() + timedelta(days=10),
            working_title="Test Paper",
            state="draft",
        )
        self.user = get_user_model().objects.create_user(username="test")
        self.author = models.Author.objects.create(user=self.user)

    def test_missing_translations(self):
        """
        Paper has no translation, so list of missing translations
        should be equal to all configured translations.
        """
        paper = models.Paper.objects.create(
            amendment_deadline=timezone.now() + timedelta(days=10),
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
            amendment_deadline=timezone.now() + timedelta(days=10),
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

    def test_start_zero_amendments(self):
        """Check if we start with zero amendments"""
        self.assertEqual(self.paper.count_amendments(), 0)

    def test_add_amendment(self):
        """Count should increase with a new public amendment"""
        amendment = self.paper.amendment_set.create(
            language_code="de",
            content="Content",
            author=models.Author.objects.create(
                user=get_user_model().objects.create(username="test_user_for_counting")
            ),
            state="draft",
            reason="reason",
        )

        self.assertEqual(0, self.paper.count_amendments())

        amendment.state = "public"
        amendment.save()

        self.assertEqual(1, self.paper.count_amendments())

    def test_start_zero_comments(self):
        """Count should start with zero"""
        self.assertEqual(self.paper.count_comments(), 0)

    def test_add_comment(self):
        """Start with zero comments"""
        amendment = self.paper.amendment_set.create(
            language_code="de",
            content="Test addign a comment",
            author=models.Author.objects.create(
                user=get_user_model().objects.create(username="test-comments")
            ),
            state="public",
            reason="reason",
        )

        amendment.comments.create(body="Test addign a comment")

        self.assertEqual(1, self.paper.count_amendments())


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


class AmendmentTestCase(TestCase):
    """
    Test case for an amendment
    """

    content = "doesn't matter"
    reason = "no reason at all"

    def setUp(self):
        self.paper = models.Paper.objects.create(
            amendment_deadline=timezone.now() + timedelta(days=10),
            working_title="Test Paper",
            state="public",
        )

        self.user = get_user_model().objects.create_user(username="test")
        self.author = models.Author.objects.create(user=self.user)

    def test_no_translations_on_creation(self):
        """
        An amendment doesn't have any translations upon creation.
        """
        amendment = models.Amendment.objects.create(
            paper=self.paper,
            language_code="de",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        self.assertEqual(
            len(list(amendment.translation_list())),
            0,
            msg="no translations upon creation",
        )

    def test_add_translation(self):
        """
        After adding a translation it should be in the list of
        translations
        """
        amendment = models.Amendment.objects.create(
            paper=self.paper,
            language_code="de",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        translation = models.Amendment.objects.create(
            paper=self.paper,
            language_code="fr",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        amendment.add_translation(translation)

        self.assertTrue(
            amendment.has_translation_for_language("fr"),
            msg="amendment as french translation",
        )
        self.assertTrue(
            translation.has_translation_for_language("de"),
            msg="translation as german translation",
        )

        self.assertTrue(
            translation in list(amendment.translation_list()),
            msg="translation in list of translations",
        )

    def test_add_two_translations(self):
        """
        Only the first translation should be added
        """
        amendment = models.Amendment.objects.create(
            paper=self.paper,
            language_code="de",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        translation = models.Amendment.objects.create(
            paper=self.paper,
            language_code="fr",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        other_translation = models.Amendment.objects.create(
            paper=self.paper,
            language_code="fr",
            content=self.content,
            author=self.author,
            state="public",
            reason=self.reason,
        )

        amendment.add_translation(translation)
        amendment.add_translation(other_translation)

        self.assertFalse(
            other_translation in list(amendment.translation_list()),
            msg="only one translation per language",
        )
        self.assertFalse(
            other_translation.has_translation_for_language("de"),
            msg="second translation should not have a translation for german",
        )


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
            amendment_deadline=timezone.now() + timedelta(days=10),
            working_title="Test Amendment Supporter",
            state="public",
        )

        amendment = models.Amendment.objects.create(
            author_id=author.id, paper_id=paper.id, state="Draft", reason="Some Reason"
        )

        self.assertEqual(amendment.num_supporters(), 0)


class LikeCommentTestCase(TestCase):
    """
    Test case for the like comment feature
    """

    def test_amount_likes(self):
        """
        A comment should have zero likes upon creation
        """
        user = get_user_model().objects.create_user(username="testuser")

        author = models.Author.objects.create(user=user)

        paper = models.Paper.objects.create(
            amendment_deadline=timezone.now() + timedelta(days=10),
            working_title="Test Amount of Likes",
            state="public",
        )

        amendment = models.Amendment.objects.create(
            author_id=author.id, paper_id=paper.id, state="Draft", reason="Some Reason"
        )

        comment = models.Comment.objects.create(
            amendment_id=amendment.id,
            author_id=author.id,
            body="Ein Kommentar zum testen",
        )

        self.assertEqual(comment.num_likes(), 0)


class BulkUserImportTestCase(TestCase):
    """
    Tests for the feature for importing users
    """

    path_var = "/members/upload-users/"

    def setUp(self):
        user = get_user_model().objects.create_superuser(username="csv-admin")
        self.client = Client()
        self.client.force_login(user=user)

        self.csv_file = BytesIO(
            b"first_name,last_name,email,username\ntest,test,test@test.ch,test-user\ntest1,test1,test2@test.ch,test2"
        )
        self.invalid_csv = BytesIO(
            b"first_name,last_name,email,username\nvalid,valid,valid@email.com,valid_user\ntest,test,not-an-email-address,username"
        )

    def test_import_single_user_csv(self):
        self.client.post(BulkUserImportTestCase.path_var, {"csv_file": self.csv_file})

        self.assertTrue(get_user_model().objects.filter(username="test-user").exists())
        self.assertTrue(get_user_model().objects.filter(username="test2").exists())

    def test_import_wrong_csv(self):
        response = self.client.post(
            BulkUserImportTestCase.path_var, {"csv_file": self.invalid_csv}
        )

        self.assertTrue(response.context["error"])
        self.assertFalse(
            get_user_model().objects.filter(username="valid_user").exists()
        )
        self.assertFalse(get_user_model().objects.filter(username="username").exists())

    def test_login_required(self):
        client = Client()
        response = client.post(
            BulkUserImportTestCase.path_var, {"csv_file": self.csv_file}
        )

        self.assertNotEqual(response.status_code, 200)
