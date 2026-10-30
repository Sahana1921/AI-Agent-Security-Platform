import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_PATH = "./model"


# Load tokenizer and trained model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()


def predict_prompt(prompt):

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)

        prediction = torch.argmax(probabilities, dim=1).item()

        confidence = probabilities[0][prediction].item()


    if prediction == 1:
        classification = "Prompt Injection"
    else:
        classification = "Benign"


    return classification, confidence


print("====================================")
print("AI Agent Security - Prompt Detector")
print("====================================")

while True:

    prompt = input("\nEnter prompt (type 'exit' to stop): ")

    if prompt.lower() == "exit":
        break

    classification, confidence = predict_prompt(prompt)

    print("\nClassification:", classification)
    print("Confidence:", round(confidence * 100, 2), "%")