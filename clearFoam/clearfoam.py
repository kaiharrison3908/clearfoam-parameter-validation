import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import threading
import re
import os
import matplotlib.pyplot as plt


container_name = "clearfoam_container"
host_path = os.getcwd()
container_path = "/home/openfoam/clearFoam"

def check_docker_installed():
    """Check if Docker is installed and available."""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_spinner(label):
    """Start an animated spinner in the given label."""
    spinner_frames = ["⏳", "◴", "◷", "◶", "◵"]
    def animate(i=0):
        if hasattr(label, 'spinner_active') and label.spinner_active:
            label.config(text=f"Downloading OpenFOAM image... {spinner_frames[i % len(spinner_frames)]}")
            label.after(200, lambda: animate(i+1))
    label.spinner_active = True
    animate()

def stop_spinner(label, message):
    """Stop the spinner and show a message."""
    if hasattr(label, 'spinner_active'):
        label.spinner_active = False
    label.config(text=message)

def ensure_openfoam_image(status_label):
    """Ensure the OpenFOAM Docker image is available, pull if missing in background."""
    def worker():
        try:
            # Check if image exists
            result = subprocess.run(
                ["docker", "images", "-q", "opencfd/openfoam-default:2406"],
                capture_output=True, text=True, check=True
            )
            if not result.stdout.strip():
                # Image doesn't exist, start spinner and pull
                root.after(0, lambda: start_spinner(status_label))
                pull = subprocess.run(["docker", "pull", "opencfd/openfoam-default:2406"])
                if pull.returncode == 0:
                    root.after(0, lambda: stop_spinner(status_label, "✅ OpenFOAM image ready."))
                    # Now ensure container after image is ready
                    root.after(100, lambda: threading.Thread(target=ensure_container, daemon=True).start())
                else:
                    root.after(0, lambda: messagebox.showerror("Error", "Failed to download OpenFOAM image."))
                    sys.exit(1)
            else:
                root.after(0, lambda: status_label.config(text="✅ OpenFOAM image found."))
                # Image exists, ensure container
                root.after(0, lambda: threading.Thread(target=ensure_container, daemon=True).start())
        except subprocess.CalledProcessError as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Could not check Docker images:\n{e}"))
            sys.exit(1)

    threading.Thread(target=worker, daemon=True).start()

def ensure_container():
    """Start or create the container if needed."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    if container_name not in result.stdout.split():
        subprocess.run([
            "docker", "run", "-dit",
            "--name", container_name,
            "-v", f"{host_path}:{container_path}",
            "opencfd/openfoam-default:2406"
        ], check=True)
    else:
        subprocess.run(["docker", "start", container_name], check=True)

def run_command(cmd, label, enable_button=None):
    """Run a docker exec command and update label."""
    try:
        label.config(text=f"▶️ Running: {cmd}")
        subprocess.run(["docker", "exec", container_name, "bash", "-lc", cmd], check=True)
        label.config(text=f"✅ Finished: {cmd}")
        if enable_button:
            enable_button.config(state=tk.NORMAL)
    except subprocess.CalledProcessError:
        label.config(text=f"❌ Failed: {cmd}")
        messagebox.showerror("Error", f"Command failed:\n{cmd}")

def prepare_build():
    """Run allwmake and clean before enabling the run button."""
    global status_label, run_button
    def worker():
        run_command(
            f"cd {container_path}/dev/clearFoam/base && ../../../allwmake -j && ./clean",
            status_label,
            run_button
        )
    threading.Thread(target=worker, daemon=True).start()

def run_solver():
    """Execute ./run after build and clean are done."""
    global status_label
    def worker():
        run_command(
            f"cd {container_path}/dev/clearFoam/base && ./run",
            status_label
        )
    threading.Thread(target=worker, daemon=True).start()



def open_set_parameters():
    """Open a window to edit transportProperties parameters."""

    def load_parameters():
        """Fetch and parse the transportProperties file from the container."""
        result = subprocess.run(
            ["docker", "exec", container_name, "cat", f"{container_path}/dev/clearFoam/base/constant/transportProperties"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.splitlines()
        params = {}
        start_parsing = False
        for line in lines:
            if line.strip().startswith("// * * *"):
                start_parsing = True
                continue
            if start_parsing:
                match = re.match(r"(\w+)\s+([^;]+);", line.strip())
                if match:
                    key, value = match.groups()
                    params[key] = value.strip()
        return params
    
    def get_parameter_units():
        """Return a dictionary mapping parameter names to their units based on dimensionSet."""
        # dimensionSet order: kg | m | s | K | mol | A | cd
        return {
            "d1": "m²/s",
            "mmax": "kg/m³", 
            "c0": "kg/m³",
            "mum": "1/s",
            "Yxs": "[-]",
            "ms": "1/s", 
            "Ks": "kg/m³",
            "eps": "[-]",
            "a": "[-]",
            "b": "[-]",
            "mu": "1/s",
            "Y": "[-]",
            "mu_e": "1/s",
            "Y_e": "[-]",
            "k_1": "kg/m³",
            "k_4": "1/s",
            "M_inf": "kg/m³",
            "E_inf": "kg/m³",
            "alpha": "m³/(kg·s·mol)",
            "beta": "m³/(kg·s·mol)",
            "n": "[-]",
            "tau": "mol/m³",
            "eta1": "1/s",
            "eta2": "1/s",
            "k5": "[-]",
            "gamma_EPS_prod": "1/s",
            "gamma_disp": "1/s",
            "E_threshold": "[-]",
            "E_crit": "[-]",
            "k_deg": "1/s",
            "delta_death": "1/s",
            "D_enzyme": "[-]",
            "M_b": "[-]",
            "eta_disp": "[-]",
            "alpha_lux": "1/s",
            "beta_lux": "1/s",
            "K_lux": "mol/m³",
            "gamma_I": "1/s",
            "K_1": "m³/mol",
            "K_I": "1/s",
            "gamma_Ie": "1/s",
            "epsilon": "mol/m³",
            "R2_TOT": "mol/m³",
            "biofilmPermeability": "m²",
            "biofilmPorosity": "[-]"
        }

    def save_parameters():
        """Write updated parameters back into the file in the container."""
        new_content = []
        result = subprocess.run(
            ["docker", "exec", container_name, "cat", f"{container_path}/dev/clearFoam/base/constant/transportProperties"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.splitlines()

        start_parsing = False
        for line in lines:
            if line.strip().startswith("// * * *"):
                start_parsing = True
                new_content.append(line)
                continue
            if start_parsing:
                match = re.match(r"(\w+)\s+([^;]+);", line.strip())
                if match:
                    key = match.group(1)
                    if key in entries:
                        new_value = entries[key].get().strip()
                        line = f"{key}\t{new_value};"
            new_content.append(line)

        updated_text = "\n".join(new_content)
        proc = subprocess.run(
            ["docker", "exec", "-i", container_name, "bash", "-lc", f"cat > {container_path}/dev/clearFoam/base/constant/transportProperties"],
            input=updated_text, text=True
        )
        if proc.returncode == 0:
            messagebox.showinfo("Success", "Parameters saved successfully!")
            param_window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save parameters.")

    def on_degradation_tag_select(value, gamma_I_entry, degradation_var):
        """Update gamma_I entry when degradation tag is selected."""
        print(f"DEBUG: Selected value: {value}")  # Debug output
        
        degradation_tags = {
            "BBa_K2333401": "0.2768",
            "BBa_K2333402": "0.0173", 
            "BBa_K2333403": "0.1211",
            "BBa_K2333405": "0.0519",
            "BBa_K2333406": "0.0346"
        }
        
        # Extract BioBrick ID from the dropdown value (e.g., "BBa_K2333401 (0.2768)" -> "BBa_K2333401")
        biobrick_id = value.split()[0]
        print(f"DEBUG: Extracted BioBrick ID: {biobrick_id}")  # Debug output
        
        if biobrick_id in degradation_tags:
            print(f"DEBUG: Setting gamma_I to: {degradation_tags[biobrick_id]}")  # Debug output
            gamma_I_entry.delete(0, tk.END)
            gamma_I_entry.insert(0, degradation_tags[biobrick_id])
            gamma_I_entry.update()  # Force UI update
            print(f"DEBUG: Entry field now contains: '{gamma_I_entry.get()}'")  # Verify the update
        else:
            print(f"DEBUG: BioBrick ID {biobrick_id} not found in degradation_tags")
        
        # Reset dropdown to default text
        degradation_var.set("Degradation Tag")

    def on_promoter_tag_select(value, R2_TOT_entry, promoter_var):
        """Update R2_TOT entry when Promoter is selected."""
        print(f"DEBUG: Selected promoter value: {value}")  # Debug output
        
        promoter_tags = {
            "BBa_K823003": "4996.6",
            "BBa_K823000": "499.66",
            "BBa_K823002": "791.9077325",
            "BBa_K823005": "2.809794665"
        }
        
        # Extract BioBrick ID from the dropdown value (e.g., "BBa_K823003 (4000)" -> "BBa_K823003")
        biobrick_id = value.split()[0]
        print(f"DEBUG: Extracted promoter BioBrick ID: {biobrick_id}")  # Debug output
        
        if biobrick_id in promoter_tags:
            print(f"DEBUG: Setting R2_TOT to: {promoter_tags[biobrick_id]}")  # Debug output
            R2_TOT_entry.delete(0, tk.END)
            R2_TOT_entry.insert(0, promoter_tags[biobrick_id])
            R2_TOT_entry.update()  # Force UI update
            print(f"DEBUG: R2_TOT entry field now contains: '{R2_TOT_entry.get()}'")  # Verify the update
        else:
            print(f"DEBUG: Promoter BioBrick ID {biobrick_id} not found in promoter_tags")
        
        # Reset dropdown to default text
        promoter_var.set("Promoter")

    # --- Tkinter window ---
    param_window = tk.Toplevel(root)
    param_window.title("Set Parameters")

    # --- Scrollable Frame ---
    canvas = tk.Canvas(param_window, width=800, height=500)
    scrollbar = tk.Scrollbar(param_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Populate entries ---
    params = load_parameters()
    parameter_units = get_parameter_units()
    entries = {}

    row = 0
    for key, value in params.items():
        # Add units to parameter name if available
        unit_str = parameter_units.get(key, "")
        label_text = f"{key} ({unit_str})" if unit_str else key
        tk.Label(scrollable_frame, text=label_text, width=25, anchor="w").grid(row=row, column=0, padx=5, pady=2)
        entry = tk.Entry(scrollable_frame, width=30)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=5, pady=2)
        entries[key] = entry
        
        # Add special dropdown for gamma_I parameter
        if key == "gamma_I":
            degradation_var = tk.StringVar(scrollable_frame)
            degradation_var.set("Degradation Tag")
            
            degradation_options = [
                "BBa_K2333401 (0.2768)",
                "BBa_K2333402 (0.0173)", 
                "BBa_K2333403 (0.1211)",
                "BBa_K2333405 (0.0519)",
                "BBa_K2333406 (0.0346)"
            ]
            
            # Capture the gamma_I entry field specifically
            gamma_I_entry_field = entry
            
            # Use trace instead of command for more reliable callback
            def on_dropdown_change(*args):
                val = degradation_var.get()
                if val != "Degradation Tag":
                    on_degradation_tag_select(val, gamma_I_entry_field, degradation_var)
            
            degradation_var.trace("w", on_dropdown_change)
            
            degradation_dropdown = tk.OptionMenu(
                scrollable_frame, 
                degradation_var,
                *degradation_options
            )
            degradation_dropdown.config(width=20)
            degradation_dropdown.grid(row=row, column=2, padx=5, pady=2)
        
        # Add special dropdown for R2_TOT parameter
        elif key == "R2_TOT":
            promoter_var = tk.StringVar(scrollable_frame)
            promoter_var.set("Promoter")
            
            promoter_options = [
                "BBa_K823003 4996.6",
                "BBa_K823000 499.66",
                "BBa_K823002 791.9077325",
                "BBa_K823005 2.809794665"
            ]
            
            # Capture the R2_TOT entry field specifically
            R2_TOT_entry_field = entry
            
            # Use trace instead of command for more reliable callback
            def on_promoter_dropdown_change(*args):
                val = promoter_var.get()
                if val != "Promoter":
                    on_promoter_tag_select(val, R2_TOT_entry_field, promoter_var)
            
            promoter_var.trace("w", on_promoter_dropdown_change)
            
            promoter_dropdown = tk.OptionMenu(
                scrollable_frame, 
                promoter_var,
                *promoter_options
            )
            promoter_dropdown.config(width=20)
            promoter_dropdown.grid(row=row, column=2, padx=5, pady=2)
        
        row += 1

    save_btn = tk.Button(scrollable_frame, text="Save", command=save_parameters)
    save_btn.grid(row=row, column=0, columnspan=3, pady=10)

def run_post_processing():
    """Run post-processing commands in the base directory."""
    cmds = [
        "biomass",
        "sessileBiomass",
        "autoinducer",
        "eps",
        "eps_max",
        "biomass_max",
        "enzyme",
        "dispersedBiomass"
    ]

    def worker():
        for cmd in cmds:
            run_command(f"cd {container_path}/dev/clearFoam/base && {cmd}", status_label)

    threading.Thread(target=worker, daemon=True).start()

def view_post_processing(selection_var):
    """Fetch .dat file from container and plot with matplotlib."""
    cmd = selection_var.get()
    if not cmd:
        messagebox.showwarning("No selection", "Please choose a post-processing option.")
        return

    dat_file = f"{container_path}/dev/clearFoam/base/{cmd}.dat"

    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "cat", dat_file],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()

        # Parse columns (assuming whitespace separated numeric data)
        data = [list(map(float, line.split())) for line in lines if line.strip()]
        if not data:
            messagebox.showerror("Error", f"No data found in {cmd}.dat")
            return

        # Convert into columns
        cols = list(zip(*data))

        # Plot
        plt.figure(figsize=(6, 4))
        if len(cols) == 2:
            plt.plot(cols[0], cols[1], marker="o")
            plt.xlabel("X")
            plt.ylabel("Y")
        else:
            for i in range(1, len(cols)):
                plt.plot(cols[0], cols[i], label=f"Col {i}")
            plt.xlabel("X")
            plt.ylabel("Values")
            plt.legend()

        plt.title(f"{cmd}.dat")
        plt.grid(True)
        plt.show()

    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Failed to read {cmd}.dat from container.")

def download_post_processing(selection_var):
    """Allow user to download the selected .dat file from the container to a chosen location."""
    cmd = selection_var.get()
    if not cmd:
        messagebox.showwarning("No selection", "Please choose a post-processing option.")
        return

    dat_file_container = f"{container_path}/dev/clearFoam/base/{cmd}.dat"
    dat_file_host = os.path.join(host_path, "dev", "clearFoam", "base", f"{cmd}.dat")

    # Make sure file exists on host (since it's bind-mounted)
    if not os.path.exists(dat_file_host):
        try:
            # fallback: fetch via docker exec
            result = subprocess.run(
                ["docker", "exec", container_name, "cat", dat_file_container],
                capture_output=True, text=True, check=True
            )
            with open(dat_file_host, "w") as f:
                f.write(result.stdout)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve {cmd}.dat:\n{e}")
            return

    # Ask user where to save
    save_path = filedialog.asksaveasfilename(
        defaultextension=".dat",
        filetypes=[("Data files", "*.dat"), ("All files", "*.*")],
        initialfile=f"{cmd}.dat"
    )
    if save_path:
        try:
            import shutil
            shutil.copy(dat_file_host, save_path)
            messagebox.showinfo("Success", f"Saved {cmd}.dat to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")


# --- Tkinter GUI ---
root = tk.Tk()
root.title("ClearFoam Runner")

# Declare GUI elements that will be referenced by functions
status_label = None
run_button = None

status_label = tk.Label(root, text="Ready", anchor="w", width=80)
status_label.pack(padx=10, pady=10)

prepare_button = tk.Button(root, text="Prepare (allwmake + clean)", command=prepare_build)
prepare_button.pack(padx=10, pady=5)

# Add this button after "Prepare"
set_params_button = tk.Button(root, text="Set Parameters", command=open_set_parameters)
set_params_button.pack(padx=10, pady=5)

run_button = tk.Button(root, text="Run Simulation", command=run_solver, state=tk.DISABLED)
run_button.pack(padx=10, pady=5)

# --- Post-Processing Section ---
post_label = tk.Label(root, text="Post-Processing", font=("Arial", 12, "bold"))
post_label.pack(padx=10, pady=(15, 5))

post_button = tk.Button(root, text="Run Post-Processing", command=run_post_processing)
post_button.pack(padx=10, pady=5)

# Dropdown for viewing results
options = [
    "biomass",
    "sessileBiomass",
    "autoinducer",
    "eps",
    "eps_max",
    "biomass_max",
    "enzyme",
    "dispersedBiomass"
]
selected_option = tk.StringVar(root)
selected_option.set(options[0])  # default selection

dropdown = tk.OptionMenu(root, selected_option, *options)
dropdown.pack(padx=10, pady=5)

view_button = tk.Button(root, text="View", command=lambda: view_post_processing(selected_option))
view_button.pack(padx=10, pady=5)

download_button = tk.Button(root, text="Download", command=lambda: download_post_processing(selected_option))
download_button.pack(padx=10, pady=5)


def quit_app():
    try:
        subprocess.run(["docker", "stop", container_name], check=False)
    except Exception as e:
        print(f"⚠️ Could not stop container: {e}")
    root.destroy()

quit_button = tk.Button(root, text="Quit", command=quit_app)
quit_button.pack(padx=10, pady=10)

# Startup checks
if not check_docker_installed():
    messagebox.showerror(
        "Missing Dependency",
        "Docker is not installed or not available in PATH.\n\n"
        "👉 Please install Docker first:\nhttps://docs.docker.com/get-docker/"
    )
    sys.exit(1)

# Check for OpenFOAM image and ensure container (in background)
status_label.config(text="Checking Docker setup...")
ensure_openfoam_image(status_label)

root.mainloop()
