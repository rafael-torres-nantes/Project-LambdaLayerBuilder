import os
import sys
import requests
import zipfile
import subprocess
import shutil
from pathlib import Path

class LambdaLayerBuilder:
    """
    A class to orchestrate the LOCAL creation of AWS Lambda layers
    for Selenium with Chrome.
    """
    def __init__(self, python_version="3.12"):
        """Initializes the builder with the necessary configurations."""
        self.python_version = python_version
        self.requirements = ["selenium", "pandas", "python-dotenv"]

        # URLs for a recent, stable version of Chrome for Testing.
        # The previous version '138.0.7204.49' was invalid.
        chrome_version = "126.0.6478.126"
        self.chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/linux64/chrome-linux64.zip"
        self.chromedriver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/linux64/chromedriver-linux64.zip"
        
        # Define working and output paths
        self.base_dir = Path.cwd()
        self.work_dir = self.base_dir / "layers_temp"      # Folder for downloads and extraction
        self.output_dir = self.base_dir / "layers_output"    # Folder for final zips

        # Paths for working files
        self.chrome_layer_dir = self.work_dir / "chrome-layer"
        self.python_layer_dir = self.work_dir / "python-layer"
        self.chrome_zip_download = self.work_dir / "chrome_pack.zip"
        self.chromedriver_zip_download = self.work_dir / "chromedriver_pack.zip"

        # Paths for final files (in the output folder)
        self.final_chrome_layer_zip = self.output_dir / "selenium-chrome-layer.zip"
        self.final_python_layer_zip = self.output_dir / "selenium-deps-layer.zip"

    def _print_step(self, message):
        """Prints a formatted step message."""
        print(f"\n{'='*60}\n--> {message}\n{'='*60}")

    def _download_file(self, url, destination):
        """Downloads a file from a URL and saves it to the specified destination."""
        self._print_step(f"Downloading: {url}")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(destination, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            print(f"Download of '{destination.name}' completed.")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to download from {url}. Check your connection or the URL. Detail: {e}")
            sys.exit(1)

    def _install_python_dependencies(self):
        """Installs Python dependencies into a target directory."""
        self._print_step(f"Installing Python dependencies for version {self.python_version}")
        # The Python layer path must follow the structure expected by Lambda
        target_dir = self.python_layer_dir / f"python/lib/python{self.python_version}/site-packages"
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            for req in self.requirements:
                print(f"Installing {req}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", req, "--target", str(target_dir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT
                )
            print("Python dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install Python dependencies. Detail: {e.output}")
            sys.exit(1)
            
    def _create_zip_from_folder(self, zip_path: Path, source_dir: Path):
        """Creates a zip file from the contents of a folder."""
        self._print_step(f"Packaging '{source_dir.name}' into '{zip_path.name}'")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    archive_name = file_path.relative_to(source_dir).as_posix()
                    
                    # For binaries, set executable permissions and stream to avoid MemoryError
                    if file in ["chromedriver", "chrome"]:
                        info = zipfile.ZipInfo(archive_name)
                        info.external_attr = 0o100755 << 16  # rwxr-xr-x
                        info.compress_type = zipfile.ZIP_DEFLATED
                        # Open the source file and stream it to the zip file in chunks
                        with open(file_path, 'rb') as src, zf.open(info, 'w') as dest:
                            shutil.copyfileobj(src, dest)
                    else:
                        zf.write(file_path, archive_name)
        print(f"File '{zip_path.name}' created successfully in '{self.output_dir}'.")

    def run(self):
        """Executes the complete local process of creating the layers."""
        self._print_step("Starting .ZIP package creation process")
        
        try:
            # 1. Directory Creation
            self.work_dir.mkdir(exist_ok=True)
            self.output_dir.mkdir(exist_ok=True)
            self.chrome_layer_dir.mkdir(exist_ok=True)
            self.python_layer_dir.mkdir(exist_ok=True)
            print(f"Working ('{self.work_dir.name}') and output ('{self.output_dir.name}') directories are ready.")

            # 2. Download
            self._download_file(self.chrome_url, self.chrome_zip_download)
            self._download_file(self.chromedriver_url, self.chromedriver_zip_download)

            # 3. Selective Extraction for a clean layer structure
            self._print_step("Extracting and structuring Chrome binaries")
            
            # Extract only the 'chrome' binary
            with zipfile.ZipFile(self.chrome_zip_download, 'r') as zf:
                try:
                    binary_path_in_zip = next(s for s in zf.namelist() if s.endswith('/chrome'))
                    target_path = self.chrome_layer_dir / "chrome"
                    with zf.open(binary_path_in_zip) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    print("'chrome' binary extracted.")
                except StopIteration:
                    print("ERROR: Could not find 'chrome' binary in the downloaded zip.")
                    sys.exit(1)

            # Extract only the 'chromedriver' binary
            with zipfile.ZipFile(self.chromedriver_zip_download, 'r') as zf:
                try:
                    binary_path_in_zip = next(s for s in zf.namelist() if s.endswith('/chromedriver'))
                    target_path = self.chrome_layer_dir / "chromedriver"
                    with zf.open(binary_path_in_zip) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    print("'chromedriver' binary extracted.")
                except StopIteration:
                    print("ERROR: Could not find 'chromedriver' binary in the downloaded zip.")
                    sys.exit(1)
            
            # 4. Dependency Installation
            self._install_python_dependencies()
            
            # 5. Layer Packaging
            self._create_zip_from_folder(self.final_chrome_layer_zip, self.chrome_layer_dir)
            self._create_zip_from_folder(self.final_python_layer_zip, self.python_layer_dir)

        finally:
            # 6. Cleanup of the working directory
            self._print_step("Cleaning up temporary files")
            if self.work_dir.exists():
                shutil.rmtree(self.work_dir)
                print(f"Working directory '{self.work_dir.name}' removed.")

        self._print_step("PROCESS FINISHED!")
        print(f"\n.zip files successfully generated in the folder: '{self.output_dir.resolve()}'")
        print(f"- {self.final_chrome_layer_zip.name}")
        print(f"- {self.final_python_layer_zip.name}")