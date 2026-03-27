"""
Improved Multi-Task Textile Segmentation Model
Segments saree + classifies pattern type + detects weave type
"""

import logging

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torchvision import models
    _TORCH_AVAILABLE = True
except Exception as e:
    logging.warning(f"TextileModel: Torch/Torchvision unavailable: {e}")
    torch = None
    nn = object  # Stub for inheritance
    F = None
    models = None
    _TORCH_AVAILABLE = False


class TextileSegmentationModel(nn.Module if _TORCH_AVAILABLE else object):
    """
    Multi-task model for textile design analysis.

    Tasks:
    1. Segmentation: Segment body/border/pallu (3 classes)
    2. Pattern Classification: Classify pattern type (5 classes: border, pallu, blouse, broket, other)
    3. Weave Classification: Classify weave type (4 classes: jeri, ani, meena, other)
    """

    def __init__(self, num_seg_classes=3, num_pattern_classes=5,
                 num_weave_classes=4):
        super().__init__()

        # Shared encoder: ResNet50 backbone (pretrained on ImageNet)
        resnet = models.resnet50(pretrained=True)

        # Encoder layers
        self.encoder1 = nn.Sequential(
            resnet.conv1,
            resnet.bn1,
            resnet.relu,
            resnet.maxpool
        )  # Output: 64 channels, H/4 x W/4

        self.encoder2 = resnet.layer1  # 256 channels, H/4 x W/4
        self.encoder3 = resnet.layer2  # 512 channels, H/8 x W/8
        self.encoder4 = resnet.layer3  # 1024 channels, H/16 x W/16
        self.encoder5 = resnet.layer4  # 2048 channels, H/32 x W/32

        # Segmentation Decoder (U-Net style with skip connections)
        self.decoder5 = self._decoder_block(2048, 1024)
        self.decoder4 = self._decoder_block(1024 + 1024, 512)
        self.decoder3 = self._decoder_block(512 + 512, 256)
        self.decoder2 = self._decoder_block(256 + 256, 128)
        self.decoder1 = self._decoder_block(128 + 64, 64)

        # Final segmentation head
        self.seg_head = nn.Conv2d(64, num_seg_classes, kernel_size=1)

        # Pattern Classification Head
        self.pattern_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.pattern_fc = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_pattern_classes)
        )

        # Weave Classification Head
        self.weave_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.weave_fc = nn.Sequential(
            nn.Linear(2048, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_weave_classes)
        )

    def _decoder_block(self, in_channels, out_channels):
        """Create decoder block with upsampling."""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Input image tensor [B, 3, H, W]

        Returns:
            dict with:
                - segmentation: [B, num_seg_classes, H, W]
                - pattern: [B, num_pattern_classes]
                - weave: [B, num_weave_classes]
        """
        # Encoder
        e1 = self.encoder1(x)  # [B, 64, H/4, W/4]
        e2 = self.encoder2(e1)  # [B, 256, H/4, W/4]
        e3 = self.encoder3(e2)  # [B, 512, H/8, W/8]
        e4 = self.encoder4(e3)  # [B, 1024, H/16, W/16]
        e5 = self.encoder5(e4)  # [B, 2048, H/32, W/32]

        # Classification heads (from bottleneck features)
        pattern_features = self.pattern_pool(e5).view(e5.size(0), -1)
        pattern_logits = self.pattern_fc(pattern_features)

        weave_features = self.weave_pool(e5).view(e5.size(0), -1)
        weave_logits = self.weave_fc(weave_features)

        # Segmentation decoder
        d5 = self.decoder5(e5)
        d5 = F.interpolate(d5,
                           size=e4.shape[2:],
                           mode='bilinear',
                           align_corners=False)

        d4 = torch.cat([d5, e4], dim=1)
        d4 = self.decoder4(d4)
        d4 = F.interpolate(d4,
                           size=e3.shape[2:],
                           mode='bilinear',
                           align_corners=False)

        d3 = torch.cat([d4, e3], dim=1)
        d3 = self.decoder3(d3)
        d3 = F.interpolate(d3,
                           size=e2.shape[2:],
                           mode='bilinear',
                           align_corners=False)

        d2 = torch.cat([d3, e2], dim=1)
        d2 = self.decoder2(d2)
        d2 = F.interpolate(d2,
                           size=e1.shape[2:],
                           mode='bilinear',
                           align_corners=False)

        d1 = torch.cat([d2, e1], dim=1)
        d1 = self.decoder1(d1)

        # Final segmentation output
        seg = self.seg_head(d1)
        seg = F.interpolate(seg,
                            size=x.shape[2:],
                            mode='bilinear',
                            align_corners=False)

        return {
            'segmentation': seg,
            'pattern': pattern_logits,
            'weave': weave_logits
        }


class TextileLoss(nn.Module):
    """Combined loss for multi-task learning."""

    def __init__(self, seg_weight=1.0, pattern_weight=0.3, weave_weight=0.2):
        super().__init__()
        self.seg_weight = seg_weight
        self.pattern_weight = pattern_weight
        self.weave_weight = weave_weight

        # Loss functions
        self.seg_criterion = self._dice_ce_loss
        self.pattern_criterion = nn.CrossEntropyLoss()
        self.weave_criterion = nn.CrossEntropyLoss()

    def _dice_ce_loss(self, pred, target):
        """Dice + CrossEntropy loss for segmentation."""
        ce_loss = F.cross_entropy(pred, target)

        # Dice loss
        pred_soft = F.softmax(pred, dim=1)
        target_one_hot = F.one_hot(
            target, num_classes=pred.shape[1]).permute(
            0, 3, 1, 2).float()

        intersection = (pred_soft * target_one_hot).sum(dim=(2, 3))
        union = pred_soft.sum(dim=(2, 3)) + target_one_hot.sum(dim=(2, 3))
        dice = (2.0 * intersection + 1) / (union + 1)
        dice_loss = 1 - dice.mean()

        return ce_loss + dice_loss

    def forward(self, outputs, targets):
        """
        Calculate combined loss.

        Args:
            outputs: dict with 'segmentation', 'pattern', 'weave'
            targets: dict with 'seg_mask', 'pattern_label', 'weave_label'

        Returns:
            total_loss, loss_dict
        """
        # Individual losses
        seg_loss = self.seg_criterion(
            outputs['segmentation'], targets['seg_mask'])
        pattern_loss = self.pattern_criterion(
            outputs['pattern'], targets['pattern_label'])
        weave_loss = self.weave_criterion(
            outputs['weave'], targets['weave_label'])

        # Combined loss
        total_loss = (
            self.seg_weight * seg_loss +
            self.pattern_weight * pattern_loss +
            self.weave_weight * weave_loss
        )

        loss_dict = {
            'total': total_loss.item(),
            'segmentation': seg_loss.item(),
            'pattern': pattern_loss.item(),
            'weave': weave_loss.item()
        }

        return total_loss, loss_dict


def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test model
    print("Testing Textile Segmentation Model...")

    model = TextileSegmentationModel()
    print(f"Model parameters: {count_parameters(model):,}")

    # Test forward pass
    x = torch.randn(2, 3, 512, 512)
    outputs = model(x)

    print("\nOutput shapes:")
    print(f"  Segmentation: {outputs['segmentation'].shape}")
    print(f"  Pattern: {outputs['pattern'].shape}")
    print(f"  Weave: {outputs['weave'].shape}")

    # Test loss
    targets = {
        'seg_mask': torch.randint(0, 3, (2, 512, 512)),
        'pattern_label': torch.randint(0, 5, (2,)),
        'weave_label': torch.randint(0, 4, (2,))
    }

    criterion = TextileLoss()
    loss, loss_dict = criterion(outputs, targets)

    print("\nLoss values:")
    for k, v in loss_dict.items():
        print(f"  {k}: {v:.4f}")

    print("\n✅ Model test successful!")
