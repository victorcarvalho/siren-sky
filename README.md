# Siren Sky - Image Garbage Classification System

A Python-based image classification system that uses OpenAI's GPT-4 vision capabilities to detect garbage in images. Features both batch processing and an interactive Streamlit web application for real-time classification with MLflow experiment tracking.

## Features

- **Batch Image Processing**: Classify entire image datasets with automated analysis
- **Interactive Web Interface**: Streamlit-based UI for uploading and classifying images in real-time
- **Simulated Predictions**: Test the application without API calls using simulated predictions
- **Experiment Tracking**: MLflow integration for tracking and comparing classification experiments
- **Image Metadata Extraction**: Automatically extract and display image properties (dimensions, format, EXIF data)
- **Geolocation Support**: Display image locations on an interactive map when available

## Project Structure

```
├── main.py                  # Batch processing script for classifying entire datasets
├── web_app.py              # Streamlit web application for interactive classification
├── classifiers.py          # Image classification logic and OpenAI API integration
├── config.py               # Configuration management and environment variables
├── image_metadata.py       # Image metadata extraction utilities
├── mlflow_tracking.py      # MLflow experiment tracking setup
├── requirements.txt        # Python package dependencies
├── .env                    # Environment configuration (see .env.example)
└── README.md              # This file
```

## Requirements

- Python 3.8+
- OpenAI API key (for GPT-4 vision access)
- MLflow server (optional, for experiment tracking)

## Installation

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd siren-sky
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your settings (see [Configuration](#configuration) below)

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATASET_PATH` | Path to the dataset directory containing images | `dataset` |
| `OPENAI_API_KEY` | Your OpenAI API key for authentication | `sk-...` |
| `CLASSIFICATION_PROMPT` | The prompt template for image classification | `Is there garbage in this image? Answer with yes or no.` |
| `IMAGE_DETAIL` | Image detail level for API calls | `auto`, `low`, or `high` |
| `MODEL` | OpenAI model to use for classification | `gpt-4-vision`, `gpt-4.1-nano` |
| `USE_SIMULATED_PREDICTIONS` | Use simulated predictions instead of API calls | `true` or `false` |
| `TRACKING_URI` | MLflow tracking server URI | `http://127.0.0.1:5000` |

## Usage

### Batch Processing

Process all images in a dataset directory and log results to MLflow:

```bash
python main.py
```

Expected dataset structure:
```
dataset/
├── category1/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── category2/
│   ├── image1.jpg
│   └── ...
```

Classification results will be printed to console and logged to MLflow.

### Interactive Web Application

Run the Streamlit web interface:

```bash
streamlit run web_app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Upload single images or batch process multiple files
- Real-time classification results
- View image metadata (dimensions, format, size)
- See geolocation on interactive map
- Toggle between simulated and live API predictions

## MLflow Tracking

To view experiment tracking results, start the MLflow server:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then navigate to `http://localhost:5000` to view experiment metrics and results.

## Testing Without API Keys

Set `USE_SIMULATED_PREDICTIONS=true` in your `.env` file to test the application without making actual OpenAI API calls. This is useful for development and testing.

## Environment Setup

### Using a Local MLflow Server

To track experiments locally:

```bash
# Start MLflow tracking server
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

Update `.env` with:
```
TRACKING_URI=http://127.0.0.1:5000
```

## Dependencies

See `requirements.txt` for the complete list. Key packages:

- **streamlit**: Web interface framework
- **openai**: OpenAI API client
- **mlflow**: Experiment tracking and management
- **pandas**: Data manipulation and analysis
- **Pillow**: Image processing
- **pydeck**: Interactive map visualization
- **python-dotenv**: Environment variable management

## Troubleshooting

**Issue: "OpenAI API key not found"**
- Ensure `OPENAI_API_KEY` is set in your `.env` file
- Or set it in your shell: `export OPENAI_API_KEY=sk-...`

**Issue: MLflow connection error**
- Verify MLflow server is running: `mlflow ui`
- Check `TRACKING_URI` in `.env` matches your server address

**Issue: "Dataset directory not found"**
- Verify `DATASET_PATH` exists and is correctly specified in `.env`
- Use absolute or relative paths as needed