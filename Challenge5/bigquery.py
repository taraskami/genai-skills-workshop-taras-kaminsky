import os
from google.cloud import bigquery
from google.cloud import storage

PROJECT_ID          = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION            = "us-central1"
DATASET_ID          = "ads_dataset"
TABLE_ID            = "faqs"
EMBEDDED_TABLE_ID   = "faqs_embedded"
CONNECTION_ID       = "ads-embedding-conn"

SOURCE_BUCKET   = "labs.roitraining.com"
SOURCE_FILE     = "alaska-dept-of-snow/alaska-dept-of-snow-faqs.csv"

def main():

    client = bigquery.Client(project=PROJECT_ID)

    try:
        # Create dataset
        dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = LOCATION
        
        client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset '{DATASET_ID}' ready")

        # Load FAQ data
        table_id = f"{PROJECT_ID}.{DATASET_ID}.faqs"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("question", "STRING"),
                bigquery.SchemaField("answer", "STRING"),
            ],
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        
        load_job = client.load_table_from_uri(SOURCE_CSV, table_id, job_config=job_config)
        load_job.result()
        
        table = client.get_table(table_id)
        print(f"✓ Loaded {table.num_rows} FAQ records into '{DATASET_ID}.faqs'")

        # Create embedding model
        query = f"""
        CREATE OR REPLACE MODEL `{PROJECT_ID}.{DATASET_ID}.embedding_model`
        REMOTE WITH CONNECTION `{PROJECT_ID}.{LOCATION}.{CONNECTION_ID}`
        OPTIONS (ENDPOINT = 'text-embedding-005')
        """
        
        client.query(query).result()
        print(f"✓ Embedding model 'embedding_model' created")

        # Generate embeddings
        query = f"""
        CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.faqs_embedded` AS
        SELECT 
            question,
            answer,
            content,
            ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
            MODEL `{PROJECT_ID}.{DATASET_ID}.embedding_model`,
            (
                SELECT 
                    question,
                    answer,
                    CONCAT('Question: ', question, ' Answer: ', answer) AS content
                FROM `{PROJECT_ID}.{DATASET_ID}.faqs`
            ),
            STRUCT(TRUE AS flatten_json_output, 'RETRIEVAL_DOCUMENT' AS task_type)
        )
        """
        
        client.query(query).result()
        
        count_query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.faqs_embedded`"
        result = list(client.query(count_query).result())[0]
        print(f"✓ Generated embeddings for {result.cnt} records")
    
    except Exception as e:
        error_msg = str(e).lower()
        print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()

