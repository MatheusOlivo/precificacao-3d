import streamlit as st

st.set_page_config(page_title="Precificação 3D", page_icon="🖨️")

st.title("🖨️ Precificação de Impressão 3D (€)")
st.write("PLA e PETG • Custo real com tempo, desgaste e falhas")

# ---------------------------------------------------------------
# MATERIAL
# ---------------------------------------------------------------
st.header("🧵 Material")
material = st.selectbox("Escolha o filamento", ["PLA", "PETG"])
if material == "PLA":
    preco_rolo = st.number_input("Preço do rolo PLA (€)", value=19.0)
else:
    preco_rolo = st.number_input("Preço do rolo PETG (€)", value=22.0)

peso_rolo = st.number_input("Peso do rolo (g)", value=1000.0)
gramas_usadas = st.number_input("Filamento usado (g)", min_value=0.0)

st.subheader("Outros materiais (opcional)")
outros_materiais = st.number_input(
    "Custo de outros componentes por peça (€) — ex: chip NFC, argola, ímanes, inserts",
    min_value=0.0, value=0.0,
    help="Tudo o que não é filamento nem embalagem mas entra na peça final."
)
custo_embalagem = st.number_input(
    "Custo de embalagem por peça (€)", min_value=0.0, value=0.0
)

# ---------------------------------------------------------------
# ENERGIA
# ---------------------------------------------------------------
st.header("⚡ Energia")
potencia = st.number_input("Potência da impressora (Watts)", value=130.0)
horas_impressao = st.number_input("Horas de impressão (por peça ou lote)", min_value=0.0)
preco_kwh = st.number_input("Preço do kWh (€)", value=0.155)

st.caption("Se estiveres a calcular para um LOTE (várias peças de uma vez), preenche 'Unidades no lote' abaixo para dividir tudo por unidade.")
unidades_lote = st.number_input("Unidades no lote", min_value=1, value=1)

# ---------------------------------------------------------------
# DEPRECIAÇÃO DA IMPRESSORA
# ---------------------------------------------------------------
st.header("🛠️ Desgaste da impressora")
preco_impressora = st.number_input("Preço pago pela impressora (€)", value=700.0)
vida_util_horas = st.number_input(
    "Vida útil estimada (horas de impressão)", value=4000.0,
    help="Estimativa comum: 3000–5000h antes de manutenção pesada ou substituição."
)
custo_manutencao_mes = st.number_input(
    "Custo médio de manutenção/peças de desgaste por mês (€) — bicos, correias, etc.",
    min_value=0.0, value=5.0
)
horas_impressao_mes = st.number_input(
    "Horas de impressão médias por mês (para diluir a manutenção)", min_value=1.0, value=100.0
)

custo_deprec_hora = preco_impressora / vida_util_horas if vida_util_horas > 0 else 0
custo_manutencao_hora = custo_manutencao_mes / horas_impressao_mes if horas_impressao_mes > 0 else 0
custo_maquina_hora = custo_deprec_hora + custo_manutencao_hora

# ---------------------------------------------------------------
# TEMPO (o teu trabalho)
# ---------------------------------------------------------------
st.header("⏱️ O teu tempo")
valor_hora_ativo = st.number_input(
    "Valor da tua hora — tempo ATIVO (€/h)", value=6.0,
    help="Modelagem, fatiamento, remoção de supports, montagem, embalagem, atendimento."
)
horas_ativas = st.number_input(
    "Horas de trabalho ATIVO (por peça ou lote)", min_value=0.0, value=0.0
)

percentual_hora_passivo = st.slider(
    "Valor da hora PASSIVA (impressão sozinha) como % da hora ativa", 0, 100, 20,
    help="Enquanto a impressora imprime sozinha podes fazer outra coisa, mas ainda há supervisão/risco. 15-25% é razoável para começar."
)
valor_hora_passivo = valor_hora_ativo * (percentual_hora_passivo / 100)

# ---------------------------------------------------------------
# TAXA DE FALHAS
# ---------------------------------------------------------------
st.header("⚠️ Taxa de falhas")
taxa_falha = st.slider(
    "% de impressões que falham (desperdício de material, energia e tempo)", 0, 50, 10
)

# ---------------------------------------------------------------
# TAXAS DE PLATAFORMA (opcional)
# ---------------------------------------------------------------
st.header("🏪 Comissões de venda (opcional)")
comissao_plataforma = st.slider(
    "Comissão de plataforma/marketplace (%)", 0, 30, 0
)

# ---------------------------------------------------------------
# LUCRO
# ---------------------------------------------------------------
st.header("💰 Lucro")
lucro_percentual = st.slider("Percentual de lucro (%)", 0, 300, 170)

# ---------------------------------------------------------------
# CÁLCULOS
# ---------------------------------------------------------------
if st.button("Calcular preço"):
    # custo por unidade (dividindo o lote)
    custo_filamento_total = (preco_rolo / peso_rolo) * gramas_usadas
    custo_energia_total = (potencia / 1000) * horas_impressao * preco_kwh

    custo_filamento_un = custo_filamento_total / unidades_lote
    custo_energia_un = custo_energia_total / unidades_lote
    horas_impressao_un = horas_impressao / unidades_lote

    # --- custo puro (o que a versão original calculava) ---
    custo_puro = custo_filamento_un + custo_energia_un

    # --- custo real (com tudo) ---
    custo_maquina_un = custo_maquina_hora * horas_impressao_un
    custo_tempo_ativo = valor_hora_ativo * horas_ativas
    custo_tempo_passivo = valor_hora_passivo * horas_impressao_un

    custo_antes_falha = (
        custo_puro
        + outros_materiais
        + custo_embalagem
        + custo_maquina_un
        + custo_tempo_ativo
        + custo_tempo_passivo
    )

    # taxa de falha infla o custo (as peças que falham têm de ser pagas pelas que vendem)
    fator_falha = 1 / (1 - taxa_falha / 100) if taxa_falha < 100 else 1
    custo_real = custo_antes_falha * fator_falha

    multiplicador = 1 + (lucro_percentual / 100)
    preco_antes_comissao = custo_real * multiplicador

    # comissão de plataforma soma-se por cima para não corroer a margem
    if comissao_plataforma > 0:
        preco_venda = preco_antes_comissao / (1 - comissao_plataforma / 100)
    else:
        preco_venda = preco_antes_comissao

    lucro_liquido = preco_venda * (1 - comissao_plataforma / 100) - custo_real

    st.success("✅ Resultado (por unidade)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Custo PURO (só material+energia)", f"€ {custo_puro:.2f}")
    with col2:
        st.metric("Custo REAL (com tempo, desgaste, falhas)", f"€ {custo_real:.2f}")

    diferenca = custo_real - custo_puro
    st.write(f"📊 Diferença escondida no cálculo simples: **€ {diferenca:.2f} por peça**")

    st.divider()
    st.write("**Detalhe do custo real:**")
    st.write(f"🧵 Filamento: € {custo_filamento_un:.2f}")
    st.write(f"🔩 Outros materiais: € {outros_materiais:.2f}")
    st.write(f"📦 Embalagem: € {custo_embalagem:.2f}")
    st.write(f"⚡ Energia: € {custo_energia_un:.2f}")
    st.write(f"🛠️ Desgaste/depreciação da máquina: € {custo_maquina_un:.2f}")
    st.write(f"⏱️ Tempo ativo teu ({horas_ativas:.2f}h × €{valor_hora_ativo:.2f}): € {custo_tempo_ativo:.2f}")
    st.write(f"⏱️ Tempo passivo (impressão, {horas_impressao_un:.2f}h × €{valor_hora_passivo:.2f}): € {custo_tempo_passivo:.2f}")
    st.write(f"⚠️ Impacto da taxa de falha ({taxa_falha}%): custo multiplicado por {fator_falha:.2f}x")

    st.divider()
    st.write(f"📈 Lucro aplicado: **{lucro_percentual}%**")
    if comissao_plataforma > 0:
        st.write(f"🏪 Comissão de plataforma: **{comissao_plataforma}%** (já incluída no preço final)")
    st.write(f"💰 **Preço de venda sugerido: € {preco_venda:.2f}**")
    st.write(f"✅ Lucro líquido real por peça (depois de tudo): **€ {lucro_liquido:.2f}**")

    horas_totais_un = horas_impressao_un + horas_ativas
    if horas_totais_un > 0:
        lucro_por_hora = lucro_liquido / horas_totais_un
        st.write(f"⏱️ Lucro líquido por hora de trabalho (ativo+passivo): **€ {lucro_por_hora:.2f}/h**")

# ---------------------------------------------------------------
# DISTRIBUIÇÃO DO LUCRO (gestão do dinheiro)
# ---------------------------------------------------------------
st.divider()
st.header("🏦 Distribuição do lucro do mês")
st.write(
    "Depois de saberes o teu lucro, usa esta secção para dividir o dinheiro em "
    "'cofres' — fiscal, reinvestimento e o teu salário. Podes usar o lucro de um mês inteiro, "
    "não só de uma peça."
)

lucro_mes = st.number_input(
    "Lucro líquido total do mês (€)", min_value=0.0, value=0.0,
    help="Soma do lucro de todas as vendas do mês. Se já calculaste o lucro por peça acima, multiplica pelas unidades vendidas."
)

st.subheader("Passo 1 — Reserva fiscal")
pct_fiscal = st.slider(
    "% reservada para impostos e Segurança Social", 0, 50, 27,
    help="IVA (se aplicável), Segurança Social (21,4% sobre 70% do rendimento), IRS. Confirma o valor exato com um contabilista."
)
valor_fiscal = lucro_mes * (pct_fiscal / 100)
lucro_disponivel = lucro_mes - valor_fiscal

st.subheader("Passo 2 — Reinvestimento vs. Salário")
pct_reinvestimento = st.slider(
    "% do lucro disponível para reinvestir no negócio (o resto é o teu salário)",
    0, 100, 50
)
valor_reinvestimento = lucro_disponivel * (pct_reinvestimento / 100)
valor_salario = lucro_disponivel - valor_reinvestimento

st.subheader("Passo 3 — Como dividir o reinvestimento")
col_a, col_b = st.columns(2)
with col_a:
    pct_stock = st.slider("Stock de insumos (%)", 0, 100, 40)
    pct_marketing = st.slider("Marketing digital (%)", 0, 100, 25)
with col_b:
    pct_manutencao = st.slider("Manutenção/melhorias (%)", 0, 100, 20)
    pct_expansao = st.slider("Poupança para expansão (%)", 0, 100, 15)

soma_pct_reinvest = pct_stock + pct_marketing + pct_manutencao + pct_expansao
if soma_pct_reinvest != 100:
    st.warning(f"⚠️ Os 4 valores acima somam {soma_pct_reinvest}%, não 100%. Ajusta os sliders para fecharem em 100%.")

if st.button("Calcular distribuição"):
    st.success("✅ Distribuição sugerida para este mês")

    st.write(f"💶 Lucro total do mês: **€ {lucro_mes:.2f}**")
    st.write(f"🏛️ Reserva fiscal ({pct_fiscal}%): **€ {valor_fiscal:.2f}**")
    st.write(f"📦 Lucro disponível após fiscal: **€ {lucro_disponivel:.2f}**")

    st.divider()
    st.write(f"🔧 Total para reinvestimento ({pct_reinvestimento}% do disponível): **€ {valor_reinvestimento:.2f}**")

    if soma_pct_reinvest > 0:
        valor_stock = valor_reinvestimento * (pct_stock / soma_pct_reinvest)
        valor_marketing = valor_reinvestimento * (pct_marketing / soma_pct_reinvest)
        valor_manutencao = valor_reinvestimento * (pct_manutencao / soma_pct_reinvest)
        valor_expansao = valor_reinvestimento * (pct_expansao / soma_pct_reinvest)
    else:
        valor_stock = valor_marketing = valor_manutencao = valor_expansao = 0.0

    st.write(f"　🧵 Stock de insumos: € {valor_stock:.2f}")
    st.write(f"　📣 Marketing digital: € {valor_marketing:.2f}")
    st.write(f"　🛠️ Manutenção/melhorias: € {valor_manutencao:.2f}")
    st.write(f"　🚀 Poupança para expansão (2ª impressora): € {valor_expansao:.2f}")

    st.divider()
    st.write(f"💰 **O teu salário este mês: € {valor_salario:.2f}**")

    if lucro_mes > 0:
        st.caption(
            f"Isto equivale a {valor_salario / lucro_mes * 100:.0f}% do lucro total ficando "
            "diretamente para ti, depois de fiscal e reinvestimento."
        )
