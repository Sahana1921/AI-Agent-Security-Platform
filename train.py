import pandas as pd
import torch

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)


# --------------------------------------------------
# 1. Dataset paths
# --------------------------------------------------

TRAIN_PATH = "../dataset/train.csv"
VALIDATION_PATH = "../dataset/validation.csv"

MODEL_NAME = "distilbert-base-uncased"

OUTPUT_DIR = "./model"


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

print("Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)

print("Training samples:", len(train_df))
print("Validation samples:", len(validation_df))


# --------------------------------------------------
# 3. Keep only required columns
# --------------------------------------------------

train_df = train_df[["text", "label"]]
validation_df = validation_df[["text", "label"]]

# Remove missing values
train_df = train_df.dropna()
validation_df = validation_df.dropna()

# Make sure labels are integers
train_df["label"] = train_df["label"].astype(int)
validation_df["label"] = validation_df["label"].astype(int)


# --------------------------------------------------
# 4. Convert Pandas → Hugging Face Dataset
# --------------------------------------------------

train_dataset = Dataset.from_pandas(
    train_df,
    preserve_index=False
)

validation_dataset = Dataset.from_pandas(
    validation_df,
    preserve_index=False
)


# --------------------------------------------------
# 5. Load DistilBERT tokenizer
# --------------------------------------------------

print("\nLoading DistilBERT tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


# --------------------------------------------------
# 6. Tokenization
# --------------------------------------------------

def tokenize_function(examples):

    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )


print("Tokenizing training dataset...")

train_dataset = train_dataset.map(
    tokenize_function,
    batched=True
)

print("Tokenizing validation dataset...")

validation_dataset = validation_dataset.map(
    tokenize_function,
    batched=True
)


# --------------------------------------------------
# 7. Load DistilBERT classifier
# --------------------------------------------------

print("\nLoading DistilBERT classification model...")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2
)


# --------------------------------------------------
# 8. Training configuration
# --------------------------------------------------

training_args = TrainingArguments(

    output_dir=OUTPUT_DIR,

    eval_strategy="epoch",

    learning_rate=2e-5,

    per_device_train_batch_size=8,

    per_device_eval_batch_size=8,

    num_train_epochs=1,

    weight_decay=0.01,

    logging_steps=100,

    save_strategy="epoch",

    load_best_model_at_end=True,

    report_to="none"
)


# --------------------------------------------------
# 9. Create Trainer
# --------------------------------------------------

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=validation_dataset
)


# --------------------------------------------------
# 10. Train
# --------------------------------------------------

print("\nStarting DistilBERT training...")

trainer.train()


# --------------------------------------------------
# 11. Evaluate
# --------------------------------------------------

print("\nEvaluating model...")

results = trainer.evaluate()

print("\nEvaluation Results:")
print(results)


# --------------------------------------------------
# 12. Save model and tokenizer
# --------------------------------------------------

print("\nSaving trained model...")

trainer.save_model(OUTPUT_DIR)

tokenizer.save_pretrained(OUTPUT_DIR)

print("\n===================================")
print("DistilBERT training completed!")
print("Model saved to:", OUTPUT_DIR)
print("===================================")