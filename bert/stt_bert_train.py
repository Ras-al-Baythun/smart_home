import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def stt_bert_train():
    # Schritt 1: Daten vorbereiten
    df = pd.read_csv('data.csv')

    # Schritt 2: Tokenizer und Modell laden
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Labels zu IDs
    label_dict = {
        "light_on": 1,
        "light_off": 2,
        "temperature": 3,
        "repeat_after_me": 4,
        "current_time": 5
    }

    df['label'] = df['label'].replace(label_dict)

    # Anzahl der Labels prüfen
    num_labels = len(label_dict) + 1  # +1 da Labels von 1 bis 5 gehen

    # Modell laden mit der richtigen Anzahl von Labels
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased', num_labels=num_labels)

    # Trainings- und Validierungsdaten splitten
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42)

    # Schritt 3: Dataset-Klasse erstellen

    class IntentDataset(Dataset):
        def __init__(self, texts, labels):
            self.texts = texts
            self.labels = labels
            self.encodings = tokenizer(
                texts, truncation=True, padding=True, max_length=128)

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx])
                    for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = IntentDataset(train_texts, train_labels)
    val_dataset = IntentDataset(val_texts, val_labels)

    # Schritt 4: Training und Evaluation
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=36,  # Du kannst die Epochenzahl anpassen
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    def compute_metrics(p):
        pred, labels = p
        pred = np.argmax(pred, axis=1)
        accuracy = accuracy_score(labels, pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, pred, average='weighted')
        return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )

    # Training
    trainer.train()

    # Evaluation
    eval_result = trainer.evaluate()
    print(f"Evaluation results: {eval_result}")

    # Speichern des Modells
    model.save_pretrained('./intent_model')
    tokenizer.save_pretrained('./intent_model')

# Modell testen


def predict_intent(text, tokenizer, model, label_dict):
    inputs = tokenizer(text, return_tensors='pt',
                       truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class_idx = probs.argmax().item()
    # -1 da die Labels bei 1 beginnen
    return list(label_dict.keys())[predicted_class_idx - 1]


if __name__ == "__main__":
    model_dir = './intent_model'
    # Beispielvorhersage
    label_dict = {
        1: "light_on",
        2: "light_off",
        3: "temperature",
        4: "repeat_after_me",
        5: "current_time"
    }

    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model = BertForSequenceClassification.from_pretrained(model_dir)
    text = "Wie ist das Wetter in Berlin?"
    predicted_intent = predict_intent(text, tokenizer, model, label_dict)
    print(f"Predicted Intent: {predicted_intent}")
