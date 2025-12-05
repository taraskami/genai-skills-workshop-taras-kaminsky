Commands to execute:
### Deployment

```bash
# 1. Set project
export PROJECT_ID=$(gcloud config get-value project)

# 2. Enable APIs
gcloud services enable aiplatform.googleapis.com bigquery.googleapis.com \
    bigqueryconnection.googleapis.com cloudbuild.googleapis.com \
    run.googleapis.com logging.googleapis.com

# 3. Set up BigQuery (prints commands to run)
python setup_bigquery.py

# 4. Deploy to Cloud Run
gcloud run deploy ads-chatbot \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
```

### Run Unit Tests
```bash
pip install pytest
pytest test_agent.py -v
```

### Run Evaluation
```bash
gcloud auth application-default login
python evaluation.py
```