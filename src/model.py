from esm.models.esm3 import ESM3
from esm.sdk.api import ESM3InferenceClient, ESMProtein, GenerationConfig
from huggingface_hub import login
from .config import HF_TOKEN, MODEL_NAME

def initialize_model():
    if not HF_TOKEN:
        raise ValueError("Please set the HF_TOKEN environment variable")
    login(HF_TOKEN)
    return ESM3.from_pretrained(MODEL_NAME).to("cpu")

def predict_sequence(model: ESM3InferenceClient, prompt: str, temperature: float, do_structure: bool):
    protein = ESMProtein(sequence=prompt)
    protein = model.generate(protein, GenerationConfig(track="sequence", num_steps=8, temperature=temperature))
    
    if not do_structure:
        return protein.sequence, None, None
        
    protein = model.generate(protein, GenerationConfig(track="structure", num_steps=8))
    protein.to_pdb("./generation.pdb")
    
    seq = protein.sequence
    protein.sequence = None
    protein = model.generate(protein, GenerationConfig(track="sequence", num_steps=8))
    protein.coordinates = None
    protein = model.generate(protein, GenerationConfig(track="structure", num_steps=8))
    protein.to_pdb("./round_tripped.pdb")
    
    return seq, "./generation.pdb", "./round_tripped.pdb"