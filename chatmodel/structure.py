
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

# Define movie schema
class Movie(BaseModel):
    title: str
    year: Optional[int] = None
    genre: List[str] = Field(default_factory=list)
    director: Optional[str] = None
    cast: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    summary: Optional[str] = None


# Initialize parser
parser = PydanticOutputParser(pydantic_object=Movie)

# Initialize Groq model
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
        You are an expert movie information extraction assistant.

        Extract movie information from the paragraph.

        Rules:
        1. Extract only explicitly available information.
        2. Never invent information.
        3. Use null for missing optional fields.
        4. Use an empty list if genre or cast is not mentioned.
        5. Return output according to the provided schema.
        6. Return only valid structured information.

        {format_instructions}
        """
    ),
    (
        "human",
        "Extract movie information from this paragraph:\n\n{paragraph}"
    )
])

# Get paragraph
para = input("Enter the movie paragraph: ")

try:
    # Generate prompt
    final_prompt = prompt.invoke({
        "paragraph": para,
        "format_instructions": parser.get_format_instructions()
    })

    # Get model response
    response = chat_model.invoke(final_prompt)

    print("\nRAW RESPONSE:")
    print(response.content)

    # Parse response
    movie_data = parser.parse(response.content)

    print("\n========== EXTRACTED MOVIE INFORMATION ==========\n")
    print(movie_data.model_dump_json(indent=4))

except Exception as e:
    print("\nError:", e)
