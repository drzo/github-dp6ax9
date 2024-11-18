from setuptools import setup, find_packages

setup(
    name="esm_protein_prediction",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch==2.2.0",
        "gradio_molecule3d==0.0.5",
        "accelerate==0.30.1",
        "huggingface_hub==0.19.4",
        "gradio==5.5.0",
        "esm==2.0.0",
        "numpy==1.24.3"
    ],
    python_requires=">=3.8",
    extra_requires={
        "dev": ["pytest"]
    }
)