import runpy
from pathlib import Path

target_file = Path(__file__).parent / "streamlit_app.py"
runpy.run_path(str(target_file), run_name="__main__")
