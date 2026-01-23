from setuptools import find_packages, setup

setup(
    name="sj-das",
    version="0.1.0",
    description="Smart Jacquard Design Automation System",
    author="SJ-DAS Team",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
        "opencv-python",
        "numpy",
        "Pillow",
        "torch",
        "torchvision",
        "diffusers",
        "transformers",
        "accelerate",
        "moderngl",
        "PyGLM",
        "fastapi",
        "uvicorn",
        "python-multipart"
    ],
    entry_points={
        "console_scripts": [
            "sj-das=sj_das.main:main",
        ],
    },
)
