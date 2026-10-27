import logging

from django.shortcuts import render

from .models import PlantImage
from .predictor import PlantDiseasePredictor

logger = logging.getLogger(__name__)
predictor = None


def get_predictor():
    # Reuse the loaded checkpoint instead of loading it for every request.
    global predictor
    if predictor is None:
        predictor = PlantDiseasePredictor()
    return predictor


RECOMMENDATIONS = {
    'Late Blight': [
        'Apply protective fungicides',
        'Keep leaves dry',
        'Remove infected plants',
        'Improve soil drainage',
    ],
    'Early Blight': [
        'Rotate crops every 2-3 years',
        'Remove infected leaves',
        'Apply preventive fungicides',
        'Maintain adequate spacing between plants',
    ],
    'Leaf Mold': [
        'Reduce ambient humidity',
        'Improve ventilation',
        'Prune infected leaves',
        'Apply disease-specific fungicides',
    ],
    'Septoria Leaf Spot': [
        'Avoid wetting leaves when watering',
        'Remove weeds',
        'Apply preventive fungicides',
        'Maintain good air circulation',
    ],
    'Target Spot': [
        'Maintain good ventilation',
        'Apply systemic fungicides',
        'Avoid excess moisture',
        'Remove infected leaves',
    ],
    'Tomato Yellow Leaf Curl Virus': [
        'Control whitefly populations',
        'Use insect screens',
        'Remove infected plants',
        'Plant resistant varieties',
    ],
    'Tomato Mosaic Virus': [
        'Remove infected plants promptly',
        'Disinfect gardening tools',
        'Control insect vectors',
        'Use virus-resistant varieties',
    ],
    'Bacterial Spot': [
        'Use certified pathogen-free seeds',
        'Apply copper-based products',
        'Avoid overhead irrigation',
        'Maintain good crop hygiene',
    ],
    'Common Rust': [
        'Apply copper-based fungicides',
        'Maintain good soil drainage',
        'Avoid overhead irrigation',
        'Use rust-resistant varieties',
    ],
    'Northern Leaf Blight': [
        'Rotate crops every 2-3 years',
        'Remove infected crop debris',
        'Apply fungicides at the first sign of infection',
        'Maintain good air circulation',
    ],
    'Cercospora Leaf Spot Gray Leaf Spot': [
        'Rotate crops to limit pathogen buildup',
        'Apply preventive fungicides',
        'Improve ventilation between plants',
        'Remove infected crop residue',
    ],
    'Spider Mites Two-Spotted Spider Mite': [
        'Apply appropriate miticides',
        'Increase ambient humidity',
        'Use biological control with predatory mites',
        'Wash leaves with a strong stream of water',
    ],
}


def format_prediction(prediction):
    """Split the display label and select care suggestions for its condition."""
    plant_type, separator, condition = prediction.partition(' - ')
    if not separator:
        plant_type, condition = 'Plant', prediction

    if condition.casefold() == 'healthy':
        recommendations = [
            'Continue good crop maintenance',
            'Maintain a regular watering schedule',
            'Monitor plant health regularly',
            'Follow good agricultural practices',
        ]
    else:
        recommendations = RECOMMENDATIONS.get(condition, [
            'Consult an agricultural specialist',
            'Monitor the plant regularly',
            'Follow good growing practices',
        ])
    return plant_type, condition, recommendations


def home(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            plant_image = PlantImage.objects.create(image=request.FILES['image'])
            model = get_predictor()
            prediction, confidence = model.predict(plant_image.image.path)
            plant_image.prediction = prediction
            plant_image.save(update_fields=['prediction'])
            plant_type, condition, recommendations = format_prediction(prediction)

            return render(request, 'classifier/result.html', {
                'plant_image': plant_image,
                'prediction': prediction,
                'plant_type': plant_type,
                'condition': condition,
                'confidence': round(confidence, 1),
                'recommendations': recommendations,
            })
        except Exception:
            logger.exception('Unable to process the uploaded image')
            return render(request, 'classifier/home.html', {
                'error': 'Unable to process this image. Please upload a valid image and try again.',
            })

    return render(request, 'classifier/home.html')
