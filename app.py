import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="平行板电容器数字孪生平台",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 平行板电容器数字孪生平台")
st.caption("微创手术机器人位移传感器 · 电容式位移测量仿真")

# ===================== 物理常数 =====================
EPS0 = 8.85e-12   # 真空介电常数 F/m

# 介质相对介电常数
MEDIA = {
    "真空 (εr=1.0)": 1.0,
    "空气 (εr=1.0006)": 1.0006,
    "纸 (εr=3.5)": 3.5,
    "玻璃 (εr=5.0)": 5.0,
    "云母 (εr=6.0)": 6.0,
    "陶瓷 (εr=10.0)": 10.0,
}

# ===================== 侧边栏参数调节 =====================
with st.sidebar:
    st.header("⚙️ 参数调节")

    S = st.slider("极板面积 S (cm²)", 10.0, 500.0, 100.0, 5.0)
    d = st.slider("极板间距 d (mm)", 1.0, 10.0, 5.0, 0.1)
    Q = st.slider("电荷量 Q (nC)", 1.0, 200.0, 50.0, 1.0)

    st.divider()
    media_name = st.selectbox("介质类型", list(MEDIA.keys()), index=0)
    er = MEDIA[media_name]

    st.divider()
    mode = st.radio("工作模式", ["电荷Q恒定", "电压U恒定"], index=0)

    st.divider()
    st.markdown(
        "**核心公式**\n\n"
        "$$C = \\frac{\\varepsilon_0 \\varepsilon_r S}{d}$$\n\n"
        "$$E = \\frac{\\sigma}{\\varepsilon_0 \\varepsilon_r} = \\frac{U}{d}$$\n\n"
        "$$\\sigma = \\frac{Q}{S} \\qquad U = \\frac{Q}{C}$$"
    )

# ===================== 物理计算 =====================
S_m2 = S * 1e-4        # cm² -> m²
d_m = d * 1e-3         # mm  -> m
Q_C = Q * 1e-9         # nC  -> C

# 电容
C = EPS0 * er * S_m2 / d_m          # F
C_pF = C * 1e12                     # pF

# 电荷面密度
sigma = Q_C / S_m2                  # C/m²
sigma_nC = sigma * 1e9              # nC/m²

# 电压与场强（区分两种工作模式）
if mode == "电荷Q恒定":
    U = Q_C / C                     # V
    E = U / d_m                     # V/m
    U_show, E_show = U, E
else:
    U = Q_C / C                     # 基准电压
    E = sigma / (EPS0 * er)         # 电压恒定时 E 只与面密度和介质有关
    U_show, E_show = U, E

# ===================== 指标卡片 =====================
c1, c2, c3, c4 = st.columns(4)
c1.metric("电容 C", f"{C_pF:.2f} pF")
c2.metric("场强 E", f"{E_show:.2f} V/m")
c3.metric("电压 U", f"{U_show:.3f} V")
c4.metric("面密度 σ", f"{sigma_nC:.2f} nC/m²")

st.divider()

# ===================== 图1：电容器实时剖面 =====================
st.subheader("📐 电容器实时剖面")

# 固定坐标范围：极板间距变化时图形不再自动缩放
Y_MAX = 7.0        # 固定 y 轴半高
PLATE_W = 8.0      # 极板半宽（固定，代表面积 S）

fig = go.Figure()

# 上极板（正，蓝色）—— 厚度随面积 S 变化，直观体现面积影响
plate_thick = 0.4 + (S / 500.0) * 0.8
fig.add_shape(
    type="rect",
    x0=-PLATE_W, x1=PLATE_W,
    y0=d / 2, y1=d / 2 + plate_thick,
    fillcolor="#1f77b4", line=dict(width=0)
)

# 下极板（负，红色）
fig.add_shape(
    type="rect",
    x0=-PLATE_W, x1=PLATE_W,
    y0=-d / 2 - plate_thick, y1=-d / 2,
    fillcolor="#d62728", line=dict(width=0)
)

# 极板间电场线（虚线，数量随场强变化）
n_lines = int(np.clip(E_show / 80000, 3, 15))
for x in np.linspace(-PLATE_W * 0.8, PLATE_W * 0.8, n_lines):
    fig.add_shape(
        type="line",
        x0=x, x1=x, y0=-d / 2, y1=d / 2,
        line=dict(color="rgba(120,120,120,0.55)", width=1, dash="dot")
    )

# 间距标注箭头
fig.add_annotation(
    x=PLATE_W * 0.55, y=0,
    text=f"<b>d = {d:.1f} mm</b>",
    showarrow=False,
    font=dict(size=15, color="#333333"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="#999999",
    borderwidth=1, borderpad=4
)

# 正负号标注
fig.add_annotation(x=-PLATE_W * 0.85, y=d / 2 + plate_thick / 2,
                   text="<b>+</b>", showarrow=False,
                   font=dict(size=16, color="white"))
fig.add_annotation(x=-PLATE_W * 0.85, y=-d / 2 - plate_thick / 2,
                   text="<b>−</b>", showarrow=False,
                   font=dict(size=16, color="white"))

fig.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(range=[-10, 10], showgrid=False, zeroline=False,
               showticklabels=False, fixedrange=True),
    yaxis=dict(range=[-Y_MAX, Y_MAX], showgrid=False, zeroline=False,
               showticklabels=False, fixedrange=True, scaleanchor="x"),
    plot_bgcolor="white",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================== 图2：C-d 特性曲线（核心） =====================
st.subheader("📈 电容 C 随极板间距 d 的变化特性")

d_arr = np.linspace(1.0, 10.0, 200)                       # mm
C_arr = EPS0 * er * S_m2 / (d_arr * 1e-3) * 1e12          # pF

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=d_arr, y=C_arr, mode="lines", name="C-d 理论曲线",
    line=dict(color="#1f77b4", width=3)
))

# 当前工作点（拖动滑块时红点沿曲线滑动）
fig2.add_trace(go.Scatter(
    x=[d], y=[C_pF], mode="markers+text",
    text=[f"  当前点 d={d:.1f}mm, C={C_pF:.2f}pF"],
    textposition="top right",
    textfont=dict(size=12, color="red"),
    marker=dict(size=15, color="red", symbol="circle",
                line=dict(width=2, color="white")),
    name="当前工作点"
))

# 辅助虚线
fig2.add_shape(type="line", x0=d, x1=d, y0=0, y1=C_pF,
               line=dict(color="red", width=1, dash="dash"))
fig2.add_shape(type="line", x0=0, x1=d, y0=C_pF, y1=C_pF,
               line=dict(color="red", width=1, dash="dash"))

fig2.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="极板间距 d (mm)", gridcolor="#eeeeee"),
    yaxis=dict(title="电容 C (pF)", gridcolor="#eeeeee"),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode="x unified"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ===================== 结论区 =====================
st.subheader("💡 仿真结论")

if mode == "电荷Q恒定":
    st.markdown(
        f"- 当前工作模式下 **Q 恒定**，由 $U = Q/C$ 可知：d 增大 → C 减小 → **U 增大**，"
        f"而场强 $E = \\sigma/\\varepsilon_0\\varepsilon_r$ **保持不变**。\n"
        f"- 当前 C = **{C_pF:.2f} pF**，U = **{U_show:.2f} V**，E = **{E_show:.0f} V/m**。"
    )
else:
    st.markdown(
        f"- 当前工作模式下 **U 恒定**，由 $E = U/d$ 可知：d 增大 → **E 减小**。\n"
        f"- 当前 C = **{C_pF:.2f} pF**，E = **{E_show:.0f} V/m**。"
    )

st.markdown(
    f"- **核心规律**：$C = \\varepsilon_0\\varepsilon_r S/d$，电容 C 与极板间距 d 成**反比**，"
    f"与极板面积 S、相对介电常数 εᵣ 成**正比**。\n"
    f"- **应用价值**：这正是电容式位移传感器的工作原理——被测物体带动极板移动使 d 改变，"
    f"通过测量 C 的变化即可反推出微小位移量，适用于微创手术机器人的高精度位置检测。"
)