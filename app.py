import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="IA Loteria V7", layout="centered")

st.title("🎯 IA Loteria Profissional V7")

arquivo = st.file_uploader("📂 Envie o CSV da Lotofácil")

# =========================
# FUNÇÕES
# =========================

def analisar_ciclo(df):
    todos = set(range(1, 26))
    ciclo = set()
    concursos = 0

    for i in range(len(df)-1, -1, -1):
        linha = set(df.iloc[i].dropna().astype(int))
        ciclo |= linha
        concursos += 1

        if ciclo == todos:
            break

    faltantes = list(todos - ciclo)

    if concursos <= 2:
        fase = "INÍCIO"
    elif concursos <= 4:
        fase = "MEIO"
    else:
        fase = "FINAL"

    return concursos, fase, faltantes


def frequencia(df):
    freq = {n: 0 for n in range(1, 26)}

    for _, row in df.iterrows():
        for n in row.dropna():
            freq[int(n)] += 1

    return sorted(freq, key=freq.get, reverse=True)


def gerar_jogo(base, faltantes, fase, modo):

    if modo == "Conservador":
        pool = base[:20]

    elif modo == "Agressivo":
        pool = list(set(base[:10] + random.sample(base, 10)))

    elif modo == "Ciclo Puro":
        pool = list(set(faltantes + base[:10]))

    else:
        pool = base[:20]

    if len(pool) < 15:
        pool = list(set(pool + base[:20]))

    return sorted(random.sample(pool, 15))


def analisar_jogo(jogo):
    pares = sum(1 for n in jogo if n % 2 == 0)
    soma = sum(jogo)

    linhas = [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1

    return pares, soma, linhas


def jogo_valido(jogo):
    pares, soma, linhas = analisar_jogo(jogo)

    if pares < 6 or pares > 9:
        return False

    if soma < 170 or soma > 230:
        return False

    if max(linhas) > 5:
        return False

    return True


def melhor_jogo(base, faltantes, fase, modo):
    for _ in range(100):
        jogo = gerar_jogo(base, faltantes, fase, modo)
        if jogo_valido(jogo):
            return jogo
    return jogo


def simular(base, faltantes, fase, modo, qtd=300):
    bons = []

    for _ in range(qtd):
        jogo = gerar_jogo(base, faltantes, fase, modo)
        if jogo_valido(jogo):
            bons.append(jogo)

    return bons[:5]


# =========================
# EXECUÇÃO
# =========================

if arquivo is not None:

    df = pd.read_csv(arquivo)

    concursos, fase, faltantes = analisar_ciclo(df)
    base = frequencia(df)

    st.subheader("📊 Ciclo")
    st.write(f"Concursos: {concursos}")
    st.write(f"Fase: {fase}")
    st.write(f"Faltantes: {faltantes}")

    st.subheader("🔥 Frequentes")
    st.write(base[:15])

    # CONFIGURAÇÃO
    st.subheader("⚙️ Configuração")

    qtd_jogos = st.slider("Quantidade de jogos", 1, 20, 5)

    modo = st.selectbox(
        "Modo",
        ["Conservador", "Agressivo", "Ciclo Puro"]
    )

    # BOTÕES
    if st.button("🔥 Melhor jogo"):
        jogo = melhor_jogo(base, faltantes, fase, modo)
        st.write(jogo)

    if st.button("🚀 Simular"):
        jogos = simular(base, faltantes, fase, modo)

        for j in jogos[:qtd_jogos]:
            st.write(j)