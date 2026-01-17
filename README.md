# Important Question Detector

## Project Overview
Important Question Detector is a machine learning–based application that analyzes examination question papers to identify frequently asked and important questions. The system processes document inputs, extracts questions using natural language processing techniques, and applies frequency analysis to generate structured outputs.

## Technologies
- Python
- Machine Learning
- Natural Language Processing
- Groq API
- Vue.js
- Vite

## Features
- Automated extraction of questions from PDF documents
- Detection of frequently occurring questions
- Structured output generation in JSON and PDF formats
- Web-based interface for user interaction

## Project Structure
- app.py – Application entry point  
- engine.py – Core processing logic  
- frequency.py – Question frequency analysis  
- my-vue-app – Frontend implementation  

## Execution Steps
```bash
pip install -r requirements.txt
python app.py
