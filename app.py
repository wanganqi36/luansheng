import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---------- 页面配置 ----------
st.set_page_config(page_title="平行板电容器数字孪生平台", layout="wide")
st.title("🔬 平行板电容器数字孪生平台")
st.caption("微创手术机器人位移传感器 · 电容式位移测量仿真")

# ---------- 常量 ----------
EPS0 = 8.854e-12          # 真空介电常数 F/m
K_E  = 8.988e9            # 静电力常量

# ---------- 侧边栏：可调参数 ----------
st.sidebar.header("⚙️ 参数调节")
S = st.sidebar.slider("极板正对面积 S (cm²)", 10.0, 500.0, 100.0, 5.0)
d = st.sidebar.slider("极板间距 d (mm)", 0.1, 20.0, 5.0, 0.1)
Q = st.sidebar.slider("极板电荷量 Q (nC)", 1.0, 200.0, 50.0, 1.0)

medium = st.sidebar.selectbox("介质类型", ["真空/空气", "云母", "陶瓷", "聚四氟乙烯"])
eps_r = {"真空/空气": 1.0, "云母": 6.0, "陶瓷": 200.0, "聚四氟乙烯": 2.1}[medium]

mode = st.sidebar.radio("工作模式", ["电荷 Q 恒定（孤立）", "电压 U 恒定（接电源）"])

# ---------- 核心物理公式 ----------
S_m = S * 1e-4            # cm² -> m²
d_m = d * 1e-3            # mm   -> m
Q_c = Q * 1e-9            # nC   -> C

C = eps_r * EPS0 * S_m / d_m          # ★ 核心公式 C = εS/d
sigma = Q_c / S_m                     # 电荷面密度 σ = Q/S
E_field = sigma / (eps_r * EPS0)      # ★ 板间场强 E = σ/ε
U = Q_c / C                           # 电压 U = Q/C
F = Q_c**2 / (2 * eps_r * EPS0 * S_m) # 极板间吸引力

# ---------- 指标卡 ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("电容 C", f"{C*1e12:.2f} pF")
c2.metric("场强 E", f"{E_field:.2f} V/m")
c3.metric("电压 U", f"{U:.3f} V")
c4.metric("面密度 σ", f"{sigma*1e9:.2f} nC/m²")

st.divider()

# ---------- 可视化：电容器剖面图 ----------
st.subheader("📐 电容器实时剖面")
fig = go.Figure()
# 上极板
fig.add_shape(type="rect", x0=0, x1=1, y0=0.6, y1=0.6+0.05, fillcolor="#4e79a7")
# 下极板
fig.add_shape(type="rect", x0=0, x1=1, y0=0.35, y1=0.35+0.05, fillcolor="#e15759")
# 电场线（数量随 σ 变化，方向向下）
n_lines = int(np.clip(S/15, 3, 30))
for x in np.linspace(0.05, 0.95, n_lines):
    fig.add_annotation(arrowhead=2, arrowsize=1.2, x=x, y=0.58,
                       text="", showarrow=True, ax=0, ay=18, arrowcolor="#f2a900")
fig.update_layout(height=320, xaxis=dict(range=[0,1], visible=False),
                  yaxis=dict(range=[0.2,0.8], visible=False),
                  margin=dict(l=10,r=10,t=10,b=10),
                  annotations=[
                    dict(x=1.02, y=0.62, text=f"+Q = {Q:.1f} nC", showarrow=False),
                    dict(x=1.02, y=0.36, text=f"−Q", showarrow=False),
                    dict(x=0.5, y=0.48, text=f"d = {d:.1f} mm", showarrow=False,
                         font=dict(size=14, color="white"))])
st.plotly_chart(fig, use_container_width=True)

# ---------- 核心曲线：C-d 关系 ----------
st.subheader("📈 电容 C 随间距 d 的变化（反比关系）")
d_arr = np.linspace(0.1, 20, 300) * 1e-3
C_arr = eps_r * EPS0 * S_m / d_arr * 1e12   # pF

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=d_arr*1e3, y=C_arr, name="C(d)", line=dict(width=3)))
fig2.add_trace(go.Scatter(x=[d], y=[C*1e12], mode="markers+text",
                          text=[f"当前点<br>d={d:.1f}mm<br>C={C*1e12:.1f}pF"],
                          textposition="top center",
                          marker=dict(size=14, color="red")))
fig2.update_layout(xaxis_title="极板间距 d (mm)", yaxis_title="电容 C (pF)",
                   height=380, margin=dict(l=40,r=20,t=20,b=40))
st.plotly_chart(fig2, use_container_width=True)

# ---------- 传感器灵敏度分析 ----------
st.subheader("🎯 传感器灵敏度分析（位移反推）")
dd = st.slider("施加微小位移 Δd (μm)", 1, 500, 50)
d2 = d_m + dd*1e-6
C2 = eps_r * EPS0 * S_m / d2
dC = (C2 - C) * 1e12
st.write(f"- 位移 Δd = **{dd} μm** 时，电容变化 ΔC = **{dC:.3f} pF**")
st.write(f"- 灵敏度 S_c = ΔC/Δd = **{abs(dC)/(dd*1e-3):.3f} pF/mm**")
st.info("💡 结论：d 越小，同样位移引起的 ΔC 越大，传感器灵敏度越高；"
        "但 d 过小易击穿，需折中选择。")

st.divider()
st.markdown("""
**核心物理公式**
- 电容决定式：$C=\\dfrac{\\varepsilon_r\\varepsilon_0 S}{d}$
- 电荷面密度：$\\sigma=Q/S$
- 板间场强：$E=\\dfrac{\\sigma}{\\varepsilon_0\\varepsilon_r}=\\dfrac{Q}{\\varepsilon_0\\varepsilon_r S}$
- 电压：$U=Q/C$
""")