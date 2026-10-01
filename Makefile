install:
	python -m pip install -r requirements.txt

run:
	python run_pipeline.py --target 50

test:
	pytest -q

demo:
	streamlit run app.py
