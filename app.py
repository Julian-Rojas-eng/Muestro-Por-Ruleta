"""Simulador RWS con Streamlit y Plotly.
Ejecutar: python -m streamlit run ruleta_plotly_animada.py
"""
import random
import time

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Muestreo por ruleta (RWS)", page_icon="🎯", layout="wide")

NOMBRES = ["A", "B", "C", "D"]
APTITUDES = [10, 30, 20, 40]
COLORES = ["#E1B12C", "#2E5984", "#DB4545", "#10253E"]
PROB = [a / sum(APTITUDES) for a in APTITUDES]

if "conteos" not in st.session_state:
    st.session_state.conteos = [0] * len(NOMBRES)
if "ultimo" not in st.session_state:
    st.session_state.ultimo = None
if "angulo" not in st.session_state:
    st.session_state.angulo = 0.0


def seleccionar():
    """Seleccionar según las probabilidades acumuladas, usando U[0,1)."""
    numero = random.random()
    acumulada = 0.0
    for i, p in enumerate(PROB):
        acumulada += p
        if numero < acumulada:
            return i, numero
    return len(PROB) - 1, numero


def dibujar_ruleta(rotacion=0):
    """Dibujar una ruleta circular; la flecha dorada permanece fija arriba."""
    fig = go.Figure(go.Pie(
        labels=NOMBRES,
        values=APTITUDES,
        sort=False,
        direction="clockwise",
        rotation=rotacion % 360,
        marker=dict(colors=COLORES, line=dict(color="white", width=3)),
        textinfo="label+percent",
        textfont=dict(size=18, color="white"),
        hovertemplate="Individuo %{label}<br>Aptitud: %{value}<br>Probabilidad: %{percent}<extra></extra>",
        showlegend=False,
    ))
    # Flecha fija dorada con contorno azul oscuro, visible sobre todos los sectores.
    fig.update_layout(
        title="Ruleta de probabilidades",
        height=425,
        margin=dict(l=10, r=10, t=80, b=10),
        shapes=[dict(
            type="path", xref="paper", yref="paper",
            # Punta hacia la ruleta y base ligeramente por encima de ella.
            path="M 0.475,1.095 L 0.525,1.095 L 0.5,1.01 Z",
            fillcolor="#E1B12C",
            line=dict(color="#10253E", width=3),
            layer="above",
        )],
    )
    return fig


st.title("🎯 Muestreo por ruleta (RWS)")
st.write("**Selección proporcional al valor de aptitud** — demostración de Probabilidad y Estadística")
st.caption("Cada individuo ocupa un sector proporcional a su aptitud. El azar determina quién es seleccionado.")

izquierda, derecha = st.columns([1.2, 1], gap="large")
with izquierda:
    espacio_ruleta = st.empty()
    espacio_ruleta.plotly_chart(dibujar_ruleta(st.session_state.angulo), use_container_width=True)
    st.caption("La flecha dorada indica el sector seleccionado después del giro.")

with derecha:
    st.subheader("Aptitudes y probabilidades")
    st.table({
        "Individuo": NOMBRES,
        "Aptitud": APTITUDES,
        "Probabilidad": [f"{p:.0%}" for p in PROB],
    })
    st.latex(r"P(i)=\frac{f_i}{\sum_{j=1}^{n}f_j}")
    st.write("**Intervalos acumulados:**")
    st.write("A: [0, 0.10) · B: [0.10, 0.40) · C: [0.40, 0.60) · D: [0.60, 1.00)")

c1, c2, c3 = st.columns(3)
with c1:
    uno = st.button("🎲 Girar y seleccionar", type="primary", use_container_width=True)
with c2:
    muchos = st.button("🔁 Simular 1000", use_container_width=True)
with c3:
    reiniciar = st.button("🧹 Reiniciar", use_container_width=True)

if reiniciar:
    st.session_state.conteos = [0] * len(NOMBRES)
    st.session_state.ultimo = None
    st.session_state.angulo = 0.0
    espacio_ruleta.plotly_chart(dibujar_ruleta(0), use_container_width=True)
elif uno:
    indice, numero = seleccionar()
    # El sector seleccionado se coloca debajo del indicador fijo (arriba).
    # Partimos de 0° en la parte superior y avanzamos en sentido horario.
    inicio = sum(PROB[:indice]) * 360
    mitad = PROB[indice] * 180
    objetivo = (-inicio - mitad) % 360
    origen = st.session_state.angulo
    distancia = 4 * 360 + (objetivo - origen) % 360
    pasos = 24
    for paso in range(1, pasos + 1):
        t = paso / pasos
        progreso = 1 - (1 - t) ** 3  # desaceleración suave
        espacio_ruleta.plotly_chart(
            dibujar_ruleta(origen + distancia * progreso),
            use_container_width=True,
            key=f"giro_{paso}",
        )
        time.sleep(0.035)
    st.session_state.angulo = objetivo
    st.session_state.conteos[indice] += 1
    st.session_state.ultimo = (indice, numero)
elif muchos:
    for _ in range(1000):
        indice, _ = seleccionar()
        st.session_state.conteos[indice] += 1
    st.session_state.ultimo = None

if st.session_state.ultimo is not None:
    indice, numero = st.session_state.ultimo
    st.success(f"Individuo seleccionado: **{NOMBRES[indice]}** · Número aleatorio: **{numero:.4f}**")

conteos = st.session_state.conteos
n = sum(conteos)
st.subheader(f"Resultados acumulados — {n} selecciones")
if n:
    observados = [100 * c / n for c in conteos]
    barras = go.Figure()
    barras.add_bar(x=NOMBRES, y=observados, name="Frecuencia observada (%)",
                   marker_color=COLORES, text=[f"{v:.1f}%" for v in observados],
                   textposition="outside")
    barras.add_scatter(x=NOMBRES, y=[p * 100 for p in PROB],
                       name="Probabilidad teórica (%)", mode="lines+markers",
                       line=dict(color="#333333", dash="dash"))
    barras.update_layout(yaxis_title="Porcentaje (%)", xaxis_title="Individuo",
                         yaxis=dict(range=[0, max(55, max(observados) + 12)]),
                         margin=dict(l=20, r=20, t=20, b=20), height=370)
    st.plotly_chart(barras, use_container_width=True)
    st.caption("Con muchas selecciones, las frecuencias observadas tienden a acercarse a las probabilidades teóricas.")
else:
    st.info("Presiona **Girar y seleccionar** o **Simular 1000** para ver los resultados.")
