
import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Initialize Groq chat model
chat_model = init_chat_model(
    "openai/gpt-oss-20b",
    model_provider="groq",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert information extraction assistant.

        Your task is to analyze the provided paragraph and
        extract useful information accurately.

        Rules:
        1. Extract only information explicitly mentioned.
        2. Never invent or assume missing information.
        3. Use null for missing information.
        4. Extract information about multiple people separately.
        5. Do not infer gender from names.
        6. Extract caste and religion only if explicitly stated.
        7. Do not infer sensitive attributes.
        8. Provide a short and clear summary.
        9. Return valid structured JSON only.

        Extract the following:

        - Names
        - Age
        - Gender
        - Caste/community (explicitly stated only)
        - Nationality
        - Religion (explicitly stated only)
        - Email
        - Phone number
        - Location
        - Education
        - College/university
        - Job title
        - Company
        - Work experience
        - Skills
        - Hobbies and interests
        - Achievements
        - Important dates
        - Key facts
        - Summary
        """
    ),
    (
        "human",
        "Analyze this paragraph:\n\n{paragraph}"
    )
])

# Get paragraph from user
para = input("Enter the paragraph: ")

# Generate prompt
final_prompt = prompt.invoke({
    "paragraph": para
})

# Get response
response = chat_model.invoke(final_prompt)

# Display result
print("\n========== EXTRACTED INFORMATION ==========\n")
print(response.content)
