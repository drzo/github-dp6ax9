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