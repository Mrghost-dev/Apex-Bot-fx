
@echo off
title Apex Market Signal Bot
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
streamlit run app.py
pause
