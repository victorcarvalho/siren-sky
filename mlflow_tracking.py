import mlflow
from mlflow.exceptions import MlflowException


def configure_mlflow(tracking_uri, experiment_name):
    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
    except MlflowException as exc:
        raise RuntimeError(
            f"Could not connect to MLflow tracking server at {tracking_uri}. "
            "Start the MLflow server first, or update TRACKING_URI in .env."
        ) from exc

    mlflow.openai.autolog()
