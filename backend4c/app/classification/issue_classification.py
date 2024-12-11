import torch
import pandas as pd
import numpy as np
from transformers import (
    DistilBertTokenizerFast, 
    DistilBertForSequenceClassification,
    Trainer, 
    TrainingArguments
)
from torch.utils.data import Dataset
import os
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class IssueDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts
        self.labels = labels.astype(np.int32)  # Convert labels to int32
        self.tokenizer = tokenizer
        self.max_len = max_len
        logger.debug(f"Dataset initialized with {len(texts)} examples")
        logger.debug(f"Label types: {self.labels.dtype}")
        logger.debug(f"Label range: {np.min(self.labels)} to {np.max(self.labels)}")

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])  # Explicitly convert to int
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        
        try:
            return {
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten(),
                'labels': torch.tensor(label, dtype=torch.long)
            }
        except Exception as e:
            logger.error(f"Error creating tensor for idx {idx}, label {label}")
            logger.error(f"Label type: {type(label)}")
            logger.error(f"Error: {str(e)}")
            raise

class IssueClassifier:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Product mapping
        self.products = [
            'Printer', 'Scanner', 'Laptop', 'Monitor', 'Keyboard', 
            'Mouse', 'Projector', 'Fax machine', 'Calculator', 'Shredder',
            'Photocopier', 'Whiteboard', 'Paper shredder', 'Desk lamp',
            'External hard drive', 'Conference phone', 'Label maker', 
            'Document camera', 'Wireless presenter', 'USB hub'
        ]
        self.label2idx = {label: idx for idx, label in enumerate(self.products)}
        self.idx2label = {idx: label for label, idx in self.label2idx.items()}
        
        logger.info(f"Initialized with {len(self.products)} product categories")
        logger.debug(f"Product mapping: {self.label2idx}")
        
        # Initialize tokenizer and model
        self.tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
        self.model = DistilBertForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", 
            num_labels=len(self.products)
        )
        
        # Check if saved model exists
        model_path = './data4c/results/model_distill_bert.pth'
        if os.path.exists(model_path):
            try:
                logger.info(f"Loading saved model from {model_path}")
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info("Model loaded successfully")
                self.model.eval()  # Set model to evaluation mode
            except Exception as e:
                logger.error(f"Error loading saved model: {str(e)}")
                logger.info("Initializing new model instead")
        else:
            logger.info("No saved model found. Model will need training before use.")
        
        self.model.to(self.device)

    def train(self, train_file='data4c/customer_queries.csv'):
        """
        Fine-tune the model on the training data
        """
        # Check if model is already trained
        model_path = './data4c/results/model_distill_bert.pth'
        if os.path.exists(model_path):
            logger.info("Model already trained and saved. Skipping training.")
            return True
            
        logger.info(f"Starting training process...")
        logger.info(f"Loading training data from {train_file}")
        
        try:
            # Load and prepare training data
            df = pd.read_csv(train_file)
            logger.info(f"Loaded {len(df)} training examples")
            
            # Convert product names to numeric labels
            labels = pd.Series(df['Product'].map(self.label2idx))
            
            # Check for any NaN values in labels
            if labels.isna().any():
                invalid_products = df[labels.isna()]['Product'].unique()
                logger.error(f"Found invalid product names: {invalid_products}")
                raise ValueError(f"Invalid product names found: {invalid_products}")
            
            labels = labels.values
            texts = df['Query'].values
            
            logger.info("Sample of training data:")
            for i in range(min(5, len(df))):
                logger.info(f"Text: {texts[i]}")
                logger.info(f"Product: {df['Product'].iloc[i]} (Label: {labels[i]})")
            
            logger.info("\nLabel distribution:")
            label_dist = pd.Series(df['Product']).value_counts()
            logger.info(str(label_dist))
            
            # Create dataset
            train_dataset = IssueDataset(
                texts=texts,
                labels=labels,
                tokenizer=self.tokenizer
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir='./data4c/results',
                num_train_epochs=5,
                per_device_train_batch_size=16,
                warmup_steps=500,
                weight_decay=0.01,
                logging_dir='./data4c/logs',
                logging_steps=10,
                save_steps=10000,
                save_total_limit=2,
            )

            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
            )

            logger.info("Starting training...")
            trainer.train()
            
            # Save the model
            model_save_path = './data4c/results/model_distill_bert.pth'
            torch.save(self.model.state_dict(), model_save_path)
            logger.info(f"Model saved to {model_save_path}")
            
            # Test the model on sample queries
            logger.info("\nTesting model on sample queries:")
            test_queries = [
                "How do I connect my printer to WiFi?",
                "The scanner is not working",
                "Laptop battery not charging",
                "Monitor display is blank"
            ]
            for query in test_queries:
                code, name = self.classify(query)
                logger.info(f"Query: {query}")
                logger.info(f"Predicted: {name} (code: {code})\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}", exc_info=True)
            return False

    def classify(self, query):
        """
        Classify a customer query and return product code and name.
        """
        logger.info(f"Classifying query: {query}")
        
        # Ensure model is in eval mode
        self.model.eval()
        
        # Tokenize input
        inputs = self.tokenizer(
            query,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt"
        )
        
        # Move input tensors to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Get probabilities
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get top prediction
        product_code = torch.argmax(outputs.logits).item()
        product_name = self.idx2label[product_code]
        
        # Log classification details
        logger.info(f"Classification details for: '{query}'")
        logger.info(f"Predicted class: {product_name} (code: {product_code})")
        logger.info("Top 3 predictions:")
        top_probs, top_indices = torch.topk(probs, min(3, len(self.products)))
        for prob, idx in zip(top_probs[0], top_indices[0]):
            logger.info(f"{self.idx2label[idx.item()]}: {prob.item():.3f}")
        
        return product_code, product_name

# Training usage example
if __name__ == "__main__":
    classifier = IssueClassifier()
    success = classifier.train()
    if success:
        logger.info("Training completed successfully")
        # Test the trained model
        test_queries = [
            "How do I connect my printer to Wi-Fi?",
            "My scanner is not working properly",
            "Laptop won't turn on",
            "Monitor keeps flickering"
        ]
        for query in test_queries:
            product_code, product_name = classifier.classify(query)
            logger.info(f"\nTest Query: {query}")
            logger.info(f"Predicted Product: {product_name}")
            logger.info(f"Product Code: {product_code}")
