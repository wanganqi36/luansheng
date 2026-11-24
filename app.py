import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="平行板电容器数字孪生平台",
                   page_icon="🔬", layout="wide")

st.title("🔬 平行板电容器数字孪生平台")
st.caption("微创手术机器人位移传感器 · 电容式位移测量仿真")

EPS0 = 8.85e-12

MEDIA = {
    "真空 (εr=1.0)": 1.0,
    "空气 (εr=1.0006)": 1.0006,
    "纸 (εr=3.5)": 3.5,
    "玻璃 (εr=5.0)": 5.0,
    "云母 (εr=6.0)": 6.0,
    "陶瓷 (εr=10.0)": 10.0,
}

# ===================== 侧边栏 =====================
with st.sidebar:
    st.header("⚙️ 参数调节")

    S = st.slider("极板面积 S (cm²)", 10.0, 500.0, 100.0, 5.0)
    d = st.slider("极板间距 d (mm)", 1.0, 10.0, 5.0, 0.1)

    st.divider()
    mode = st.radio("工作模式", ["电荷Q恒定", "电压U恒定"], index=0)

    # 根据模式显示不同的输入量
    if mode == "电荷Q恒定":
        Q = st.slider("电荷量 Q (nC)", 1.0, 200.0, 50.0, 1.0)
        U_in = None
    else:
        U_in = st.slider("电压 U (V)", 10.0, 3000.0, 1000.0, 10.0)
        Q = None

    st.divider()
    media_name = st.selectbox("介质类型", list(MEDIA.keys()), index=0)
    er = MEDIA[media_name]

    st.divider()
    st.markdown(
        "**核心公式**\n\n"
        "$$C = \\frac{\\varepsilon_0 \\varepsilon_r S}{d}$$\n\n"
        "**电荷Q恒定：**\n"
        "$$U = \\frac{Q}{C},\\quad E = \\frac{\\sigma}{\\varepsilon_0\\varepsilon_r}$$\n\n"
        "**电压U恒定：**\n"
        "$$Q = CU,\\quad E = \\frac{U}{d}$$"
    )

# ===================== 物理计算 =====================
S_m2 = S * 1e-4
d_m = d * 1e-3

# 电容（只与 S、d、εr 有关）
C = EPS0 * er * S_m2 / d_m
C_pF = C * 1e12

if mode == "电荷Q恒定":
    Q_C = Q * 1e-9
    U = Q_C / C                    # U 随 C 变化
    E = Q_C / (EPS0 * er * S_m2)   # E 不变
    sigma = Q_C / S_m2
else:
    U = U_in                       # U 恒定不变
    Q_C = C * U                    # Q 随 C 变化
    Q = Q_C * 1e9
    E = U / d_m                    # E 随 d 变化
    sigma = Q_C / S_m2

sigma_nC = sigma * 1e9

# ===================== 指标卡片 =====================
c1, c2, c3, c4 = st.columns(4)
c1.metric("电容 C", f"{C_pF:.2f} pF")
c2.metric("场强 E", f"{E:,.2f} V/m")
c3.metric("电压 U", f"{U:,.3f} V")
c4.metric("面密度 σ", f"{sigma_nC:,.2f} nC/m²")

if mode == "电荷Q恒定":
    st.info(f"⚡ 当前模式：**电荷 Q 恒定** = {Q:.1f} nC（输入量）→ 改变 d 时 U 变化、E 不变")
else:
    st.success(f"🔋 当前模式：**电压 U 恒定** = {U_in:.1f} V（输入量）→ 改变 d 时 Q 变化、E = U/d 变化")

st.divider()

# ===================== 图1：剖面图 =====================
st.subheader("📐 电容器实时剖面")

Y_MAX = 7.0
PLATE_W = 8.0
plate_thick = 0.4 + (S / 500.0) * 0.8

fig = go.Figure()

fig.add_shape(type="rect", x0=-PLATE_W, x1=PLATE_W,
              y0=d/2, y1=d/2 + plate_thick,
              fillcolor="#1f77b4", line=dict(width=0))
fig.add_shape(type="rect", x0=-PLATE_W, x1=PLATE_W,
              y0=-d/2 - plate_thick, y1=-d/2,
              fillcolor="#d62728", line=dict(width=0))

# 电场线：密度随 E 变化，U恒定时拖 d 会明显变疏密
n_lines = int(np.clip(E / 60000, 3, 18))
for x in np.linspace(-PLATE_W*0.8, PLATE_W*0.8, n_lines):
    fig.add_shape(type="line", x0=x, x1=x, y0=-d/2, y1=d/2,
                  line=dict(color="rgba(120,120,120,0.55)", width=1, dash="dot"))

fig.add_annotation(x=PLATE_W*0.55, y=0,
                   text=f"<b>d = {d:.1f} mm</b>", showarrow=False,
                   font=dict(size=15, color="#333333"),
                   bgcolor="rgba(255,255,255,0.85)",
                   bordercolor="#999999", borderwidth=1, borderpad=4)

fig.add_annotation(x=-PLATE_W*0.85, y=d/2 + plate_thick/2,
                   text="<b>+</b>", showarrow=False,
                   font=dict(size=16, color="white"))
fig.add_annotation(x=-PLATE_W*0.85, y=-d/2 - plate_thick/2,
                   text="<b>−</b>", showarrow=False,
                   font=dict(size=16, color="white"))

fig.update_layout(
    height=380, margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(range=[-10, 10], showgrid=False, zeroline=False,
               showticklabels=False, fixedrange=True),
    yaxis=dict(range=[-Y_MAX, Y_MAX], showgrid=False, zeroline=False,
               showticklabels=False, fixedrange=True, scaleanchor="x"),
    plot_bgcolor="white", showlegend=False
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ===================== 图2：C-d 曲线 =====================
st.subheader("📈 电容 C 随极板间距 d 的变化特性")

d_arr = np.linspace(1.0, 10.0, 200)
C_arr = EPS0 * er * S_m2 / (d_arr * 1e-3) * 1e12

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=d_arr, y=C_arr, mode="lines", name="C-d 理论曲线",
                          line=dict(color="#1f77b4", width=3)))
fig2.add_trace(go.Scatter(x=[d], y=[C_pF], mode="markers+text",
                          text=[f"  d={d:.1f}mm, C={C_pF:.2f}pF"],
                          textposition="top right",
                          textfont=dict(size=12, color="red"),
                          marker=dict(size=15, color="red",
                                      line=dict(width=2, color="white")),
                          name="当前工作点"))
fig2.add_shape(type="line", x0=d, x1=d, y0=0, y1=C_pF,
               line=dict(color="red", width=1, dash="dash"))
fig2.add_shape(type="line", x0=0, x1=d, y0=C_pF, y1=C_pF,
               line=dict(color="red", width=1, dash="dash"))

fig2.update_layout(
    height=380, margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="极板间距 d (mm)", gridcolor="#eeeeee"),
    yaxis=dict(title="电容 C (pF)", gridcolor="#eeeeee"),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode="x unified"
)
st.plotly_chart(fig2, use_container_width=True)
st.divider()

# ===================== 图3：E-d 曲线（新增） =====================
st.subheader("📉 场强 E 随极板间距 d 的变化特性")

if mode == "电荷Q恒定":
    E_arr = np.full_like(d_arr, E)
    y_title = "场强 E (V/m)"
    note = "Q 恒定时 E = σ/(ε₀εᵣ) 与 d 无关，故为水平直线"
else:
    E_arr = U / (d_arr * 1e-3)
    y_title = "场强 E (V/m)"
    note = "U 恒定时 E = U/d，与 d 成反比"

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=d_arr, y=E_arr, mode="lines", name="E-d 曲线",
                          line=dict(color="#2ca02c", width=3)))
fig3.add_trace(go.Scatter(x=[d], y=[E], mode="markers",
                          marker=dict(size=15, color="red",
                                      line=dict(width=2, color="white")),
                          name="当前工作点"))
fig3.update_layout(
    height=350, margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="极板间距 d (mm)", gridcolor="#eeeeee"),
    yaxis=dict(title=y_title, gridcolor="#eeeeee"),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode="x unified",
    annotations=[dict(text=note, xref="paper", yref="paper",
                      x=0.01, y=0.95, showarrow=False,
                      font=dict(size=11, color="#666666"))]
)
st.plotly_chart(fig3, use_container_width=True)
st.divider()

# ===================== 结论 =====================
st.subheader("💡 仿真结论")

if mode == "电荷Q恒定":
    st.markdown(
        f"- **Q = {Q:.1f} nC 恒定**，改变 d：C = ε₀εᵣS/d 随 d 增大而减小，"
        f"由 U = Q/C 知 **U 随 d 增大而增大**；"
        f"而 E = σ/(ε₀εᵣ) 仅由面密度和介质决定，**与 d 无关，保持不变**。"
    )
else:
    st.markdown(
        f"- **U = {U:.1f} V 恒定**，改变 d：C 随 d 增大而减小，"
        f"由 Q = CU 知 **Q 随 d 增大而减小**（极板放电）；"
        f"由 E = U/d 知 **E 与 d 成反比，d 增大则 E 减小**。"
    )

st.markdown(
    f"- **核心规律**：C = ε₀εᵣS/d，电容与极板间距 d 成**反比**，"
    f"与面积 S、相对介电常数 εᵣ 成**正比**。\n"
    f"- **应用价值**：这正是电容式位移传感器原理——被测物体带动极板移动使 d 改变，"
    f"通过测量 C 的变化反推微小位移，适用于微创手术机器人高精度位置检测。"
)