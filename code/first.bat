@echo off
setlocal

:: Navigate to project directory
cd M:\ML\Finance\BI\code

:: Check if conda environment exists and create if not
conda info --envs | findstr /C:"my_streamlit_env" 1>nul 2>&1 || conda create --name my_streamlit_env python=3.8 -y

:: Activate conda environment
call conda activate my_streamlit_env

:: Check if Poetry is installed and install if not
pip show poetry || pip install poetry

:: Install dependencies using Poetry
call poetry install

:: Run the Streamlit app
call streamlit run your_streamlit_app.py

endlocal
