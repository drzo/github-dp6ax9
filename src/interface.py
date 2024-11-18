import gradio as gr
from gradio_molecule3d import Molecule3D
from .model import initialize_model, predict_sequence
from .visualization import read_mol, create_molecule_viewer

def create_empty_pdb():
    with open("./empty.pdb", "w") as f:
        f.write("\n")
    return "./empty.pdb"

def prediction(prompt, temperature, do_structure):
    model = initialize_model()
    do_structure = do_structure == "Yes"
    
    seq, gen_pdb, round_pdb = predict_sequence(model, prompt, temperature, do_structure)
    
    if not do_structure:
        empty_pdb = create_empty_pdb()
        return (
            seq,
            "Inverse folding and re-generation not enabled",
            "<h3>Structure reconstruction not enabled</h3>",
            "<h3>Inverse folding and re-generation not enabled</h3>",
            empty_pdb,
            empty_pdb
        )
    
    html = create_molecule_viewer(read_mol(gen_pdb))
    html1 = create_molecule_viewer(read_mol(round_pdb))
    
    return seq, seq, html, html1, round_pdb, gen_pdb

def create_interface():
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
    
    return gr.Interface(
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