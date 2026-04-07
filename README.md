# Mini_proj
Minor project
# 🌳 Intergenerational Knowledge Preservation using Agentic AI

---

## 📌 OVERVIEW

This project is an **Agentic AI system** that captures and analyzes intergenerational knowledge (experiences, values, decisions) from elders and compares it with modern lifestyle patterns.

It generates:
- 🧠 Insight (difference + meaning)
- 📊 Graphical analysis
- 🖼️ Visual representation (images)

---

## 🎯 OBJECTIVE

To transform:

> Raw human experience → Structured knowledge → Insight → Visualization

---

## 🧠 CORE IDEA

| Modern AI | This System |
|----------|------------|
Information | Wisdom |
Speed | Depth |
Answers | Reflection |

---

## ⚙️ COMPLETE WORKFLOW


User Input (Text / Speech)
↓
Input Processing Agent
↓
Knowledge Structuring Agent (LLM)
↓
Custom Knowledge Database
↓
Memory Layer (Vector + Graph)
↓
Intergenerational Insight Agent ⭐
↓
Retrieval + Reasoning Agent
↓
LLM Structured Output (JSON)
↓
Visualization Agent
↓
User Response Agent
↓
Final Output (Text + Graph + Image)


---

## 🤖 AGENT ARCHITECTURE

### 1️⃣ Input Processing Agent
**Purpose:** Handle raw input

Tasks:
- Speech → Text (Whisper)
- Language detection
- Translation

---

### 2️⃣ Knowledge Structuring Agent (LLM)
**Purpose:** Convert raw text → structured knowledge

Extract:
- Topic
- Entities
- Values
- Decision patterns
- Emotional insights

---

## ⭐ 3️⃣ Custom Knowledge Database

### Purpose:
Store elder knowledge permanently

---

### Data Format:

```json
{
  "id": 1,
  "topic": "Health",
  "elder_statement": "We used to walk daily",
  "value": "Discipline",
  "decision_pattern": "Preferred physical activity",
  "emotion": "Wisdom",
  "timestamp": "1970s"
}
```

---

### SQLITE SCHEMA:
```sql
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    elder_statement TEXT,
    value TEXT,
    decision_pattern TEXT,
    emotion TEXT,
    timestamp TEXT
);

```
---

### DB Initialization (db_init.py):
```python
import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    elder_statement TEXT,
    value TEXT,
    decision_pattern TEXT,
    emotion TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

```

---


### DB Insert (db_operations.py)
```python
import sqlite3

def insert_knowledge(data):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO knowledge (topic, elder_statement, value, decision_pattern, emotion, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["topic"],
        data["elder_statement"],
        data["value"],
        data["decision_pattern"],
        data["emotion"],
        data["timestamp"]
    ))

    conn.commit()
    conn.close()
```
---
### 🧠 4️⃣ Memory Layer:

Stores data in 3 forms:

Type	Tool
Structured	SQLite
Semantic	FAISS
Relationships	NetworkX

---
### ⭐ 5️⃣ Intergenerational Insight Agent (CORE):
🔥 Purpose:

Convert experience → insight

Responsibilities:
Detect theme
Infer modern lifestyle
Compare past vs present
Generate:
Difference
Value
Impact
Recommendation
💡 THIS IS NOT A MODEL

It is:

A function that calls the LLM with a structured prompt

---
### Insight Agent Code:
```python

import ollama
import json

def generate_insight(user_input):

    prompt = f"""
    Analyze the following elder experience:

    "{user_input}"

    Compare with modern lifestyle.

    Return ONLY valid JSON:

    {{
      "topic": "",
      "analysis": {{
        "difference": "",
        "value": "",
        "impact": "",
        "modern_pattern": "",
        "recommendation": ""
      }},
      "scores": {{
        "past_score": 0,
        "present_score": 0
      }},
      "visualization": {{
        "image_prompt": "",
        "chart_data": {{
          "labels": [],
          "past": [],
          "present": []
        }}
      }}
    }}
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response['message']['content'])
```
---

### 🧠 MODELS USED (FREE & LOCAL)
Component	Model
LLM	Ollama (Llama3)
Speech	Whisper
Embeddings	Sentence Transformers
Vector DB	FAISS
Graph	NetworkX
Image	Stable Diffusion

---
### 🛠️ OLLAMA SETUP:
Install:

https://ollama.com

---
### Run model:
ollama run llama3

---
### Test:
```python
import ollama

print(ollama.chat(
    model="llama3",
    messages=[{"role": "user", "content": "Hello"}]
))
```
---
### 📊 JSON OUTPUT STRUCTURE (CRITICAL):
```json
{
  "topic": "Health",
  "analysis": {
    "difference": "...",
    "value": "...",
    "impact": "...",
    "modern_pattern": "...",
    "recommendation": "..."
  },
  "scores": {
    "past_score": 9,
    "present_score": 4
  },
  "visualization": {
    "image_prompt": "...",
    "chart_data": {
      "labels": ["..."],
      "past": [],
      "present": []
    }
  }
}
```
---
### 📊 GRAPH GENERATION (chart_generator.py):
```python
import matplotlib.pyplot as plt

def generate_chart(data):
    labels = data["labels"]
    past = data["past"]
    present = data["present"]

    x = range(len(labels))

    plt.bar(x, past)
    plt.bar(x, present)

    plt.xticks(x, labels)
    plt.title("Past vs Present")

    plt.savefig("chart.png")
```
---
### 🖼️ IMAGE GENERATION (Concept):

Use:
    Stable Diffusion OR API
```python
   prompt = data["visualization"]["image_prompt"]
```
---
### 🧩 COMPLETE PROJECT STRUCTURE:
intergen_ai_project/

├── app.py
├── config.py
├── requirements.txt

├── database/
│   ├── db.sqlite3
│   ├── db_init.py
│   ├── db_operations.py

├── models/
│   ├── llm/
│   │   └── ollama_client.py

├── agents/
│
│   ├── input_agent/
│   ├── structuring_agent/
│   ├── graph_agent/
│   ├── memory_agent/
│   ├── retrieval_agent/
│   ├── reasoning_agent/
│
│   ├── insight_agent/
│   │   └── insight_generator.py
│
│   ├── visualization_agent/
│   │   ├── chart_generator.py
│   │   └── image_generator.py
│
│   └── response_agent/

├── data/
├── frontend/
├── utils/
└── tests/

---
### 🔁 BACKEND FLOW (Flask):
```python

from flask import Flask, request, jsonify
from agents.insight_agent.insight_generator import generate_insight

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json['text']
    result = generate_insight(text)
    return jsonify(result)

app.run()
```
---
### 🧪 EXAMPLE:

Input:

"We used to repair things instead of buying new ones"

---
### Output:

Insight → sustainability vs consumerism
Graph → comparison
Image → repair vs replace

---
### 🚀 FEATURES:
Agent-based system
Custom database
Hybrid retrieval
Multimodal output
Offline AI

---
### ⚠️ LIMITATIONS
Needs ~10GB storage
Local LLM slower
JSON validation required

---
### 🔮 FUTURE SCOPE:
Voice interface
Timeline comparison
Wisdom scoring
Mobile app

---
### 🎓 CONCLUSION:

This system transforms:

Experience → Intelligence → Insight → Action

---



That will take you from **0 → working project fast** 🚀

---
