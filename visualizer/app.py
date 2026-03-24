import os
import json
import time
from collections import Counter
import streamlit as st
import pandas as pd
import redis

st.set_page_config(page_title="GitHub Method Miner", page_icon="📊", layout="wide")
st.title("Ranking de Palabras en Código Fuente")
st.markdown("Visualización en tiempo real de los métodos más usados en GitHub.")

# conexión a Redis (Igual que en el Miner)
@st.cache_resource
def get_redis_client():
    host = os.environ.get('REDIS_HOST', 'localhost')
    return redis.Redis(host=host, port=6379, decode_responses=True)

redis_client = get_redis_client()

# interfaz parametrizable
top_n = st.sidebar.slider("¿Cuántas palabras quieres ver en el Top?", min_value=5, max_value=50, value=15)
st.sidebar.markdown("---")
st.sidebar.info("El dashboard se actualiza automáticamente cada 2 segundos.")

# contenedores vacíos que se actualizaran en el bucle
metrics_placeholder = st.empty()
charts_placeholder = st.empty()

# bucle de actualización en tiempo real
while True:
    # se obtienen todos los mensajes de la cola sin borrarlos (lrange)
    raw_data = redis_client.lrange('words_queue', 0, -1)
    
    python_words = []
    java_words = []
    
    # se decodifica el JSON y se separa por lenguaje
    for item in raw_data:
        try:
            data = json.loads(item)
            if data['language'] == 'python':
                python_words.append(data['word'])
            elif data['language'] == 'java':
                java_words.append(data['word'])
        except json.JSONDecodeError:
            continue

    # se actualizan las métricas generales y se destaca al ganador
    with metrics_placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Palabras Extraídas", len(python_words) + len(java_words))
        col2.metric("Palabras de Python", len(python_words))
        col3.metric("Palabras de Java", len(java_words))
        
        st.markdown("---")
        
        # lógica para encontrar la palabra más usada de cada lenguaje
        top_py_word, top_py_count = ("-", 0)
        top_java_word, top_java_count = ("-", 0)
        
        if python_words:
            top_py = Counter(python_words).most_common(1)[0]
            top_py_word, top_py_count = top_py[0], top_py[1]
            
        if java_words:
            top_java = Counter(java_words).most_common(1)[0]
            top_java_word, top_java_count = top_java[0], top_java[1]

        col_win_py, col_win_java = st.columns(2)

        # se destaca al ganador global
        if top_py_count > top_java_count and top_py_count > 0:
            col_win_py.success(f"👑 **GANADOR GLOBAL:** `{top_py_word}` con {top_py_count} usos (Python)")
            col_win_java.info(f"Palabra #1 en Java: `{top_java_word}` ({top_java_count} usos)")
            
        elif top_java_count > top_py_count and top_java_count > 0:
            col_win_py.info(f"Palabra #1 en Python: `{top_py_word}` ({top_py_count} usos)")
            col_win_java.success(f"👑 **GANADOR GLOBAL:** `{top_java_word}` con {top_java_count} usos (Java)")
            
        elif top_py_count == top_java_count and top_py_count > 0:
            col_win_py.warning(f"⚔️ **EMPATE:** `{top_py_word}` ({top_py_count} usos)")
            col_win_java.warning(f"⚔️ **EMPATE:** `{top_java_word}` ({top_java_count} usos)")
        else:
            col_win_py.write("Esperando datos...")
            col_win_java.write("Esperando datos...")

    # se actualizan los gráficos
    with charts_placeholder.container():
        col_py, col_java = st.columns(2)
        
        with col_py:
            st.subheader("Top Python")
            if python_words:
                # se cuentan las frecuencias y se arma un DataFrame de Pandas para el gráfico
                py_counter = Counter(python_words).most_common(top_n)
                df_py = pd.DataFrame(py_counter, columns=['Palabra', 'Frecuencia']).set_index('Palabra')
                st.bar_chart(df_py, color="#FFD43B") # Amarillo Python
            else:
                st.info("Esperando datos de Python...")
                
        with col_java:
            st.subheader("Top Java")
            if java_words:
                java_counter = Counter(java_words).most_common(top_n)
                df_java = pd.DataFrame(java_counter, columns=['Palabra', 'Frecuencia']).set_index('Palabra')
                st.bar_chart(df_java, color="#f89820") # Naranja Java
            else:
                st.info("Esperando datos de Java...")

    # pausa de 2 segundos antes de volver a consultar Redis
    time.sleep(2)
    st.rerun()