from backend.classification_service import DEFAULT_SETTINGS, classify_image_path
from backend.classifiers import create_openai_client
from backend.config import (
    DATASET_PATH,
    EXPERIMENT_NAME,
    IMAGE_EXTENSIONS,
    TRACKING_URI,
    require_openai_api_key,
)
from experiments.mlflow_tracking import configure_mlflow


def iter_images(dataset_path):
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

    for category_path in sorted(path for path in dataset_path.iterdir() if path.is_dir()):
        for image_path in sorted(category_path.iterdir()):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                yield category_path.name, image_path


def print_summary(results):
    print("\n" + "=" * 60)
    print("CLASSIFICATION RESULTS")
    print("=" * 60)
    for result in results:
        print(
            f"{result['file']!s:45} | "
            f"{result['category']:12} | "
            f"{result['classification']}"
        )
    print("=" * 60)


def main():
    configure_mlflow(TRACKING_URI, EXPERIMENT_NAME)
    client = None
    if not DEFAULT_SETTINGS.use_simulated_predictions:
        client = create_openai_client(require_openai_api_key())
    results = []

    for category, image_path in iter_images(DATASET_PATH):
        print(f"Processing: {image_path}...")

        try:
            classification = classify_image_path(
                image_path=image_path,
                client=client,
                settings=DEFAULT_SETTINGS,
            )
            print(f"  -> {classification}")
        except Exception as exc:
            classification = f"Error: {exc}"
            print(f"  !! {classification}")

        results.append(
            {
                "file": image_path,
                "category": category,
                "classification": classification,
            }
        )

    print_summary(results)


if __name__ == "__main__":
    main()
