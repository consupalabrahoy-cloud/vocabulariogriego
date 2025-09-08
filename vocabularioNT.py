import streamlit as st
import string
import io
import re
import unicodedata
import pandas as pd # Asegúrate de que pandas está importado

# Función de procesamiento de texto (sin cambios)
def process_text_and_get_unique_words(uploaded_files):
    """
    Processes the uploaded text files, cleans the content, and returns a sorted
    list of unique words.
    """
    all_text = ""
    if not uploaded_files:
        return []

    for file in uploaded_files:
        text_content = file.getvalue().decode("utf-8")
        all_text += text_content + " "

    normalized_text = unicodedata.normalize('NFKD', all_text)
    cleaned_text = "".join(c for c in normalized_text if not unicodedata.combining(c))
    cleaned_text = cleaned_text.lower()
    cleaned_text = re.sub(r'[^α-ω\s]', '', cleaned_text, flags=re.UNICODE)
    words = cleaned_text.split()
    unique_words_set = set(words)
    sorted_unique_words = sorted(list(unique_words_set))
    return sorted_unique_words

# --- Streamlit UI Components ---
st.set_page_config(
    page_title="Westcott-Hort Unique Word Counter",
    page_icon="📖",
    layout="wide"
)

st.title("Generador de Lista de Palabras Únicas (Westcott-Hort)")
st.markdown("Sube los archivos `.txt` de cada libro del Nuevo Testamento griego de Westcott-Hort para generar una lista de todas las **formas de palabras únicas**.")

# File uploader widget
uploaded_files = st.file_uploader(
    "Selecciona los archivos de texto (.txt) del Nuevo Testamento:", 
    type="txt", 
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Procesando los archivos..."):
        unique_words = process_text_and_get_unique_words(uploaded_files)
    
    if unique_words:
        st.success(f"¡Procesamiento completo! Se encontraron {len(unique_words):,} palabras únicas.")
        
        # --- MODIFICACIÓN CLAVE AQUÍ ---
        # 1. Crear un DataFrame de pandas con las columnas deseadas
        #    Inicializamos las columnas 'Transliteración', 'Traducción literal' y 'Análisis Morfológico' vacías
        df = pd.DataFrame({
            'Palabra': unique_words,
            'Transliteración': [''] * len(unique_words),
            'Traducción literal': [''] * len(unique_words),
            'Análisis Morfológico': [''] * len(unique_words)
        })

        # 2. Convertir el DataFrame a formato CSV y codificar
        csv = df.to_csv(index=False).encode('utf-8')
        
        # 3. Botón de descarga con el nuevo DataFrame
        st.download_button(
            label="Descargar lista de palabras en CSV",
            data=csv,
            file_name='westcott_hort_palabras_unicas.csv',
            mime='text/csv',
        )
        
        st.subheader("Lista de Palabras Únicas")
        
        col1, col2 = st.columns(2)
        with col1:
            # Mostrar solo la primera columna en el área de texto si prefieres
            st.text_area(
                "Copiar/Descargar la lista de palabras", 
                value="\n".join(unique_words), 
                height=500
            )

        with col2:
            st.write("Visualización de la lista:")
            # Se muestra el DataFrame completo con todas las columnas
            st.dataframe(df, width=600)

    else:
        st.warning("No se encontraron palabras en los archivos subidos. Por favor, asegúrate de que los archivos contengan texto.")
