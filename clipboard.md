cd /home/chaitanya/translation-model/Indic-Trans-2-Setup

source /home/chaitanya/translation-model/trans-env/bin/activate && python -m pytest tests/test_health.py
       tests/test_pdf.py tests/test_concurrency.py -v -s 2>&1