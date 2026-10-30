import os
import re
import sys

import pandas as pd
import torch
import matplotlib.pyplot as plt

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "test.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml-model",
    "model"
)

RESULTS_PATH = os.path.join(
    BASE_DIR,
    "ml-model",
    "comparative_results.csv"
)

GRAPH_PATH = os.path.join(
    BASE_DIR,
    "ml-model",
    "comparative_performance.png"
)


# --------------------------------------------------
# Check files
# --------------------------------------------------

print("==========================================")
print("AI Agent Security Platform")
print("Comparative Model Evaluation")
print("==========================================")

if not os.path.exists(DATASET_PATH):
    print("ERROR: test.csv not found")
    print(DATASET_PATH)
    sys.exit()

if not os.path.exists(MODEL_PATH):
    print("ERROR: trained model not found")
    print(MODEL_PATH)
    sys.exit()

print("\nDataset:")
print(DATASET_PATH)

print("\nModel:")
print(MODEL_PATH)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("\nLoading test dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

if "text" not in df.columns:
    print("ERROR: 'text' column not found")
    sys.exit()

if "label" not in df.columns:
    print("ERROR: 'label' column not found")
    sys.exit()


# --------------------------------------------------
# Rule-based detector
# --------------------------------------------------

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?(the\s+)?system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"override\s+(the\s+)?system",
    r"bypass\s+(the\s+)?security",
    r"disable\s+(the\s+)?security"
]


def rule_based_predict(prompt):

    prompt = str(prompt).lower()

    for pattern in INJECTION_PATTERNS:

        if re.search(pattern, prompt):
            return 1

    return 0


print("\nRunning Rule-Based detector...")

df["rule_prediction"] = df["text"].apply(
    rule_based_predict
)


# --------------------------------------------------
# Load DistilBERT
# --------------------------------------------------

print("\nLoading DistilBERT model...")

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.to(device)
model.eval()

print("DistilBERT loaded successfully.")


# --------------------------------------------------
# DistilBERT prediction
# --------------------------------------------------

def distilbert_predict(
    texts,
    batch_size=16
):

    predictions = []

    total = len(texts)

    print("\nRunning DistilBERT predictions...")

    for start in range(
        0,
        total,
        batch_size
    ):

        end = min(
            start + batch_size,
            total
        )

        batch = texts[start:end]

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )

        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = model(**inputs)

            batch_predictions = torch.argmax(
                outputs.logits,
                dim=1
            )

        predictions.extend(
            batch_predictions.cpu().numpy().tolist()
        )

        print(
            f"Processed {end}/{total}"
        )

    return predictions


df["distilbert_prediction"] = distilbert_predict(
    df["text"].tolist()
)


# --------------------------------------------------
# Proposed Hybrid detector
# --------------------------------------------------

print("\nGenerating Proposed Hybrid predictions...")

df["hybrid_prediction"] = (
    (df["rule_prediction"] == 1) |
    (df["distilbert_prediction"] == 1)
).astype(int)


# --------------------------------------------------
# Calculate metrics
# --------------------------------------------------

print("\nCalculating performance metrics...")

y_true = df["label"]

methods = {
    "Rule-Based": df["rule_prediction"],
    "DistilBERT": df["distilbert_prediction"],
    "Proposed Hybrid": df["hybrid_prediction"]
}

results = []

for method_name, predictions in methods.items():

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    results.append({
        "Method": method_name,
        "Accuracy": accuracy * 100,
        "Precision": precision * 100,
        "Recall": recall * 100,
        "F1-Score": f1 * 100
    })


results_df = pd.DataFrame(results)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n==========================================")
print("COMPARATIVE RESULTS")
print("==========================================")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


# --------------------------------------------------
# Save results
# --------------------------------------------------

results_df.to_csv(
    RESULTS_PATH,
    index=False
)

print("\nResults saved to:")
print(RESULTS_PATH)


# --------------------------------------------------
# Generate graph
# --------------------------------------------------

metrics = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1-Score"
]

method_names = results_df["Method"].tolist()

x = range(len(metrics))

width = 0.25

plt.figure(
    figsize=(12, 7)
)

for i, method in enumerate(method_names):

    values = results_df[
        results_df["Method"] == method
    ][metrics].values[0]

    positions = [
        value + (i - 1) * width
        for value in x
    ]

    bars = plt.bar(
        positions,
        values,
        width,
        label=method
    )

    for bar, value in zip(
        bars,
        values
    ):

        plt.text(
            bar.get_x() +
            bar.get_width() / 2,

            bar.get_height() + 1,

            f"{value:.2f}",

            ha="center",

            va="bottom",

            fontsize=9
        )


plt.xlabel(
    "Performance Metrics",
    fontsize=12
)

plt.ylabel(
    "Score (%)",
    fontsize=12
)

plt.title(
    "Comparative Performance of Prompt Injection Detection Methods",
    fontsize=15,
    fontweight="bold"
)

plt.xticks(
    [
        value
        for value in x
    ],
    metrics
)

plt.ylim(
    0,
    105
)

plt.legend()

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    GRAPH_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print("\n==========================================")
print("EVALUATION COMPLETED")
print("==========================================")

print("\nGraph saved to:")
print(GRAPH_PATH)