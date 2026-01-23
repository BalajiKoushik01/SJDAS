from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, utils


class PatternDataset(Dataset):
    def __init__(self, root_dir, image_size=64):
        self.root_dir = Path(root_dir)
        self.image_size = image_size
        self.files = sorted([f for f in self.root_dir.glob(
            '*') if f.suffix.lower() in ['.jpg', '.png', '.bmp']])

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        img_path = self.files[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            return self.transform(image)
        except Exception:
            # Return black image on error
            return torch.zeros(3, self.image_size, self.image_size)

# Weights initialization


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)


class Generator(nn.Module):
    def __init__(self, nz=100, ngf=64, nc=3):
        super().__init__()
        self.main = nn.Sequential(
            # input is Z, going into a convolution
            nn.ConvTranspose2d(nz, ngf * 8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(ngf * 8),
            nn.ReLU(True),
            # state size. (ngf*8) x 4 x 4
            nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 4),
            nn.ReLU(True),
            # state size. (ngf*4) x 8 x 8
            nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.ReLU(True),
            # state size. (ngf*2) x 16 x 16
            nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(True),
            # state size. (ngf) x 32 x 32
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
            nn.Tanh()
            # state size. (nc) x 64 x 64
        )

    def forward(self, input):
        return self.main(input)


class Discriminator(nn.Module):
    def __init__(self, nc=3, ndf=64):
        super().__init__()
        self.main = nn.Sequential(
            # input is (nc) x 64 x 64
            nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf) x 32 x 32
            nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 2),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*2) x 16 x 16
            nn.Conv2d(ndf * 2, ndf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 4),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*4) x 8 x 8
            nn.Conv2d(ndf * 4, ndf * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 8),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*8) x 4 x 4
            nn.Conv2d(ndf * 8, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input)


class PatternGANTrainer:
    def __init__(self, data_dir, output_dir='models/gan'):
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu")
        self.data_dir = data_dir
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Hyperparams
        self.nz = 100
        self.ngf = 64
        self.ndf = 64
        self.lr = 0.0002
        self.beta1 = 0.5

        self.netG = Generator(self.nz, self.ngf).to(self.device)
        self.netG.apply(weights_init)

        self.netD = Discriminator(ndf=self.ndf).to(self.device)
        self.netD.apply(weights_init)

        self.criterion = nn.BCELoss()
        self.optimizerD = optim.Adam(
            self.netD.parameters(), lr=self.lr, betas=(
                self.beta1, 0.999))
        self.optimizerG = optim.Adam(
            self.netG.parameters(), lr=self.lr, betas=(
                self.beta1, 0.999))

    def train(self, epochs=50, batch_size=32, progress_callback=None):
        dataset = PatternDataset(self.data_dir)
        if len(dataset) == 0:
            raise ValueError(f"No images found in {self.data_dir}")

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0)  # 0 workers for Windows safety

        print(f"Starting Training Loop on {self.device}...")

        for epoch in range(epochs):
            for i, data in enumerate(dataloader):
                # 1. Update D network: maximize log(D(x)) + log(1 - D(G(z)))
                self.netD.zero_grad()
                real_cpu = data.to(self.device)
                b_size = real_cpu.size(0)
                label = torch.full(
                    (b_size,), 1., dtype=torch.float, device=self.device)

                output = self.netD(real_cpu).view(-1)
                errD_real = self.criterion(output, label)
                errD_real.backward()
                output.mean().item()

                noise = torch.randn(b_size, self.nz, 1, 1, device=self.device)
                fake = self.netG(noise)
                label.fill_(0.)

                output = self.netD(fake.detach()).view(-1)
                errD_fake = self.criterion(output, label)
                errD_fake.backward()
                output.mean().item()
                errD = errD_real + errD_fake
                self.optimizerD.step()

                # 2. Update G network: maximize log(D(G(z)))
                self.netG.zero_grad()
                label.fill_(1.)  # fake labels are real for generator cost
                output = self.netD(fake).view(-1)
                errG = self.criterion(output, label)
                errG.backward()
                output.mean().item()
                self.optimizerG.step()

                if i % 50 == 0:
                    print(
                        f'[{epoch}/{epochs}][{i}/{len(dataloader)}] Loss_D: {errD.item():.4f} Loss_G: {errG.item():.4f}')

            # Progress update
            if progress_callback:
                progress_callback(int((epoch + 1) / epochs * 100),
                                  f"Epoch {epoch+1} Loss: {errG.item():.4f}")

            # Save checkpoint sample
            if (epoch + 1) % 10 == 0:
                with torch.no_grad():
                    fake = self.netG(
                        torch.randn(
                            64,
                            self.nz,
                            1,
                            1,
                            device=self.device)).detach().cpu()
                vutils_path = self.output_dir / f"epoch_{epoch+1}.png"
                utils.save_image(fake, vutils_path, normalize=True)

        # Save Final Model
        torch.save(self.netG.state_dict(), self.output_dir / "generator.pth")
        torch.save(
            self.netD.state_dict(),
            self.output_dir /
            "discriminator.pth")
        print("Training Finished!")
        return str(self.output_dir / "generator.pth")

    def generate(self, count=1):
        """Generate 'count' designs using trained model"""
        model_path = self.output_dir / "generator.pth"
        if not model_path.exists():
            return []

        self.netG.load_state_dict(
            torch.load(
                model_path,
                map_location=self.device))
        self.netG.eval()

        designs = []
        with torch.no_grad():
            for _ in range(count):
                noise = torch.randn(1, self.nz, 1, 1, device=self.device)
                fake = self.netG(noise).detach().cpu()
                # Convert to numpy [0,1] -> [0,255]
                img = fake[0].permute(1, 2, 0).numpy()
                img = ((img * 0.5 + 0.5) * 255).astype(np.uint8)
                # BGR for OpenCV
                img = img[..., ::-1].copy()
                designs.append(img)

        return designs
