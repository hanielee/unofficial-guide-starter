"""
Web interface for UC Berkeley Dining Guide RAG system using Gradio.
Provides a user-friendly interface for querying the dining guide.
"""

import gradio as gr
from generation import answer_question
from embedding_and_retrieval import main as setup_embedding_retrieval
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Global state
_state = {}


def initialize_system():
    """Initialize the RAG system on first load."""
    global _state

    if _state:
        return  # Already initialized

    print("Initializing RAG system...")

    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in .env file. "
            "Get a free key at https://console.groq.com"
        )

    # Setup models
    model, collection = setup_embedding_retrieval()
    client = Groq(api_key=api_key)

    _state = {
        "model": model,
        "collection": collection,
        "client": client,
    }

    print("✓ RAG system ready")


def query_dining_guide(question, retrieval_count):
    """
    Query the dining guide with a question.

    Args:
        question: User's question
        retrieval_count: Number of chunks to retrieve (k)

    Returns:
        Tuple of (answer, sources_html)
    """

    if not question.strip():
        return "", "Please enter a question."

    try:
        initialize_system()

        # Temporarily override top_k
        import generation
        original_top_k = generation.TOP_K
        generation.TOP_K = retrieval_count

        result = answer_question(
            question,
            _state["model"],
            _state["collection"],
            _state["client"]
        )

        generation.TOP_K = original_top_k

        # Format sources
        sources_html = "<div style='margin-top: 20px;'><h3>📍 Sources</h3>"
        seen_sources = set()

        for i, chunk in enumerate(result["retrieved_chunks"][:5], 1):
            source_key = (chunk['source'], chunk['chunk_index'])
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                distance = chunk['distance']
                distance_color = (
                    "green" if distance < 0.35 else
                    "orange" if distance < 0.5 else
                    "red"
                )
                sources_html += f"""
                <div style='margin: 10px 0; padding: 10px; background: #f5f5f5; border-left: 4px solid {distance_color};'>
                    <strong>{chunk['source']}</strong> (Chunk {chunk['chunk_index']})<br>
                    <small>Distance: {distance:.3f}</small><br>
                    <em>{chunk['content'][:150]}...</em>
                </div>
                """

        sources_html += "</div>"

        return result["answer"], sources_html

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if "GROQ_API_KEY" in str(e):
            error_msg += "\n\nPlease set GROQ_API_KEY in .env file"
        return error_msg, ""


def create_interface():
    """Create a modern, centered Gradio interface."""

    # Custom CSS with Berkeley Blue & Gold
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    body {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
        min-height: 100vh;
    }

    .gradio-container {
        max-width: 900px !important;
        margin: 0 auto !important;
        padding: 40px 20px !important;
    }

    .header-section {
        text-align: center;
        margin-bottom: 40px;
        background: linear-gradient(135deg, #003262 0%, #004b87 100%);
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 50, 98, 0.2);
    }

    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FDB827;
        margin: 0;
        padding: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .subtitle {
        font-size: 1rem;
        color: #003262;
        margin-top: 10px;
        font-weight: 400;
    }

    .search-box {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 50, 98, 0.08);
        margin-bottom: 30px;
        border: 2px solid #FDB827;
    }

    #search-input textarea {
        font-size: 1rem !important;
        border-radius: 8px !important;
        border: 2px solid #003262 !important;
        padding: 12px !important;
    }

    #search-input textarea:focus {
        border-color: #FDB827 !important;
        box-shadow: 0 0 0 3px rgba(253, 184, 39, 0.2) !important;
    }

    .search-btn {
        background: linear-gradient(135deg, #003262, #FDB827) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 32px !important;
        border-radius: 8px !important;
        margin-top: 15px;
    }

    .search-btn:hover {
        box-shadow: 0 10px 25px rgba(0, 50, 98, 0.3) !important;
    }

    .answer-section {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 50, 98, 0.08);
        margin-bottom: 20px;
        border-left: 5px solid #003262;
    }

    .answer-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #003262;
        margin-bottom: 15px;
    }

    .sources-section {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f0f8 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #FDB827;
    }

    .examples-section {
        margin-top: 40px;
        text-align: center;
    }

    .example-label {
        font-size: 0.9rem;
        color: #003262;
        margin-bottom: 15px;
        font-weight: 600;
    }

    .info-section {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f0f8 100%);
        border-radius: 12px;
        padding: 25px;
        margin-top: 30px;
        box-shadow: 0 5px 20px rgba(0, 50, 98, 0.1);
        color: #003262;
    }

    .info-section h3 {
        color: #003262;
        margin-top: 0;
        font-size: 1rem;
    }

    .info-section p {
        margin: 8px 0;
        color: #003262;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Slider styling */
    .gradio-slider {
        background: #f0f4f8 !important;
    }

    .gradio-slider input {
        accent-color: #003262 !important;
    }

    /* Button styling */
    .gradio-button {
        background: #003262 !important;
    }

    .gradio-button:hover {
        background: #004b87 !important;
    }
    """

    with gr.Blocks(
        title="UC Berkeley Dining Guide",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as demo:
        # Header
        with gr.Group(elem_classes="header-section"):
            gr.Markdown("# 🍽️ UC Berkeley Dining Guide", elem_classes="title")
            gr.Markdown("*Unofficial AI guide to campus food, restaurants, and dining resources*", elem_classes="subtitle")

        # Main search section
        with gr.Group(elem_classes="search-box"):
            question = gr.Textbox(
                label="Ask about Berkeley dining",
                placeholder="e.g., Where can I find affordable food under $10?",
                lines=4,
                elem_id="search-input",
                show_label=False
            )

            with gr.Row():
                with gr.Column(scale=3):
                    retrieval_slider = gr.Slider(
                        minimum=3,
                        maximum=20,
                        value=12,
                        step=1,
                        label="📊 Chunks to retrieve",
                        info="More context = better answers but slower"
                    )

                with gr.Column(scale=1):
                    submit_btn = gr.Button(
                        "🔍 Search",
                        variant="primary",
                        scale=1,
                        elem_classes="search-btn"
                    )

        # Results section
        with gr.Group(elem_classes="answer-section"):
            answer_output = gr.Markdown(
                label="Answer",
                elem_classes="answer-label"
            )

        sources_output = gr.HTML(
            label="📍 Sources",
            elem_classes="sources-section"
        )

        # Examples
        with gr.Group(elem_classes="examples-section"):
            gr.Markdown("### Try these questions:", elem_classes="example-label")
            gr.Examples(
                examples=[
                    ["What are the main dining commons at UC Berkeley?"],
                    ["Where can I find affordable food under $10?"],
                    ["What resources are available for students with food insecurity?"],
                    ["Which restaurants are recommended for a date night?"],
                    ["How do I get to the dining commons from Sproul Plaza?"],
                ],
                inputs=question,
                label=""
            )

        # Info section
        with gr.Group(elem_classes="info-section"):
            gr.Markdown("""
            ### ℹ️ About This System

            - **LLM**: llama-3.3-70b-versatile (Groq)
            - **Embeddings**: all-MiniLM-L6-v2 (sentence-transformers)
            - **Vector Store**: ChromaDB
            """)

        # Connect interactions
        submit_btn.click(
            fn=query_dining_guide,
            inputs=[question, retrieval_slider],
            outputs=[answer_output, sources_output]
        )

        question.submit(
            fn=query_dining_guide,
            inputs=[question, retrieval_slider],
            outputs=[answer_output, sources_output]
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=False)
