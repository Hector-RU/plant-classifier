const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const previewSection = document.getElementById('preview-section');
const previewImage = document.getElementById('preview-image');
const errorMessage = document.getElementById('error-message');
const form = document.getElementById('upload-form');
const submitButton = form.querySelector('[type="submit"]');
const initialButton = submitButton.innerHTML;
let previewUrl;
let selection = 0;

document.getElementById('choose-image').addEventListener('click', () => fileInput.click());
document.getElementById('change-image').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => handleFiles(fileInput.files));
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(name => {
    document.addEventListener(name, event => event.preventDefault());
    uploadArea.addEventListener(name, event => {
        event.preventDefault();
        event.stopPropagation();
        uploadArea.classList.toggle('is-dragging', name === 'dragenter' || name === 'dragover');
    });
});
uploadArea.addEventListener('drop', event => handleFiles(event.dataTransfer.files));

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}
function handleFiles(files) {
    if (!files.length) return;
    const file = files[0];
    const currentSelection = ++selection;
    if (!file.type.startsWith('image/')) {
        fileInput.value = '';
        previewSection.hidden = true;
        uploadArea.hidden = false;
        return showError('Please select a valid image file.');
    }
    const nextUrl = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
        if (currentSelection !== selection) return URL.revokeObjectURL(nextUrl);
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = nextUrl;
        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;
        previewImage.src = previewUrl;
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('file-size').textContent = file.size < 1048576
            ? `${(file.size / 1024).toFixed(1)} KB` : `${(file.size / 1048576).toFixed(1)} MB`;
        errorMessage.style.display = 'none';
        uploadArea.hidden = true;
        previewSection.hidden = false;
        submitButton.focus({preventScroll: true});
    };
    image.onerror = () => {
        URL.revokeObjectURL(nextUrl);
        if (currentSelection !== selection) return;
        fileInput.value = '';
        previewSection.hidden = true;
        uploadArea.hidden = false;
        showError('This image could not be opened. Please try a JPG, PNG, or another supported image.');
    };
    image.src = nextUrl;
}
form.addEventListener('submit', event => {
    if (!fileInput.files.length) {
        event.preventDefault();
        return showError('Please choose a leaf image first.');
    }
    submitButton.textContent = 'Analyzing your leaf…';
    submitButton.disabled = true;
    form.setAttribute('aria-busy', 'true');
});
window.addEventListener('pageshow', () => {
    submitButton.innerHTML = initialButton;
    submitButton.disabled = false;
    form.removeAttribute('aria-busy');
});
