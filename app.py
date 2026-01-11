import streamlit as st

st.title("🖨️ Precificação de Impressão 3D (€)")
st.write("PLA e PETG • Lucro ajustável")

st.header("🧵 Material")
material = st.selectbox("Escolha o filamento", ["PLA", "PETG"])

if material == "PLA":
    preco_rolo = st.number_input("Preço do rolo PLA (€)", value=22.0)
else:
    preco_rolo = st.number_input("Preço do rolo PETG (€)", value=28.0)

peso_rolo = st.number_input("Peso do rolo (g)", value=1000.0)
gramas_usadas = st.number_input("Filamento usado (g)", min_value=0.0)

st.header("⚡ Energia")
potencia = st.number_input("Potência da impressora (Watts)", value=300.0)
horas = st.number_input("Horas de impressão", min_value=0.0)
preco_kwh = st.number_input("Preço do kWh (€)", value=0.25)

st.header("💰 Lucro")
lucro_percentual = st.slider("Percentual de lucro (%)", 0, 300, 170)

if st.button("Calcular preço"):
    custo_filamento = (preco_rolo / peso_rolo) * gramas_usadas
    custo_energia = (potencia / 1000) * horas * preco_kwh
    custo_total = custo_filamento + custo_energia

    multiplicador = 1 + (lucro_percentual / 100)
    preco_venda = custo_total * multiplicador

    st.success("✅ Resultado")
    st.write(f"🧵 Material: **{material}**")
    st.write(f"🧵 Custo do filamento: **€ {custo_filamento:.2f}**")
    st.write(f"⚡ Custo de energia: **€ {custo_energia:.2f}**")
    st.write(f"📦 Custo total: **€ {custo_total:.2f}**")
    st.write(f"📈 Lucro aplicado: **{lucro_percentual}%**")
    st.write(f"💰 **Preço de venda: € {preco_venda:.2f}**")
