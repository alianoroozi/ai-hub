# Spend Assistant

This project is a simple Spend Assistant that lets you chat with your organizational spend data.

## Dataset Overview

The dataset includes information about:
- Department
- Item
- Vendor
- Delivery Date
- Number of Items
- Price
- Total Cost
- Ordered By
- Approved By

## What the Assistant Can Do

- Answer natural language questions about the spend data
- Search and retrieve relevant entries from the dataset
- Use an LLM API to generate accurate and insightful responses
- Combine structured data with LLM-generated insights to provide meaningful answers

## Available Solutions

This project includes five different implementations of the Spend Assistant:

- `openai.ipynb` – Uses OpenAI API directly
- `anthropic.ipynb` – Uses Anthropic's Claude API
- `langchain.ipynb` – Uses LangChain agents to interact with the data
- `llama_index.ipynb` – Uses LlamaIndex as a query engine
- `pandas_ai.ipynb` – Uses the pandas-ai package with a text-to-SQL approach
