import torch
import torch.nn as nn
import torch.optim as optim
import logging


def train_model(model, train_loader, val_loader, device, epochs=10):
    criterion = nn.CrossEntropyLoss(ignore_index=-1)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    model.to(device)

    for epoch in range(epochs):

        # Training
        model.train() # Bật tính năng training
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        train_batch_errors = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            try:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()

            except Exception as e:
                logging.error(f"Error during training: Batch {batch_idx} - Error: {str(e)}")
                train_batch_errors += 1
                continue

        train_accuracy = 100 * train_correct / train_total if train_total > 0 else 0
        avg_train_loss = train_loss / (len(train_loader) - train_batch_errors) if (len(train_loader) - train_batch_errors) > 0 else 0
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_train_loss: .4f}, Accuracy: {train_accuracy: .4f}%")

        if train_batch_errors > 0:
            print(f"Train batch errors: {train_batch_errors}")

        #Validation
        model.eval() # Bật tính năng validate
        val_correct = 0
        val_total = 0
        val_batch_errors = 0

        with torch.no_grad():
            for batch_idx, (images, labels) in enumerate(val_loader):
                try:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()

                except Exception as e:
                    logging.error(f"Error during validation: Batch {batch_idx} - Error: {str(e)}")
                    val_batch_errors += 1
                    continue

        val_accuracy = 100 * val_correct / val_total if val_total > 0 else 0
        print(f"Validation Accuracy: {val_accuracy: .4f}%")
        if val_batch_errors > 0:
            print(f"Validation batch errors: {val_batch_errors}")
