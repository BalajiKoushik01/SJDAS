from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms


class SareeSegmentationDataset(Dataset):
    """Dataset for saree image segmentation"""

    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.transform = transform
        # Robustly find images
        self.images = sorted(
            list(
                self.image_dir.glob('*.jpg')) +
            list(
                self.image_dir.glob('*.png')))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # Load image
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')

        # Load mask
        mask_path = self.mask_dir / f"{img_path.stem}.png"
        # Try finding mask with same name but png extension
        if not mask_path.exists():
            mask_path = self.mask_dir / f"{img_path.stem}.jpg"

        if mask_path.exists():
            mask = Image.open(mask_path).convert('L')
        else:
            # Fallback for inference/testing without masks
            mask = Image.new('L', image.size)

        if self.transform:
            image = self.transform(image)
            mask = transforms.Resize(
                image.shape[1:], interpolation=transforms.InterpolationMode.NEAREST)(mask)
            mask = transforms.ToTensor()(mask)
            mask = (mask * 255).long().squeeze(0)  # 0-3 labels

        return image, mask


class DoubleConv(nn.Module):
    """(Conv2D -> BatchNorm -> ReLU) * 2"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class UNetProduction(nn.Module):
    """Production U-Net for saree segmentation"""

    def __init__(self, in_channels=3, num_classes=4):
        super().__init__()

        # Encoder
        self.enc1 = DoubleConv(in_channels, 64)
        self.enc2 = DoubleConv(64, 128)
        self.enc3 = DoubleConv(128, 256)
        self.enc4 = DoubleConv(256, 512)

        # Bottleneck
        self.bottleneck = DoubleConv(512, 1024)

        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = DoubleConv(1024, 512)

        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(512, 256)

        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(256, 128)

        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(128, 64)

        # Output
        self.out = nn.Conv2d(64, num_classes, kernel_size=1)

        # Pooling
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        # Bottleneck
        b = self.bottleneck(self.pool(e4))

        # Decoder with skip connections
        d4 = self.upconv4(b)
        # Resize to handle odd dimensions if necessary (simple fix for skip
        # connection mismatch)
        if d4.shape != e4.shape:
            d4 = transforms.Resize(e4.shape[2:])(d4)
        d4 = torch.cat([d4, e4], dim=1)
        d4 = self.dec4(d4)

        d3 = self.upconv3(d4)
        if d3.shape != e3.shape:
            d3 = transforms.Resize(e3.shape[2:])(d3)
        d3 = torch.cat([d3, e3], dim=1)
        d3 = self.dec3(d3)

        d2 = self.upconv2(d3)
        if d2.shape != e2.shape:
            d2 = transforms.Resize(e2.shape[2:])(d2)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)

        d1 = self.upconv1(d2)
        if d1.shape != e1.shape:
            d1 = transforms.Resize(e1.shape[2:])(d1)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)

        return self.out(d1)


def train_unet(
    train_dir='dataset/train',
    val_dir='dataset/val',
    epochs=100,
    batch_size=8,
    lr=1e-4,
    device='cuda' if torch.cuda.is_available() else 'cpu'
):
    """Train U-Net model"""
    print(f"Training on device: {device}")

    # Data transforms
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    # Datasets
    train_dataset = SareeSegmentationDataset(
        f'{train_dir}/images',
        f'{train_dir}/masks',
        transform=transform
    )

    val_dataset = SareeSegmentationDataset(
        f'{val_dir}/images',
        f'{val_dir}/masks',
        transform=transform
    )

    # Dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Model
    model = UNetProduction().to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=5
    )

    best_val_loss = float('inf')

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        for images, masks in train_loader:
            images = images.to(device)
            masks = masks.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for images, masks in val_loader:
                images = images.to(device)
                masks = masks.to(device)

                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()

        train_loss /= len(train_loader) if len(train_loader) > 0 else 1
        val_loss /= len(val_loader) if len(val_loader) > 0 else 1

        print(
            f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'models/unet_saree_best.pth')

        scheduler.step(val_loss)

    return model
