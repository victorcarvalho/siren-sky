import os
import time
import mlflow
import pandas as pd

from ultralytics import YOLO

from huggingface_hub import hf_hub_download

# ============================================================
# CONFIGURAÇÕES
# ============================================================

IMAGE_DIR = "images"

MODEL_PATH = hf_hub_download(
    repo_id="FathomNet/trash-detector",
    filename="trash_mbari_09072023_640imgsz_50epochs_yolov8.pt"
)

CONFIDENCE = 0.6

MLFLOW_EXPERIMENT = "Siren Sky - FathomNet Trash Detector"

# ============================================================
# MODELO
# ============================================================

print("Carregando modelo...")

model = YOLO(MODEL_PATH)

print("Modelo carregado.")


# ============================================================
# ENCONTRAR IMAGENS
# ============================================================

images = []

for filename in os.listdir(IMAGE_DIR):

    lower = filename.lower()

    if not lower.endswith((".jpg", ".jpeg", ".png")):
        continue

    if lower.startswith("com lixo"):
        images.append(
            os.path.join(IMAGE_DIR, filename)
        )

    elif lower.startswith("sem lixo"):
        images.append(
            os.path.join(IMAGE_DIR, filename)
        )


if not images:
    raise RuntimeError(
        "Nenhuma imagem encontrada na pasta images."
    )


print(f"{len(images)} imagens encontradas.")


# ============================================================
# MLFLOW
# ============================================================

mlflow.set_experiment(
    MLFLOW_EXPERIMENT
)


with mlflow.start_run() as run:

    # --------------------------------------------------------
    # PARÂMETROS
    # --------------------------------------------------------

    mlflow.log_params({
        "model": MODEL_PATH,
        "confidence_threshold": CONFIDENCE,
        "total_images": len(images)
    })


    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    results_data = []

    total_correct = 0

    total_inference_time = 0


    # --------------------------------------------------------
    # INFERÊNCIA
    # --------------------------------------------------------

    for index, image_path in enumerate(images):

        filename = os.path.basename(image_path)

        print(
            f"[{index + 1}/{len(images)}] "
            f"{filename}"
        )


        # ----------------------------------------------------
        # RÓTULO ESPERADO
        # ----------------------------------------------------

        lower_filename = filename.lower()

        if lower_filename.startswith("com lixo"):
            expected = True

        elif lower_filename.startswith("sem lixo"):
            expected = False

        else:
            continue


        # ----------------------------------------------------
        # INFERÊNCIA
        # ----------------------------------------------------

        start = time.perf_counter()

        results = model.predict(
            source=image_path,
            conf=CONFIDENCE,
            verbose=False
        )

        end = time.perf_counter()


        inference_time = end - start

        total_inference_time += inference_time


        # ----------------------------------------------------
        # ANALISAR DETECÇÕES
        # ----------------------------------------------------

        result = results[0]

        detected = (
            result.boxes is not None
            and len(result.boxes) > 0
        )


        # ----------------------------------------------------
        # CONFIANÇA
        # ----------------------------------------------------

        if detected:

            confidences = (
                result.boxes.conf
                .cpu()
                .numpy()
            )

            max_confidence = float(
                confidences.max()
            )

        else:

            max_confidence = 0.0


        # ----------------------------------------------------
        # ACERTO
        # ----------------------------------------------------

        correct = (
            detected == expected
        )

        if correct:
            total_correct += 1


        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        results_data.append({

            "image": filename,

            "expected": (
                "com lixo"
                if expected
                else "sem lixo"
            ),

            "detected": detected,

            "prediction": (
                "com lixo"
                if detected
                else "sem lixo"
            ),

            "confidence": max_confidence,

            "inference_time": inference_time,

            "correct": correct

        })


    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        results_data
    )


    # ========================================================
    # MÉTRICAS
    # ========================================================

    accuracy = (
        total_correct /
        len(df)
    )

    average_inference_time = (
        total_inference_time /
        len(df)
    )


    # ========================================================
    # RESULTADOS
    # ========================================================

    print()
    print("=" * 50)
    print("RESULTADOS")
    print("=" * 50)

    print(
        f"Imagens: {len(df)}"
    )

    print(
        f"Acertos: {total_correct}"
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        f"Tempo médio: "
        f"{average_inference_time:.4f} s/imagem"
    )

    print("=" * 50)


    # ========================================================
    # MLFLOW
    # ========================================================

    mlflow.log_metrics({

        "accuracy": accuracy,

        "correct_images": total_correct,

        "average_inference_time":
            average_inference_time,

        "total_inference_time":
            total_inference_time

    })


    # --------------------------------------------------------
    # RESULTADOS INDIVIDUAIS
    # --------------------------------------------------------

    results_file = "fathomnet_results.csv"

    df.to_csv(
        results_file,
        index=False
    )

    mlflow.log_artifact(
        results_file
    )


    # ========================================================
    # MATRIZ DE CONFUSÃO
    # ========================================================

    true_positive = len(
        df[
            (df["expected"] == "com lixo") &
            (df["prediction"] == "com lixo")
        ]
    )

    true_negative = len(
        df[
            (df["expected"] == "sem lixo") &
            (df["prediction"] == "sem lixo")
        ]
    )

    false_positive = len(
        df[
            (df["expected"] == "sem lixo") &
            (df["prediction"] == "com lixo")
        ]
    )

    false_negative = len(
        df[
            (df["expected"] == "com lixo") &
            (df["prediction"] == "sem lixo")
        ]
    )


    mlflow.log_metrics({

        "true_positive": true_positive,

        "true_negative": true_negative,

        "false_positive": false_positive,

        "false_negative": false_negative

    })


    print()
    print("Matriz de confusão:")
    print()
    print(
        f"Verdadeiro positivo : {true_positive}"
    )

    print(
        f"Verdadeiro negativo : {true_negative}"
    )

    print(
        f"Falso positivo      : {false_positive}"
    )

    print(
        f"Falso negativo      : {false_negative}"
    )


    print()
    print("Run MLflow:")
    print(run.info.run_id)