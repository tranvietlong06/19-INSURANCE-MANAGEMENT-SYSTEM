@echo off
echo Installing dependencies...
pip install mysql-connector-python streamlit pandas
echo Dependencies installed.
cd "19-INSURANCE-MANAGEMENT-SYSTEM-main"
python -m streamlit run app.py
pause