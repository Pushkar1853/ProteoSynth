from flask import Flask, render_template, request, send_file
import random
import subprocess
import os
import zipfile

app = Flask(__name__)

PHI_RANGE = (-135, 135)
PSI_RANGE = (-45, 45)
PSI_RANGE_2 = (-90, -150)

AA_CODES = {
    "A": "ALA",
    "R": "ARG",
    "N": "ASN",
    "D": "ASP",
    "C": "CYS",
    "Q": "GLN",
    "E": "GLU",
    "G": "GLY",
    "H": "HIS",
    "I": "ILE",
    "L": "LEU",
    "K": "LYS",
    "M": "MET",
    "F": "PHE",
    "P": "PRO",
    "S": "SER",
    "T": "THR",
    "W": "TRP",
    "Y": "TYR",
    "V": "VAL",
}

AA_LIST = list(AA_CODES.values()) + ["UNK"]

def generate_line(exclude_aa=None):
    aa_list = [aa for aa in AA_LIST if aa != exclude_aa]
    res_aa = random.choice(aa_list)
    phi = round(random.uniform(*PHI_RANGE), 2)
    psi = round(random.uniform(*PSI_RANGE), 2)
    return "res {} phi {} psi {}".format(res_aa, phi, psi)

def generate_model(num_lines, exclude_aa):
    model_data = []
    for _ in range(num_lines):
        model_data.append(generate_line(exclude_aa))
    return model_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_lines = int(request.form["num_lines"])
        exclude_aa = request.form["exclude_aa"]
        num_models = int(request.form["num_models"])  # Retrieve num_models from the form

        zip_filename = "protein_data.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for i in range(num_models):
                filename = f"random_protein_data_{i}.rib"
                with open(filename, "w") as outfile:
                    outfile.write("TITLE RIBOSOME 1\n")
                    model_data = generate_model(num_lines, exclude_aa)
                    for line in model_data:
                        outfile.write("{}\n".format(line))

                # Execute subprocess to generate .pdb file
                try:
                    subprocess.run(["./ribosome", filename, f"output_{i}.pdb", "res.zmat"], check=True)
                except subprocess.CalledProcessError as e:
                    # Log the error and continue to the next model
                    print(f"Error generating .pdb file for model {i}: {e}")
                    continue

                if os.path.exists(f"output_{i}.pdb"):
                    zipf.write(f"output_{i}.pdb")
                    os.remove(f"output_{i}.pdb")
                else:
                    # Log a warning if the .pdb file is not found
                    print(f"Warning: .pdb file for model {i} not found.")

                # Clean up temporary files
                os.remove(filename)

        return send_file(zip_filename, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
