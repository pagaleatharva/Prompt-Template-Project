
import os
import json
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Movie Information Extractor",
    page_icon="🎬",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 850px;
    }

    .main-title {
        text-align: center;
        font-size: 34px;
        font-weight: 750;
        color: #172554;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 15px;
        margin-bottom: 30px;
    }

    .result-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }

    .result-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .result-value {
        color: #172554;
        font-size: 17px;
        font-weight: 600;
        margin-top: 5px;
    }

    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Movie schema
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
@st.cache_resource
def load_model():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

    return init_chat_model(
        "openai/gpt-oss-20b",
        model_provider="groq",
        api_key=api_key,
        temperature=0
    )


# Prompt template
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


# UI Header
st.markdown(
    '<div class="main-title">🎬 Movie Information Extractor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Extract structured movie details using LangChain and Groq AI</div>',
    unsafe_allow_html=True
)

st.divider()

# Input section
st.markdown("### Enter Movie Paragraph")

paragraph = st.text_area(
    "Paste your movie description below:",
    height=180,
    placeholder="Example: The movie 3 Idiots was released in 2009 and directed by Rajkumar Hirani..."
)

# Extract button
if st.button("Extract Movie Information"):

    if not paragraph.strip():
        st.warning("Please enter a movie paragraph first.")

    else:
        try:
            with st.spinner("Extracting movie information..."):

                chat_model = load_model()

                final_prompt = prompt.invoke({
                    "paragraph": paragraph,
                    "format_instructions": parser.get_format_instructions()
                })

                response = chat_model.invoke(final_prompt)

                movie_data = parser.parse(response.content)

            st.success("Movie information extracted successfully!")

            st.divider()

            # Results
            st.markdown("### Extracted Movie Details")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">MOVIE TITLE</div>
                        <div class="result-value">{movie_data.title}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">DIRECTOR</div>
                        <div class="result-value">{movie_data.director or "Not available"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">GENRE</div>
                        <div class="result-value">{", ".join(movie_data.genre) or "Not available"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">RELEASE YEAR</div>
                        <div class="result-value">{movie_data.year if movie_data.year is not None else "Not available"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">IMDB RATING</div>
                        <div class="result-value">{movie_data.rating if movie_data.rating is not None else "Not available"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">CAST</div>
                        <div class="result-value">{", ".join(movie_data.cast) or "Not available"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("#### Movie Summary")

            st.write(movie_data.summary or "Not available")

            st.markdown("#### Structured JSON Output")

            st.json(movie_data.model_dump())

        except Exception as e:
            st.error(f"Error extracting movie information: {e}")
