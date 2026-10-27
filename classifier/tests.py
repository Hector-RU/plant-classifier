from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import PlantImage
from .predictor import PlantDiseasePredictor
from .views import RECOMMENDATIONS, format_prediction


class PredictionFormattingTests(SimpleTestCase):
    def test_every_disease_class_has_specific_suggestions(self):
        for label in PlantDiseasePredictor.classes:
            plant, condition = label.split('__')
            condition = condition.replace('_', ' ').title()
            with self.subTest(condition=condition):
                if condition != 'Healthy':
                    self.assertIn(condition, RECOMMENDATIONS)
                    self.assertEqual(
                        format_prediction(f'{plant} - {condition}')[2],
                        RECOMMENDATIONS[condition],
                    )

    def test_healthy_prediction_has_maintenance_suggestions(self):
        plant, condition, suggestions = format_prediction('Tomato - Healthy')
        self.assertEqual((plant, condition), ('Tomato', 'Healthy'))
        self.assertIn('Maintain a regular watering schedule', suggestions)

    def test_unknown_label_uses_fallback_suggestions(self):
        plant, condition, suggestions = format_prediction('Unknown condition')
        self.assertEqual((plant, condition), ('Plant', 'Unknown condition'))
        self.assertIn('Consult an agricultural specialist', suggestions)


class UploadViewTests(TestCase):
    def setUp(self):
        media = TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)

    def image_upload(self):
        content = BytesIO()
        Image.new('RGB', (32, 32), color='green').save(content, format='PNG')
        return SimpleUploadedFile('leaf.png', content.getvalue(), content_type='image/png')

    def test_home_page_is_in_english(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, 'Choose Image')

    @patch('classifier.views.get_predictor')
    def test_upload_saves_english_prediction_and_renders_result(self, get_predictor):
        get_predictor.return_value.predict.return_value = ('Tomato - Late Blight', 95.57)
        response = self.client.post(reverse('home'), {'image': self.image_upload()})
        self.assertContains(response, 'Tomato - Late Blight')
        self.assertContains(response, '95.6%')
        self.assertContains(response, 'Keep leaves dry')
        self.assertEqual(PlantImage.objects.get().prediction, 'Tomato - Late Blight')

    @patch('classifier.views.get_predictor')
    def test_healthy_result_uses_healthy_care_intro(self, get_predictor):
        get_predictor.return_value.predict.return_value = ('Tomato - Healthy', 98.0)
        response = self.client.post(reverse('home'), {'image': self.image_upload()})
        self.assertContains(response, 'General care for a healthy plant:')
        self.assertContains(response, 'status-healthy')

    @patch('classifier.views.get_predictor')
    def test_inference_failure_displays_visible_english_error(self, get_predictor):
        get_predictor.return_value.predict.side_effect = ValueError('Invalid image')
        with self.assertLogs('classifier.views', level='ERROR'):
            response = self.client.post(reverse('home'), {'image': self.image_upload()})
        self.assertContains(response, 'Unable to process this image.')
        self.assertContains(response, 'role="alert" style="display: block;"')
