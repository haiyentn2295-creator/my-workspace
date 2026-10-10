import runpy
import sys

# Entrypoint cho Streamlit Community Cloud
# Tự động điều hướng và thực thi app_lead_scoring.py
runpy.run_path("app_lead_scoring.py", run_name="__main__")
