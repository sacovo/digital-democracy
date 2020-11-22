from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from papers import models

# Create your tests here.


class PaperTestCase(TestCase):
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
