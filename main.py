import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from openai import AsyncOpenAI

app = FastAPI()

# Enable CORS so your local dev servers can securely talk to each other
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Switch client connection to Groq's ultra-fast LPU infrastructure
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

async def generate_analysis_stream(df_summary: str):
    """Generates an executive analysis stream from Groq word-by-word."""
    try:
        stream = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an elite Business Analyst AI. You interpret complex datasets "
                        "and deliver sharp, executive-level structural insights, anomalies, "
                        "and actionable recommendations. Format your output clearly with markdown headings."
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze this business dataset profile and provide high-level insights:\n\n{df_summary}"
                }
            ],
            stream=True,  # This tells Groq to stream responses chunk-by-chunk
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content  # Yield text as soon as it arrives from the network boundary
                
    except Exception as e:
        yield f"\n[Groq LPU Engine Error]: {str(e)}"

@app.post("/api/analyze")
async def analyze_data(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a standard CSV file.")
        
    try:
        # Load and parse the CSV structural shape instantly using Pandas
        df = pd.read_csv(file.file)
        
        # Build a highly compact data layout profile for the LLM context window
        buffer = []
        buffer.append(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
        buffer.append("Data Columns and Types:")
        for col in df.columns:
            buffer.append(f" - {col}: {df[col].dtype} ({df[col].isnull().sum()} missing values)")
        
        buffer.append("\nStatistical Summary Preview:")
        buffer.append(df.describe(include='all').to_string())
        
        df_summary = "\n".join(buffer)
        
        # Return a live asynchronous text stream straight back to the React UI fetch loop
        return StreamingResponse(generate_analysis_stream(df_summary), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pandas processing failed: {str(e)}")