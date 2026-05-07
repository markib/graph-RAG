import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


# 🔷 Prompt Template (IMPORTANT)
SYSTEM_PROMPT = """
You are an information extraction system.

Extract structured knowledge from text.

Return ONLY valid JSON in this format:

{
  "entities": [
    {"type": "User", "name": "John"},
    {"type": "Product", "name": "Laptop"}
  ],
  "relationships": [
    {
      "source": "John",
      "target": "Laptop",
      "type": "BOUGHT",
      "properties": {"date": "2024-01"}
    }
  ]
}

Rules:
- Use consistent entity types: User, Product, Store, Category
- Use UPPERCASE relationship types: BOUGHT, SOLD_BY, BELONGS_TO
- Do not add explanations
- Do not return text outside JSON
"""


# 🔷 Groq Call using SDK
async def call_groq(prompt: str) -> Dict[str, Any]:
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=2048,
    )

    content = response.choices[0].message.content
    return safe_json_parse(content)


# 🔷 Safe JSON Parser (VERY IMPORTANT)
def safe_json_parse(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to fix common issues
        text = text.strip()

        # Remove markdown if present
        if text.startswith("```"):
            text = text.split("```")[1]

        try:
            return json.loads(text)
        except Exception as e:
            print("❌ JSON parsing failed:", e)
            print("Raw output:", text)
            return {"entities": [], "relationships": []}


# 🔷 Extract from text
async def extract_from_text(text: str):
    return await call_groq(text)


# 🔷 Read file
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# 🔷 Main Pipeline
async def process_file(file_path: str):
    print(f"\n📄 Processing: {file_path}")

    text = read_file(file_path)

    result = await extract_from_text(text)

    print("\n🔷 Entities:")
    for e in result.get("entities", []):
        print(f"  - {e}")

    print("\n🔷 Relationships:")
    for r in result.get("relationships", []):
        print(f"  - {r}")

    return result


# 🔷 Batch Processing
async def process_files(files: List[str]):
    all_data = {
        "entities": [],
        "relationships": []
    }

    for file in files:
        result = await process_file(file)

        all_data["entities"].extend(result.get("entities", []))
        all_data["relationships"].extend(result.get("relationships", []))

    return all_data


# 🔷 Run Script
if __name__ == "__main__":
    files = ["doc1.txt", "doc2.txt"]

    data = asyncio.run(process_files(files))

    # Save output
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\n✅ Extraction complete → output.json")