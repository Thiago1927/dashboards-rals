import pandas as pd
from dash import Dash, html, dcc
import plotly.graph_objects as go
import plotly.express as px

# === 1️⃣ Leitura e filtragem ===
df = pd.read_excel("Link_status_09_10.xlsx")

# Mantém apenas linhas com número na coluna "RAL/INC CADASTRADOS"
df = df[pd.to_numeric(df["RAL/INC CADASTRADOS"], errors="coerce").notna()]

# Converte colunas de data/hora
df["HORÁRIO ALARME"] = pd.to_datetime(df["HORÁRIO ALARME"], errors="coerce")
df["HORÁRIO NORMALIZAÇÃO"] = pd.to_datetime(df["HORÁRIO NORMALIZAÇÃO"], errors="coerce")

# Calcula tempo de recuperação (em minutos)
df["TEMPO_RECUPERACAO"] = (df["HORÁRIO NORMALIZAÇÃO"] - df["HORÁRIO ALARME"]).dt.total_seconds() / 60

# Remove tempos inválidos
df = df[df["TEMPO_RECUPERACAO"].notna() & (df["TEMPO_RECUPERACAO"] > 0)]

# Cria colunas auxiliares
df["MÊS"] = df["HORÁRIO ALARME"].dt.to_period("M").astype(str)
df["DIA"] = df["HORÁRIO ALARME"].dt.date

# === 2️⃣ Estatísticas principais ===
total_rals = len(df)
tempo_medio = df["TEMPO_RECUPERACAO"].mean()
tempo_min = df["TEMPO_RECUPERACAO"].min()
tempo_max = df["TEMPO_RECUPERACAO"].max()

# === 3️⃣ Divisões por tempo de recuperação ===
rals_ate_5 = len(df[df["TEMPO_RECUPERACAO"] <= 5])
rals_ate_10 = len(df[df["TEMPO_RECUPERACAO"] <= 10])
rals_ate_15 = len(df[df["TEMPO_RECUPERACAO"] <= 15])

# === 4️⃣ Agrupamento diário ===
diario = df.groupby("DIA").agg(QTD_RALS=("RAL/INC CADASTRADOS", "count")).reset_index()

# === 5️⃣ Gráfico de colunas (RALs por dia) ===
fig_colunas = go.Figure()
fig_colunas.add_trace(go.Bar(
    x=diario["DIA"],
    y=diario["QTD_RALS"],
    name="RALs abertas",
    marker_color="#00CCFF"
))

fig_colunas.update_layout(
    template="plotly_dark",
    title="📅 RALs Abertas por Dia",
    xaxis_title="Data",
    yaxis_title="Quantidade de RALs",
    plot_bgcolor="#111",
    paper_bgcolor="#111",
    font=dict(color="white"),
    hovermode="x unified",
)

# === 6️⃣ Gráfico de pizza (divisão por mês) ===
pizza = df["MÊS"].value_counts().reset_index()
pizza.columns = ["MÊS", "QTD"]
fig_pizza = px.pie(
    pizza,
    values="QTD",
    names="MÊS",
    title="📊 Distribuição de RALs por Mês",
    color_discrete_sequence=["#00CCFF", "#FF8800"],
    hole=0.4
)
fig_pizza.update_traces(textinfo="percent+label", pull=[0.05, 0.05])
fig_pizza.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111",
    font=dict(color="white")
)

# === 7️⃣ Layout do Dashboard ===
app = Dash(__name__)
app.title = "Dashboard RALs - Tema Dark Profissional"

app.layout = html.Div(style={
    "backgroundColor": "#0c0c0c",
    "color": "white",
    "padding": "30px",
    "fontFamily": "Segoe UI, sans-serif"
}, children=[
    html.H1("📈 Dashboard de RALs e Tempos de Recuperação", style={"textAlign": "center"}),

    # --- Cards principais ---
    html.Div(style={"display": "flex", "justifyContent": "space-around", "marginTop": "30px"}, children=[
        html.Div([
            html.H3("🔢 Total de RALs"),
            html.H2(f"{total_rals:,}".replace(",", "."), style={"color": "#00CCFF"})
        ]),
        html.Div([
            html.H3("⏱️ Tempo Médio"),
            html.H2(f"{tempo_medio:.1f} min", style={"color": "#FF8800"})
        ]),
        html.Div([
            html.H3("⬇️ Menor Tempo"),
            html.H2(f"{tempo_min:.1f} min", style={"color": "#00FF88"})
        ]),
        html.Div([
            html.H3("⬆️ Maior Tempo"),
            html.H2(f"{tempo_max:.1f} min", style={"color": "#FF4444"})
        ]),
    ]),

    html.Br(),

    # --- Novas divisões por faixa de tempo ---
    html.Div(style={"display": "flex", "justifyContent": "space-evenly", "marginTop": "20px"}, children=[
        html.Div([
            html.H4("🟢 RALs ≤ 5 min"),
            html.H3(f"{rals_ate_5:,}".replace(",", "."), style={"color": "#00FF88"})
        ], style={"backgroundColor": "#1a1a1a", "padding": "20px", "borderRadius": "12px", "width": "25%", "textAlign": "center"}),
        html.Div([
            html.H4("🟡 RALs ≤ 10 min"),
            html.H3(f"{rals_ate_10:,}".replace(",", "."), style={"color": "#FFD700"})
        ], style={"backgroundColor": "#1a1a1a", "padding": "20px", "borderRadius": "12px", "width": "25%", "textAlign": "center"}),
        html.Div([
            html.H4("🔴 RALs ≤ 15 min"),
            html.H3(f"{rals_ate_15:,}".replace(",", "."), style={"color": "#FF5555"})
        ], style={"backgroundColor": "#1a1a1a", "padding": "20px", "borderRadius": "12px", "width": "25%", "textAlign": "center"}),
    ]),

    html.Br(),
    html.Hr(style={"borderColor": "#333"}),

    # --- Gráficos lado a lado ---
    html.Div(style={"display": "flex", "justifyContent": "space-around", "marginTop": "30px"}, children=[
        html.Div([
            dcc.Graph(figure=fig_colunas, style={"height": "500px", "width": "800px"})
        ]),
        html.Div([
            dcc.Graph(figure=fig_pizza, style={"height": "500px", "width": "500px"})
        ]),
    ])
])

# === 8️⃣ Execução ===
if __name__ == "__main__":
    app.run(debug=True)