from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms


class PlantDiseasePredictor:
    """Run the trained 21-class ResNet18 checkpoint on a leaf image."""

    # Checkpoint output indices must retain the training ImageFolder class order.
    classes = [
        'Corn (maize)__Cercospora_leaf_spot Gray_leaf_spot',
        'Corn (maize)__Common_rust',
        'Corn (maize)__Northern_Leaf_Blight',
        'Corn (maize)__healthy',
        'Peach__Bacterial_spot',
        'Peach__healthy',
        'Pepper,bell__Bacterial_spot',
        'Pepper,bell__healthy',
        'Potato__Early_blight',
        'Potato__Late_blight',
        'Potato__healthy',
        'Tomato__Bacterial_spot',
        'Tomato__Early_blight',
        'Tomato__Late_blight',
        'Tomato__Leaf_Mold',
        'Tomato__Septoria_leaf_spot',
        'Tomato__Spider_mites Two-spotted_spider_mite',
        'Tomato__Target_Spot',
        'Tomato__Tomato_Yellow_Leaf_Curl_Virus',
        'Tomato__Tomato_mosaic_virus',
        'Tomato__healthy',
    ]

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # The checkpoint contains all weights; inference needs no ImageNet download.
        self.model = models.resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, len(self.classes))
        model_path = Path(__file__).resolve().parent.parent / 'models' / 'plant_classifier_model.pth'
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        # Keep inference preprocessing identical to the notebook's validation pipeline.
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def predict(self, image_path):
        """Return an English plant/condition label and its softmax score as a percentage."""
        with Image.open(image_path) as image:
            input_batch = self.transform(image.convert('RGB')).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_batch)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, class_index = probabilities.max(dim=0)

        plant, condition = self.classes[class_index.item()].split('__')
        plant = {'Pepper,bell': 'Bell Pepper'}.get(plant, plant)
        condition = condition.replace('_', ' ').title()
        return f'{plant} - {condition}', confidence.item() * 100
