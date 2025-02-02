import os
import gradio as gr
from gradio_molecule3d import Molecule3D
from huggingface_hub import login
from esm.models.esm3 import ESM3
from esm.sdk.api import ESM3InferenceClient, ESMProtein, GenerationConfig

TOKEN = os.getenv("HF_TOKEN", "")

def initialize_model():
    if not TOKEN:
        raise ValueError("Please set the HF_TOKEN environment variable")
    login(TOKEN)
    return ESM3.from_pretrained("esm3_sm_open_v1").to("cpu")

def read_mol(molpath):
    with open(molpath, "r") as fp:
        return "".join(fp.readlines())

def create_molecule_viewer(mol_content):
    return f"""<iframe style="width: 100%; height: 600px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='<!DOCTYPE html>
    <html>
    <head>    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <style>
    body{{ font-family:sans-serif }}
    .mol-container {{
        width: 100%;
        height: 600px;
        position: relative;
    }}
    .mol-container select{{ background-image:None; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.3/jquery.min.js"></script>
    <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    </head>
    <body>  
    <div id="container" class="mol-container"></div>
    <script>
    let pdb = `{mol_content}`;
    $(document).ready(function () {{
        let element = $("#container");
        let config = {{ backgroundColor: "white" }};
        let viewer = $3Dmol.createViewer(element, config);
        viewer.addModel(pdb, "pdb");
        viewer.getModel(0).setStyle({{}}, {{ cartoon: {{ colorscheme:"whiteCarbon" }} }});
        viewer.zoomTo();
        viewer.render();
        viewer.zoom(0.8, 2000);
    }});
    </script>
    </body></html>'></iframe>"""

def create_empty_pdb():
    with open("./empty.pdb", "w") as f:
        f.write("\n")
    return "./empty.pdb"

def prediction(prompt, temperature, do_structure):
    model = initialize_model()
    protein = ESMProtein(sequence=prompt)
    protein = model.generate(protein, GenerationConfig(track="sequence", num_steps=8, temperature=temperature))
    
    if do_structure == "No":
        empty_pdb = create_empty_pdb()
        return (
            protein.sequence,
            "Inverse folding and re-generation not enabled",
            "<h3>Structure reconstruction not enabled</h3>",
            "<h3>Inverse folding and re-generation not enabled</h3>",
            empty_pdb,
            empty_pdb
        )
    
    protein = model.generate(protein, GenerationConfig(track="structure", num_steps=8))
    protein.to_pdb("./generation.pdb")
    
    seq = protein.sequence
    protein.sequence = None
    protein = model.generate(protein, GenerationConfig(track="sequence", num_steps=8))
    protein.coordinates = None
    protein = model.generate(protein, GenerationConfig(track="structure", num_steps=8))
    protein.to_pdb("./round_tripped.pdb")
    
    html = create_molecule_viewer(read_mol("./generation.pdb"))
    html1 = create_molecule_viewer(read_mol("./round_tripped.pdb"))
    
    return seq, protein.sequence, html, html1, "./round_tripped.pdb", "./generation.pdb"

reps = [{
    "model": 0,
    "chain": "",
    "resname": "",
    "style": "stick",
    "color": "whiteCarbon",
    "residue_range": "",
    "around": 0,
    "byres": False,
    "visible": False
}]

demo = gr.Interface(
    fn=prediction,
    inputs=[
        gr.Textbox(
            label="Masked protein sequence",
            info="Use '_' as masking character",
            value="___________________________________________________DQATSLRILNNGHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHLVHWNTKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDPRGLLPESLDYWTYPGSLTTPP___________________________________________________________"
        ),
        gr.Slider(0, 1, label="Temperature"),
        gr.Radio(
            ["Yes", "No"],
            label="Reconstruct structure",
            info="Choose whether to reconstruct structure or not, allowing also inverse folding-powered double check"
        )
    ],
    outputs=[
        gr.Textbox(label="Originally predicted sequence", show_copy_button=True),
        gr.Textbox(label="Inverse folding predicted sequence", show_copy_button=True),
        gr.HTML(label="Predicted 3D structure"),
        gr.HTML(label="Inverse-folding predicted 3D structure"),
        Molecule3D(label="Inverse-folding predicted molecular structure", reps=reps),
        Molecule3D(label="Predicted molecular structure", reps=reps)
    ],
    title="""<h1 align='center'>Proteins with ESM</h1>
    <h2 align='center'>Predict the whole sequence and 3D structure of masked protein sequences!</h2>
    <h3 align='center'>Support this space with a ⭐ on <a href='https://github.com/AstraBert/proteins-w-esm'>GitHub</a></h3>
    <h3 align='center'>Support Evolutionary Scale's ESM with a ⭐ on <a href='https://github.com/evolutionaryscale/esm'>GitHub</a></h3>""",
    examples=[
        ["___________________________________________________DQATSLRILNNGHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHLVHWNTKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDPRGLLPESLDYWTYPGSLTTPP___________________________________________________________", 0.7, "No"],
        ["__________________________________________________________AGQEEYSAMRDQYMRTGEGFLCVFAINNTKSFEDIHQYREQIKRVKDSDDVPMVLVGNKCDLAARTVESRQAQDLARSYGIPYIETSAKTRQGVEDAFYTLVRE___________________________", 0.2, "Yes"],
        ["__________KTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLH________", 0.5, "Yes"]
    ],
    cache_examples=False
)

if __name__ == "__main__":
    demo.launch()