import os
import json
import subprocess
import pandas as pd
from pathlib import Path

project_root = Path("/usr/local/google/home/luiskaiser/Documents/morph-testing")
results_dir = project_root / "results"

tasks = [
    "petfinder-pawpularity-score",
    "somics",
    "mimics",
    "aerial-cactus-identification",
    "forest-matrix-rates",
    "forest-matrix-distribution",
    "crop-surrogate-jaegermeyer"
]

dummy_folders = []

for task in tasks:
    folder_name = f"dummy_{task}"
    folder_path = results_dir / folder_name
    folder_path.mkdir(exist_ok=True)
    dummy_folders.append(str(folder_path))
    
    # Create run_meta.json
    with open(folder_path / "run_meta.json", "w") as f:
        json.dump({"task": task, "task_name": task}, f)
        
    # Create submission.csv
    sub_path = folder_path / "submission.csv"
    
    if task == "somics":
        lines = ["site_key,predicted_soc_t_ha"]
        for i in range(100):
            lines.append(f"site_{i},44.37")
        sub_path.write_text("\n".join(lines) + "\n")
    elif task == "mimics":
        lines = ["ID,Model_Stock_t_ha"]
        for i in range(100):
            lines.append(f"{i},120.5")
        sub_path.write_text("\n".join(lines) + "\n")
    elif task == "aerial-cactus-identification":
        # Read valid IDs from test.csv
        test_csv_path = project_root / "testing/eval/aerial-cactus-identification/test_data/test.csv"
        if test_csv_path.exists():
            df = pd.read_csv(test_csv_path)
            df['has_cactus'] = 0.5 # dummy prediction
            df[['id', 'has_cactus']].to_csv(sub_path, index=False)
        else:
            sub_path.write_text("id,has_cactus\n09034a34de0e2015a8a28dfe18f423f6.jpg,0.5\n")
    elif task == "petfinder-pawpularity-score":
        # We created a dummy test.csv with 5 rows
        test_csv_path = project_root / "testing/eval/petfinder-pawpularity-score/test_data/test.csv"
        if test_csv_path.exists():
            df = pd.read_csv(test_csv_path)
            df['Pawpularity'] = 50.0 # dummy prediction
            df[['Id', 'Pawpularity']].to_csv(sub_path, index=False)
        else:
             sub_path.write_text("Id,Pawpularity\n1a8795e64a294ed0c95132e18ee198e1,50.0\n")
    elif task == "crop-surrogate-jaegermeyer":
        sub_path.write_text("id,yield\nmai_firr_49.75_-109.75_2015,7.15\nmai_firr_49.75_-94.75_2015,6.25\n")
    elif task in ["forest-matrix-rates", "forest-matrix-distribution"]:
        sub_path.write_text("run_id\ndummy_run_id\n")
    else:
        sub_path.write_text("id,target\n1,0\n")

print(f"Created dummy folders: {dummy_folders}")

# Run evaluation
folders_str = ",".join([f"results/dummy_{t}" for t in tasks])
cmd = ["poetry", "run", "python", "morph.py", "evaluate", "--folders", folders_str]
print(f"Running command: {' '.join(cmd)}")

try:
    res = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
except Exception as e:
    print(f"Error running evaluation: {e}")
