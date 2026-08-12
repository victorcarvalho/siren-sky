import io
import os
from pathlib import Path
import base64
import mlflow
from PIL import Image
from openai import OpenAI
from typing import List
import pandas as pd
import time
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from dotenv import load_dotenv

# ======================================
# CONFIGURAÇÕES
# ======================================

model_dict = {
    "gpt-4o-mini": {
        "preco_input": 0.15 / 1_000_000,
        "preco_output": 0.60 / 1_000_000
    },
    "gpt-4.1-mini": {
        "preco_input": 0.40 / 1_000_000,
        "preco_output": 1.60 / 1_000_000
    },
    "gpt-5-nano": {
        "preco_input": 0.05 / 1_000_000,
        "preco_output": 0.40 / 1_000_000
    },
    "gpt-5-mini": {
        "preco_input": 0.25 / 1_000_000,
        "preco_output": 2.00 / 1_000_000
    },
    "gpt-5.4-nano": {
        "preco_input": 0.20 / 1_000_000,
        "preco_output": 1.25 / 1_000_000
    },
    "gpt-5.4-mini": {
        "preco_input": 0.75 / 1_000_000,
        "preco_output": 2.50 / 1_000_000
    },
}

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-5.4-mini"

if (not OPENAI_API_KEY) or (MODEL not in model_dict):
    raise ValueError("OPENAI_API_KEY não definido ou modelo inválido.")

PRECO_INPUT = model_dict[MODEL]["preco_input"]
PRECO_OUTPUT = model_dict[MODEL]["preco_output"]

PASTA_IMAGENS = "images"

TIPO_IMAGEM = "JPEG"      # JPEG, PNG...
QUALIDADE = 50            # 1-100
RESOLUCAO = 1             # 0.5 = 50%

# Lista vazia OU uma lista de True/False
respostas: List[bool] = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
print(f"Total de imagens: {len(respostas)}")

resultados = []

client = OpenAI(api_key=OPENAI_API_KEY)
imagens = sorted(Path(PASTA_IMAGENS).glob("*"))

mime = TIPO_IMAGEM.lower()
if mime == "jpg":
    mime = "jpeg"

if len(respostas) not in (0, len(imagens)):
    raise ValueError("respostas deve possuir 0 elementos ou o mesmo número de imagens.")

mlflow.set_experiment("Siren Sky")

with mlflow.start_run(run_name=f"{MODEL}_{TIPO_IMAGEM}_Q{QUALIDADE}_R{RESOLUCAO}"):
    inicio_total = time.perf_counter()

    mlflow.log_param("modelo", MODEL)
    mlflow.log_param("tipo_imagem", TIPO_IMAGEM)
    mlflow.log_param("qualidade", QUALIDADE)
    mlflow.log_param("resolucao", RESOLUCAO)

    for i, arquivo in enumerate(imagens):
        inicio_imagem = time.perf_counter()
        img = Image.open(arquivo)
        largura = int(img.width * RESOLUCAO)
        altura = int(img.height * RESOLUCAO)
        img = img.resize((largura, altura), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        salvar = img

        if TIPO_IMAGEM.upper() == "JPEG":
            salvar = img.convert("RGB")

        salvar.save(buffer, format=TIPO_IMAGEM, quality=QUALIDADE)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        resposta = client.responses.create(
            model=MODEL,
            max_output_tokens=10,
            max_input_tokens=1000,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text":
                                "Responda SOMENTE True ou False.\n"
                                "True = a imagem possui lixo.\n"
                                "False = a imagem não possui lixo."
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/{mime};base64,{image_base64}"
                        }
                    ]
                }
            ]
        )

        tempo_imagem = time.perf_counter() - inicio_imagem
        texto = resposta.output_text.strip().lower()

        if texto == "true":
            classificacao = True
        elif texto == "false":
            classificacao = False
        else:
            raise ValueError(f"Resposta inválida da OpenAI: {texto}")

        print(f"{arquivo.name}: {classificacao}")

        if len(respostas):
            correto = classificacao == respostas[i]
            resultados.append({
                "imagem": arquivo.name,
                "esperado": respostas[i],
                "predito": classificacao,
                "correto": correto,
                "tempo": tempo_imagem,

                "input_tokens": resposta.usage.input_tokens,
                "output_tokens": resposta.usage.output_tokens,
                "total_tokens": resposta.usage.total_tokens,

                "preco_input": PRECO_INPUT * resposta.usage.input_tokens,
                "preco_output": PRECO_OUTPUT * resposta.usage.output_tokens,
                "preco_total": PRECO_INPUT * resposta.usage.input_tokens + PRECO_OUTPUT * resposta.usage.output_tokens,

                "resposta": resposta.output_text,
                "largura": img.width,
                "altura": img.height,
                "bytes": len(buffer.getvalue()),
            })

    if len(respostas):
        corretas = [r for r in resultados if r["correto"]]
        erradas = [r for r in resultados if not r["correto"]]
        y_true = [r["esperado"] for r in resultados]
        y_pred = [r["predito"] for r in resultados]
        
        acuracia = len(corretas) / len(imagens)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        print(f"\nAcurácia: {acuracia:.2%}")

        mlflow.log_metric("accuracy", acuracia)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        mlflow.log_metric("true_positive", tp)
        mlflow.log_metric("true_negative", tn)
        mlflow.log_metric("false_positive", fp)
        mlflow.log_metric("false_negative", fn)

        mlflow.log_metric("total_imagens", len(imagens))
        mlflow.log_metric("total_corretas", len(corretas))
        mlflow.log_metric("total_erradas", len(erradas))

        mlflow.log_metric("tempo_total", time.perf_counter() - inicio_total)
        mlflow.log_metric("tempo_medio", sum(r["tempo"] for r in resultados) / len(resultados))
        mlflow.log_metric("tempo_maximo", max(r["tempo"] for r in resultados))
        mlflow.log_metric("tempo_minimo", min(r["tempo"] for r in resultados))

        mlflow.log_metric("input_tokens", sum(r["input_tokens"] for r in resultados))
        mlflow.log_metric("output_tokens", sum(r["output_tokens"] for r in resultados))
        mlflow.log_metric("total_tokens", sum(r["total_tokens"] for r in resultados))

        mlflow.log_metric("total_preco_input", sum(r["preco_input"] for r in resultados))
        mlflow.log_metric("total_preco_output", sum(r["preco_output"] for r in resultados))
        mlflow.log_metric("total_preco_total", sum(r["preco_total"] for r in resultados))
        mlflow.log_metric("preco_medio",  sum(r["preco_total"] for r in resultados) / len(resultados))
        
        pd.DataFrame(resultados).to_csv("resultados.csv", index=False)
        mlflow.log_artifact("resultados.csv")