# Alaska Department of Snow - Chatbot Architecture

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph Users["👥 Users"]
        Web["🌐 Web Browser"]
        Mobile["📱 Mobile Device"]
    end

    subgraph CloudRun["☁️ Cloud Run"]
        Frontend["Frontend<br/>(HTML/JS)"]
        API["Flask API<br/>(/api/chat)"]
        
        subgraph Security["🔒 Security Layer"]
            InputVal["Input Validation<br/>& Prompt Filtering"]
            OutputVal["Response Validation"]
        end
    end

    subgraph GCP["Google Cloud Platform"]
        subgraph BigQuery["📊 BigQuery"]
            FAQTable["faqs table<br/>(questions, answers)"]
            EmbedTable["faqs_embedded<br/>(with vectors)"]
            EmbedModel["embedding_model<br/>(text-embedding-005)"]
        end
        
        subgraph VertexAI["🤖 Vertex AI"]
            Gemini["Gemini 2.0 Flash<br/>+ Safety Settings"]
        end
        
        subgraph Logging["📝 Cloud Logging"]
            Logs["All Prompts<br/>& Responses"]
        end
    end

    subgraph DataSource["📁 Data Source"]
        GCS["GCS Bucket<br/>gs://labs.roitraining.com<br/>/alaska-dept-of-snow"]
    end

    Web --> Frontend
    Mobile --> Frontend
    Frontend --> API
    API --> InputVal
    InputVal --> |"Valid Query"| EmbedModel
    EmbedModel --> |"Query Embedding"| EmbedTable
    EmbedTable --> |"VECTOR_SEARCH<br/>Top K Results"| API
    API --> |"Context + Query"| Gemini
    Gemini --> |"Response"| OutputVal
    OutputVal --> |"Safe Response"| API
    API --> Logs
    API --> Frontend

    GCS --> |"Load Data"| FAQTable
    FAQTable --> |"Generate Embeddings"| EmbedTable
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Server
    participant V as Input Validator
    participant B as BigQuery
    participant G as Gemini
    participant O as Output Validator
    participant L as Cloud Logging

    U->>F: Enter Question
    F->>A: POST /api/chat
    A->>V: Validate Input
    
    alt Invalid Input (injection attempt)
        V-->>A: Rejected
        A->>L: Log (filtered=true)
        A-->>F: Error Message
    else Valid Input
        V-->>A: Approved
        A->>B: Generate Query Embedding
        B-->>A: Embedding Vector
        A->>B: VECTOR_SEARCH (top_k=3)
        B-->>A: Relevant FAQs
        A->>G: Context + Question
        G-->>A: Generated Response
        A->>O: Validate Response
        O-->>A: Safe Response
        A->>L: Log Interaction
        A-->>F: Response JSON
    end
    
    F-->>U: Display Answer
```

## Component Details

### 1. Frontend (Cloud Run)
- Simple HTML/CSS/JavaScript chat interface
- Hosted within the same Cloud Run service
- No external dependencies

### 2. Backend API (Flask)
- `/` - Serves chat interface
- `/api/chat` - Main chat endpoint
- `/api/health` - Health check

### 3. Security Features
| Feature | Implementation |
|---------|----------------|
| Input Validation | Length limits, empty check |
| Prompt Injection Detection | Pattern matching for known attacks |
| Safety Settings | Gemini's built-in harm categories |
| Response Validation | Filter leaked instructions |
| Logging | All interactions logged to Cloud Logging |

### 4. RAG System (BigQuery)
- **Data**: FAQ CSV loaded from GCS
- **Embeddings**: text-embedding-005 via BigQuery ML
- **Search**: VECTOR_SEARCH function for semantic matching
- **Top-K**: Returns 3 most relevant FAQ entries

### 5. Generation (Vertex AI)
- **Model**: Gemini 2.0 Flash
- **System Instructions**: ADS-specific behavior
- **Safety Settings**: Block medium and above for all harm categories

### 6. Logging (Cloud Logging)
All interactions logged with:
- Timestamp
- User query
- Response
- Context used
- Filter status

## Cost Considerations

| Service | Pricing Model | Est. Monthly Cost |
|---------|---------------|-------------------|
| Cloud Run | Per request + CPU/Memory | ~$5-20 |
| BigQuery | Storage + Query processing | ~$1-5 |
| Vertex AI (Gemini) | Per 1M tokens | ~$5-50 |
| Cloud Logging | Per GB ingested | ~$0.50 |

**Total Estimated**: $15-100/month depending on usage

## Security & Privacy

1. **Data Residency**: All data stays in GCP US region
2. **No PII Storage**: System doesn't collect/store personal data
3. **Audit Trail**: Complete logging of all interactions
4. **Input Sanitization**: Prevents prompt injection attacks
5. **Access Control**: IAM-based access to GCP resources