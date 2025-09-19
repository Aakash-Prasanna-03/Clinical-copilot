# Clinical Copilot - Gemini Integration Setup

This guide will help you set up the Gemini AI integration for the Clinical Copilot to provide intelligent, context-aware responses with citations from your patient dataset.

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Gemini API Key**: Obtain a Gemini API key from Google AI Studio
3. **Patient Data**: Have patient data indexed in the vector database

## Setup Steps

### 1. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Set Up Gemini API Key

Create a `.env` file in the `src` directory with your Gemini API key:

```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

Or set it as an environment variable:

```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here

# macOS/Linux
export GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Prepare Patient Data

Ensure you have patient data indexed:

1. Upload patient data via the `/api/upload-json` endpoint
2. Or run the indexing process:
   ```bash
   python embed.py
   ```

### 4. Start the Server

```bash
python app.py
```

The server should display:
- ✅ Gemini AI available: True
- ✅ Search functions available: True
- ✅ Vector search available: True

## API Usage

### Copilot Endpoint

**POST** `/api/copilot`

```json
{
  "query": "What are the patient's current conditions?",
  "n_results": 5,
  "filter_type": "conditions"
}
```

**Response:**

```json
{
  "query": "What are the patient's current conditions?",
  "answer": "Based on the patient data, the patient has the following conditions...",
  "citations": [
    {
      "id": 1,
      "text": "Condition: Diabetes Type 2",
      "type": "conditions",
      "relevance": 0.95,
      "source": "Patient Data - Conditions"
    }
  ],
  "context_used": 3,
  "confidence": 0.87,
  "response_metadata": {
    "model": "gemini-pro",
    "temperature": 0.3,
    "context_sources": ["conditions", "medications"]
  }
}
```

### Query Parameters

- `query` (required): The clinical question or query
- `n_results` (optional): Number of context documents to retrieve (default: 5)
- `filter_type` (optional): Filter context by data type (conditions, medications, etc.)

## Testing

Run the test script to verify everything is working:

```bash
python test_copilot.py
```

This will test:
- Environment setup
- Basic endpoints
- Copilot functionality
- Response format

## Features

### Context-Aware Responses
- Retrieves relevant patient data using vector similarity search
- Provides context to Gemini AI for accurate, personalized responses
- Maintains patient data privacy by processing locally

### Citations and Sources
- Every response includes citations from the patient dataset
- Shows relevance scores for each source
- Identifies the type of data (conditions, medications, labs, etc.)

### Fallback Modes
- Works with or without vector database
- Falls back to simple patient data if vector search unavailable
- Graceful error handling

### Medical Context
- Configured for clinical/medical domain
- Lower temperature for consistent medical advice
- Appropriate disclaimers and limitations

## Example Queries

```json
{"query": "What medications is the patient taking?"}
{"query": "Are there any drug interactions I should be aware of?"}
{"query": "What do the latest lab results indicate?"}
{"query": "Based on the patient's allergies, what should we avoid?"}
{"query": "What clinical considerations should I note for this patient?"}
```

## Troubleshooting

### Common Issues

1. **"Gemini AI integration not available"**
   - Check your GEMINI_API_KEY environment variable
   - Ensure the google-generativeai package is installed

2. **"Vector search not available"**
   - Install chromadb and sentence-transformers
   - Run the embedding process: `python embed.py`

3. **No context in responses**
   - Ensure patient data is indexed
   - Check that the vector database directory exists
   - Verify data was uploaded and processed

4. **Empty responses**
   - Check your Gemini API key is valid
   - Ensure you have API quota remaining
   - Check network connectivity

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export DEBUG=1
```

This will show detailed logs of:
- Context retrieval
- Gemini API calls
- Response processing

## Configuration

### Gemini Model Settings

The integration uses these settings:
- Model: `gemini-pro`
- Temperature: `0.3` (lower for medical consistency)
- Max tokens: `2048`
- Top-p: `0.8`

You can modify these in `gemini_integration.py` if needed.

### Response Confidence

Confidence scores are calculated based on:
- Average relevance of context documents (70%)
- Number of context documents available (30%)
- Ranges from 0.0 to 1.0

## Security Notes

- API keys should never be committed to version control
- Use environment variables or secure key management
- Patient data remains on your local system
- Gemini API calls include context but not full patient records

## Next Steps

1. Customize prompts for your specific clinical workflow
2. Add specialized query types (drug interactions, dosage calculations, etc.)
3. Integrate with your existing EHR systems
4. Add user authentication and audit logging