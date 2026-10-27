# Plant Disease Classifier

A Django application that classifies leaf images using a trained PyTorch ResNet18 model. The web interface, branded as **AgroVision AI**, supports 21 labels across five crops and displays the predicted condition, model confidence, and condition-specific care suggestions.

## Features

- Image upload through a file picker or drag and drop, with a local preview.
- Classification of healthy leaves and supported disease or pest conditions.
- Inference on CUDA when available, with CPU fallback.
- English prediction labels, interface text, error messages, and care suggestions.
- SQLite records for uploaded images, timestamps, and prediction labels.
- A Google Colab notebook for training, validation, checkpoint export, and single-image inference.

## Supported Classes

| Crop | Conditions | Labels |
| --- | --- | --- |
| Corn (maize) | Cercospora leaf spot / gray leaf spot, common rust, northern leaf blight, healthy | 4 |
| Peach | Bacterial spot, healthy | 2 |
| Bell pepper | Bacterial spot, healthy | 2 |
| Potato | Early blight, late blight, healthy | 3 |
| Tomato | Bacterial spot, early blight, late blight, leaf mold, Septoria leaf spot, two-spotted spider mite, target spot, tomato yellow leaf curl virus, tomato mosaic virus, healthy | 10 |

## Architecture

1. The browser submits an image to the Django home view.
2. Django stores the file under `media/plant_images/` and creates a `PlantImage` record.
3. A lazily initialized predictor loads `models/plant_classifier_model.pth` and reuses it for subsequent requests in the same process.
4. The image is converted to RGB, resized to 256 pixels on its shorter edge, center-cropped to 224 × 224, converted to a tensor, and normalized with ImageNet statistics.
5. ResNet18 produces 21 scores. Softmax selects the highest-scoring label and its confidence percentage.
6. The view saves the English prediction and renders the result with care suggestions.

The frontend uses shared Django templates, local responsive CSS, inline SVG illustrations and icons, and vanilla JavaScript. Google Fonts supplies DM Sans and Manrope, with system font fallbacks when offline. The included checkpoint supplies all inference weights; the predictor does not download pretrained weights at startup.

## Local Setup

Use a Python environment compatible with both PyTorch and torchvision. The existing development environment uses Python 3.13, Django 5.2.4, PyTorch 2.7.1, and torchvision 0.22.1. `requirements.txt` specifies minimum versions rather than a locked environment.

Clone the repository:

```sh
git clone https://github.com/Hector-RU/plant-classifier.git
cd plant-classifier
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Or on macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies, initialize the database, and start the development server:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [the local application](http://127.0.0.1:8000/). The trained checkpoint is included at `models/plant_classifier_model.pth`; training is not required to run the application.

## Usage

1. Upload a clear leaf image using **Choose Image** or drag and drop.
2. Review the preview and select **Analyze Image**.
3. Read the predicted condition, confidence score, and care suggestions.
4. Select **Analyze Another Image** to return to the upload page.

Uploaded files and prediction records remain in the local media directory and SQLite database. The current interface does not provide upload history or deletion controls.

## Training and Evaluation

Open [`models/train.ipynb`](models/train.ipynb) in Google Colab and run its cells in order. The notebook installs its additional training dependencies: Matplotlib, scikit-learn, and seaborn. Google Drive and file-upload integrations are specific to Colab.

Provide a dataset archive at `MyDrive/Colab_Projects/PLANTS.zip` with this structure:

```text
PLANTS/
  train/
    <class-name>/
      <image files>
  valid/
    <class-name>/
      <image files>
```

The dataset is not included. Both splits must contain the same 21 class folders. `ImageFolder` assigns indices using sorted folder names; preserve that mapping in the notebook's `CLASS_NAMES` and the predictor's `classes` list. The notebook accepts the dataset's triple-underscore separator when comparing folder names with the application's double-underscore labels.

The default configuration uses ImageNet-initialized ResNet18, a frozen feature extractor, a new classification layer, batch size 64, 20 epochs, cross-entropy loss, and Adam with learning rate 0.001. Training augmentation includes random resized crops, horizontal flips, and color jitter. Validation uses the same preprocessing as web inference.

The training loop restores the weights with the highest validation accuracy and exports a state dictionary to Google Drive. Copy the exported file to `models/plant_classifier_model.pth` and restart the Django process to use a replacement checkpoint. Any class changes also require updating the predictor and this documentation.

The notebook produces learning curves, a classification report, and a confusion matrix. Final evaluation uses the same validation split used for checkpoint selection. No independent test-set accuracy or field-performance claim is established by this repository. Stored notebook outputs are intentionally cleared; run the notebook to generate results for your dataset.

## Project Structure

```text
plant-classifier/
  classifier/
    migrations/             # Database schema
    templates/classifier/   # Upload and result pages
    models.py               # Uploaded image record
    predictor.py            # Checkpoint loading and inference
    tests.py                # View and prediction regression tests
    urls.py                 # Application route
    views.py                # Upload handling and care suggestions
  models/
    plant_classifier_model.pth
    train.ipynb
  plant_classifier/         # Django settings and entry points
  manage.py
  requirements.txt
```

`db.sqlite3`, uploaded media, and virtual environments are local files excluded from version control. `plant_classifier/settings_append.txt` is a reference snippet; active media settings already live in `settings.py`.

## Validation

Run Django's configuration checks and application tests:

```sh
python manage.py check
python manage.py test
```

The automated view tests mock model inference to verify upload handling, English result rendering, healthy care suggestions, and error presentation without requiring GPU access or a training run.

## Limitations and Deployment

The classifier always chooses among its supported labels, including for unrelated or unfamiliar images. Its confidence is a softmax score, not a calibrated probability of a correct diagnosis. Care suggestions are static text associated with a predicted condition.

The included configuration is intended for local development: `DEBUG=True`, a development secret key, SQLite storage, and development media serving. Before public deployment, configure a private secret, disable debug mode, set allowed hosts, use a production application server, configure static and media hosting, and add upload validation and resource limits appropriate to the deployment.

## License

Distributed under the [MIT License](LICENSE).
