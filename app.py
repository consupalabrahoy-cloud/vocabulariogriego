import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN ---
# Reemplaza con la URL RAW de tu archivo output_diccionario.json en GitHub
GITHUB_JSON_URL = "https://raw.githubusercontent.com/consupalabrahoy-cloud/vocabulariogriego/main/output_diccionario.json"
# ---------------------

def load_data():
    """Carga los datos del JSON de GitHub y los almacena en el estado de la sesión."""
    try:
        response = requests.get(GITHUB_JSON_URL)
        if response.status_code == 200:
            st.session_state['dictionary'] = response.json()
            st.session_state['is_data_loaded'] = True
        else:
            st.error(f"Error al cargar el JSON desde GitHub. Código: {response.status_code}")
            st.session_state['dictionary'] = []
            st.session_state['is_data_loaded'] = False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.session_state['dictionary'] = []
        st.session_state['is_data_loaded'] = False

def find_next_pending_index():
    """Busca el índice de la primera palabra con estado 'pendiente'."""
    if 'dictionary' in st.session_state:
        for i, entry in enumerate(st.session_state['dictionary']):
            if entry.get("estado") == "pendiente":
                return i
    return -1

def initialize_session_state():
    """Inicializa variables de estado si no existen."""
    if 'is_data_loaded' not in st.session_state:
        st.session_state['is_data_loaded'] = False
        load_data()
    
    if 'current_index' not in st.session_state:
        st.session_state['current_index'] = find_next_pending_index()

def save_and_advance():
    """
    Simula el proceso de guardar, actualizar el estado y avanzar a la siguiente palabra.
    
    ¡IMPORTANTE!: En una aplicación real, esta función debe escribir en Google Sheets, 
    una base de datos o un servicio externo.
    """
    current_index = st.session_state['current_index']
    
    if current_index == -1:
        st.toast("Ya no hay más palabras pendientes para guardar.", icon="✅")
        return

    # 1. Obtener la información de la caja de texto
    new_info = st.session_state.editor_box

    # 2. Modificar el JSON en el estado de la sesión (Simulación)
    word_entry = st.session_state['dictionary'][current_index]
    
    # 3. Guardar en el servicio externo (Esta es la parte que debes integrar con Google Sheets)
    # Ejemplo de cómo se vería la línea si usaras un servicio real:
    # database_client.update_entry(word_entry['palabra'], new_info, "completado") 
    
    # --- SIMULACIÓN DE LA ESCRITURA ---
    # En el entorno real, la base de datos se actualizaría aquí.
    # Como NO estamos escribiendo en GitHub, solo actualizamos el estado interno.
    word_entry["información"] = new_info
    word_entry["estado"] = "completado"
    # ----------------------------------

    # 4. Limpiar el campo de texto
    st.session_state.editor_box = ""
    
    # 5. Buscar la siguiente palabra pendiente
    next_index = find_next_pending_index()
    st.session_state['current_index'] = next_index

    st.toast("✅ Datos guardados y estado cambiado a 'completado'.", icon="✅")
    time.sleep(0.5) # Pequeña pausa para asegurar que el toast se muestre
    st.rerun() # Volver a ejecutar la aplicación para mostrar la siguiente palabra

def edit_existing_word(word_to_edit):
    """Carga una palabra completada en la caja de edición."""
    st.session_state['current_index'] = word_to_edit
    st.session_state.editor_box = st.session_state['dictionary'][word_to_edit]['información']
    st.toast(f"Cargando palabra {st.session_state['dictionary'][word_to_edit]['palabra']} para edición.", icon="✏️")
    st.rerun()

# --- INTERFAZ STREAMLIT ---

# Inicializar y cargar los datos
initialize_session_state()

st.set_page_config(page_title="Editor de Vocabulario Griego", layout="centered")

st.title("📚 Editor de Diccionario Griego")

if not st.session_state['is_data_loaded']:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la URL del JSON.")
else:
    current_index = st.session_state['current_index']

    if current_index != -1:
        current_word = st.session_state['dictionary'][current_index]['palabra']
        
        st.subheader("Palabra Pendiente Actual:")
        # 3. Primer casilla: muestra la palabra pendiente
        st.text_input(
            label="Palabra Griega a Definir",
            value=current_word,
            disabled=True,
            key="display_word"
        )
        
        st.subheader("Información de la Palabra:")
        # 4. Segunda caja: permite ingresar la información
        st.text_area(
            label="Ingresa aquí la definición, traducción o información",
            height=200,
            key="editor_box",
            placeholder="Ej: 'αγαθός' significa 'bueno, excelente'. Es un adjetivo..."
        )
        
        # 5. Botón para guardar
        st.button("💾 Guardar y Siguiente", on_click=save_and_advance, type="primary")
        
        # 7. Los mensajes de guardado y limpieza se manejan con st.toast y st.rerun
        
    else:
        st.success("🎉 ¡Felicidades! Todas las palabras han sido completadas (en esta sesión).")
        st.info("Para que los cambios persistan en el tiempo, ¡debes integrarte con una base de datos!")


    # 9. Funcionalidad de Edición
    st.markdown("---")
    st.header("🔍 Buscar y Editar Palabras Completadas")

    completed_words = [
        (i, entry['palabra']) 
        for i, entry in enumerate(st.session_state['dictionary']) 
        if entry.get("estado") == "completado"
    ]

    if completed_words:
        options = [f"{word[1]} ({st.session_state['dictionary'][word[0]]['encabezado']})" for word in completed_words]
        
        selected_word_display = st.selectbox(
            "Selecciona una palabra para editar:",
            options=options,
            index=None,
            placeholder="Selecciona una palabra 'completada'..."
        )
        
        if selected_word_display:
            # Encuentra el índice original basado en la palabra seleccionada
            selected_word = selected_word_display.split(' (')[0]
            
            # Buscar el índice en la lista original
            edit_index = next((i for i, entry in enumerate(st.session_state['dictionary']) 
                               if entry['palabra'] == selected_word), -1)
            
            if edit_index != -1:
                st.button(f"✏️ Editar: {selected_word}", on_click=edit_existing_word, args=[edit_index])
    else:
        st.info("Aún no hay palabras en estado 'completado' para editar.")
