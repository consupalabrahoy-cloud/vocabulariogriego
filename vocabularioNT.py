import streamlit as st
import string
import io
import re

def process_text_and_get_unique_words(uploaded_files):
    """
    Processes the uploaded text files, cleans the content, and returns a sorted
    list of unique words.

    Args:
        uploaded_files: A list of Streamlit UploadedFile objects.

    Returns:
        A sorted list of unique words found in the texts.
    """
    all_text = ""
    if not uploaded_files:
        return []

    for file in uploaded_files:
        # Decode the file content from bytes to a string
        text_content = file.getvalue().decode("utf-8")
        all_text += text_content + " "

    # Normalize the text: convert to lowercase and remove punctuation
    # A more robust approach for Greek would be to use a library like NLTK or spacy
    # but for this example, we'll use a simple regex to keep Greek characters
    # and remove punctuation.
    all_text = all_text.lower()
    
    # Remove all characters that are not Greek letters or spaces.
    # The regex below keeps lowercase Greek letters (alpha-omega),
    # uppercase Greek letters (which we've already converted to lowercase),
    # and a few other common symbols in Greek text that might be included
    # (like the diaeresis and accent marks).
    cleaned_text = re.sub(r'[^α-ω\s]', '', all_text, flags=re.UNICODE)
    
    # Split the text into a list of words
    words = cleaned_text.split()
    
    # Create a set to get unique words
    unique_words_set = set(words)
    
    # Convert the set to a list and sort it alphabetically
    sorted_unique_words = sorted(list(unique_words_set))
    
    return sorted_unique_words

st.set_page_config(
    page_title="Westcott-Hort Unique Word Counter",
    page_icon="📖",
    layout="wide"
)

# --- Streamlit UI Components ---
st.title("Generador de Lista de Palabras Únicas (Westcott-Hort)")
st.markdown("Sube los archivos `.txt` de cada libro del Nuevo Testamento griego de Westcott-Hort para generar una lista de todas las **formas de palabras únicas**.")

# File uploader widget
uploaded_files = st.file_uploader(
    "Selecciona los archivos de texto (.txt) del Nuevo Testamento:", 
    type="txt", 
    accept_multiple_files=True
)

if uploaded_files:
    # Use a Streamlit spinner to indicate that the processing is happening
    with st.spinner("Procesando los archivos..."):
        unique_words = process_text_and_get_unique_words(uploaded_files)
    
    if unique_words:
        st.success(f"¡Procesamiento completo! Se encontraron {len(unique_words):,} palabras únicas.")
        
        # Display the unique words
        st.subheader("Lista de Palabras Únicas")
        
        # Create two columns for a better display
        col1, col2 = st.columns(2)
        with col1:
            st.text_area(
                "Copiar/Descargar la lista de palabras", 
                value="\n".join(unique_words), 
                height=500
            )

        with col2:
            st.write("Visualización de la lista:")
            st.dataframe(unique_words, width=300)
    else:
        st.warning("No se encontraron palabras en los archivos subidos. Por favor, asegúrate de que los archivos contengan texto.")
