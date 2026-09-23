import time
from tqdm import tqdm

import torch
from torch.cuda.amp import autocast, GradScaler

from utils import AverageMeter, save_checkpoint, load_checkpoint, classification_accuracy


def train_one_epoch(model, train_loader, optimizer, device, epoch,):

    model.train()
    loss_meter = AverageMeter()
    accuracy_meter = AverageMeter()

    batches = tqdm(train_loader, desc=f"Train Epoch {epoch}", leave=False,)

    for batch in batches:

        images = batch["image"].to(device)
        prompt_ids = batch["prompt_ids"].to(device)
        prompt_mask = batch["prompt_mask"].to(device)
        target_ids = batch["target_ids"].to(device)
        target_mask = batch["target_mask"].to(device)
        category = batch["category_name"]  

        loss = model(images, prompt_ids, prompt_mask, target_ids, target_mask)
        
        with torch.no_grad():
            generated_text = model.generate_caption(images, prompt_ids, prompt_mask)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loss_meter.update(loss.item(), images.size(0))
        batches.set_postfix(loss=f"{loss_meter.avg:.4f}")

        batch_accuracy = classification_accuracy(generated_text, category)
        accuracy_meter.update(batch_accuracy, images.size(0))

    return loss_meter.avg,  accuracy_meter.avg


@torch.no_grad()
def validate(args, model, val_loader, device,):

    model.eval()
    loss_meter = AverageMeter()
    accuracy_meter = AverageMeter()

    batches = tqdm(val_loader, desc="Validation", leave=False,)

    for batch in batches:

        images = batch["image"].to(device)
        prompt_ids = batch["prompt_ids"].to(device)
        prompt_mask = batch["prompt_mask"].to(device)
        target_ids = batch["target_ids"].to(device)
        target_mask = batch["target_mask"].to(device)
        category = batch["category_name"]

        loss = model(images, prompt_ids, prompt_mask, target_ids, target_mask)
        generated_text = model.generate_caption(images, prompt_ids, prompt_mask)

        loss_meter.update(loss.item(), images.size(0))
        batches.set_postfix(loss=f"{loss_meter.avg:.4f}")

        batch_accuracy = classification_accuracy(generated_text, category)
        accuracy_meter.update(batch_accuracy, images.size(0))

    return loss_meter.avg, accuracy_meter.avg
