import os
import csv
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer
from PIL import Image

class PadChestDataset(Dataset):
    """
    Generic PadChest dataset loader.
    """

    def __init__(self, args, csv_file, img_prefix, preprocess=None):
        self.args = args
        self.img_prefix = img_prefix
        self.preprocess = preprocess

        self.tokenizer = GPT2Tokenizer.from_pretrained(args.decoder_model)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        prompt_enc = self.tokenizer(args.streeing_prompt, return_tensors="pt")
        self.prompt_ids = prompt_enc.input_ids.squeeze(0)
        self.prompt_mask = prompt_enc.attention_mask.squeeze(0)

        self.db = []
        
        print(f"=> Loading dataset from {csv_file}")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_id = row['ImageID']
                report = row['Report']
                
                # Skip if report is empty
                if not report or not report.strip():
                    continue
                
                caption = report.strip() + " <|endoftext|>"
                
                self.db.append({
                    "image_id": image_id,
                    "caption": caption
                })

        print(f"=> Loaded {len(self.db)} samples")

    def __len__(self):
        return len(self.db)

    def __getitem__(self, idx):
        while True:
            sample = self.db[idx]
            image_file = os.path.join(self.img_prefix, sample["image_id"])

            try:
                with Image.open(image_file) as cv_image:
                    cv_image = cv_image.convert("RGB")
                    if self.preprocess is not None:
                        image = self.preprocess(cv_image)
                    else:
                        image = cv_image
                break # successfully loaded image
            except (FileNotFoundError, OSError):
                # If the image doesn't exist or is corrupted, try the next one
                idx = (idx + 1) % len(self.db)

        target_enc = self.tokenizer(sample["caption"], padding="max_length", truncation=True,
                                    max_length=self.args.max_seq_len, return_tensors="pt")

        target_ids = target_enc.input_ids.squeeze(0)
        target_mask = target_enc.attention_mask.squeeze(0)

        return {
            "image": image,

            "prompt_ids": self.prompt_ids,
            "prompt_mask": self.prompt_mask,

            "target_ids": target_ids,
            "target_mask": target_mask,

            "caption": sample["caption"],
            "category_name": "xray",
        }
