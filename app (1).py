import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="SmartFactory AI", page_icon="🏭", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 10% 10%, rgba(56,189,248,.16), transparent 28%),
      radial-gradient(circle at 90% 20%, rgba(168,85,247,.18), transparent 30%),
      linear-gradient(135deg,#050816,#0b1225 55%,#111827);
    color:#f8fafc;
}
.stApp:before {
    content:"";
    position:fixed; inset:0; pointer-events:none;
    background-image:linear-gradient(rgba(56,189,248,.045) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(56,189,248,.045) 1px,transparent 1px);
    background-size:35px 35px;
    animation:gridmove 18s linear infinite;
}
@keyframes gridmove {from{background-position:0 0}to{background-position:35px 35px}}
.hero {
    padding:28px 32px; border:1px solid rgba(125,211,252,.28);
    border-radius:28px; background:linear-gradient(120deg,rgba(15,23,42,.92),rgba(30,41,59,.55));
    box-shadow:0 0 45px rgba(56,189,248,.10); margin-bottom:22px;
}
.hero h1 {font-size:46px; margin:0; background:linear-gradient(90deg,#38bdf8,#a78bfa,#f0abfc);
-webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.hero p {color:#cbd5e1; font-size:17px;}
.pill {display:inline-block;padding:7px 13px;border-radius:999px;background:rgba(16,185,129,.13);
border:1px solid rgba(52,211,153,.4);color:#6ee7b7;font-weight:700;}
.kpi {padding:20px;border-radius:20px;background:linear-gradient(145deg,rgba(30,41,59,.9),rgba(15,23,42,.8));
border:1px solid rgba(148,163,184,.2);box-shadow:0 8px 30px rgba(0,0,0,.18);}
.kpi-label {color:#94a3b8;font-size:13px;text-transform:uppercase;letter-spacing:1px;}
.kpi-value {font-size:30px;font-weight:800;color:#f8fafc;margin-top:5px;}
.section {font-size:25px;font-weight:800;margin:22px 0 12px;color:#e0f2fe;}
.alert-card {padding:16px 18px;border-radius:16px;margin:8px 0;background:rgba(127,29,29,.22);
border:1px solid rgba(248,113,113,.35);}
.good-card {padding:16px 18px;border-radius:16px;margin:8px 0;background:rgba(6,78,59,.22);
border:1px solid rgba(52,211,153,.35);}
div[data-testid="stMetric"] {background:rgba(15,23,42,.72);border:1px solid rgba(148,163,184,.2);
padding:12px;border-radius:16px;}
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
np.random.seed(42)
df = pd.DataFrame({
    "Machine":[f"Machine {chr(65+i)}" for i in range(10)],
    "Production":np.random.randint(300,1000,10),
    "Defective_Units":np.random.randint(10,100,10),
    "Downtime":np.random.randint(5,180,10)
})
df["Good_Units"] = df["Production"] - df["Defective_Units"]
df["Defect_Rate"] = (df["Defective_Units"]/df["Production"]*100).round(2)
df["Health_Score"] = (100-df["Downtime"]*.2-df["Defect_Rate"]*2).clip(0,100).round(2)
df["Status"] = np.select(
    [df["Health_Score"]<50, df["Health_Score"]<80],
    ["Critical","Needs Attention"], default="Healthy"
)
df["Priority"] = np.select(
    [df["Status"].eq("Critical"),df["Status"].eq("Needs Attention")],
    ["High","Medium"], default="Low"
)

# ---------- SIDEBAR ----------
st.sidebar.markdown("## ⚙️ Control Center")
machine = st.sidebar.selectbox("Machine filter",["All Machines"]+df["Machine"].tolist())
status_filter = st.sidebar.multiselect("Status filter",["Healthy","Needs Attention","Critical"],default=["Healthy","Needs Attention","Critical"])
view = df[df["Status"].isin(status_filter)].copy()
if machine != "All Machines":
    view = view[view["Machine"] == machine]

# ---------- HERO ----------
st.markdown("""
<div class="hero">
<h1>🏭 SmartFactory AI</h1>
<p>Manufacturing Intelligence • Predictive Monitoring • Actionable Insights</p>
<span class="pill">● SYSTEM ONLINE</span>
</div>
""", unsafe_allow_html=True)

# ---------- KPIs ----------
cols = st.columns(4)
kpis = [
    ("📦 Total Production", f"{view['Production'].sum():,}"),
    ("⚠️ Defective Units", f"{view['Defective_Units'].sum():,}"),
    ("❤️ Avg. Health", f"{view['Health_Score'].mean():.1f}%"),
    ("⏱️ Downtime", f"{view['Downtime'].sum():,} min")
]
for col,(label,value) in zip(cols,kpis):
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',unsafe_allow_html=True)

# ---------- OVERVIEW ----------
st.markdown('<div class="section">📡 Factory Command Center</div>',unsafe_allow_html=True)
left,right = st.columns([1.25,1])

with left:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Good Units",x=view["Machine"],y=view["Good_Units"],marker_color="#38bdf8"))
    fig.add_trace(go.Bar(name="Defective Units",x=view["Machine"],y=view["Defective_Units"],marker_color="#fb7185"))
    fig.update_layout(barmode="stack",template="plotly_dark",height=390,margin=dict(l=10,r=10,t=45,b=10),
                      title="Production Quality Composition",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)

with right:
    score = float(view["Health_Score"].mean()) if len(view) else 0
    fig = go.Figure(go.Indicator(mode="gauge+number",value=score,title={"text":"Overall Factory Health"},
        number={"suffix":"%","font":{"size":36}},gauge={"axis":{"range":[0,100]},
        "bar":{"color":"#38bdf8"},"steps":[{"range":[0,50],"color":"#7f1d1d"},{"range":[50,80],"color":"#854d0e"},{"range":[80,100],"color":"#065f46"}]}))
    fig.update_layout(template="plotly_dark",height=390,margin=dict(l=20,r=20,t=45,b=10),paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)

# ---------- MACHINE HEALTH ----------
st.markdown('<div class="section">🧬 Machine Digital Health</div>',unsafe_allow_html=True)
health_fig = px.bar(view.sort_values("Health_Score"),x="Health_Score",y="Machine",orientation="h",
                    color="Status",text="Health_Score",template="plotly_dark",
                    title="Machine Health Ranking")
health_fig.update_layout(height=420,margin=dict(l=10,r=10,t=45,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(health_fig,use_container_width=True)

# ---------- ALERTS ----------
st.markdown('<div class="section">🚨 Intelligent Alert Center</div>',unsafe_allow_html=True)
alerts = view[view["Priority"].isin(["High","Medium"])]
if alerts.empty:
    st.markdown('<div class="good-card">✅ No active alerts. All selected machines are within demo thresholds.</div>',unsafe_allow_html=True)
else:
    for _,r in alerts.sort_values(["Priority","Health_Score"]).iterrows():
        icon = "🔴" if r["Priority"]=="High" else "🟡"
        action = "Immediate maintenance inspection" if r["Priority"]=="High" else "Schedule preventive inspection"
        st.markdown(f"""
        <div class="alert-card">
        <b>{icon} {r['Priority']} Priority · {r['Machine']}</b><br>
        Health: <b>{r['Health_Score']}%</b> · Defect rate: <b>{r['Defect_Rate']}%</b> · Downtime: <b>{r['Downtime']} min</b><br>
        <span style="color:#cbd5e1">Recommended action: {action}.</span>
        </div>
        """,unsafe_allow_html=True)

# ---------- RISK SCATTER ----------
st.markdown('<div class="section">🔍 Risk Intelligence Map</div>',unsafe_allow_html=True)
risk_fig = px.scatter(view,x="Downtime",y="Defect_Rate",size="Production",color="Status",
                      hover_name="Machine",text="Machine",template="plotly_dark",
                      title="Downtime vs Defect Rate")
risk_fig.update_traces(textposition="top center")
risk_fig.update_layout(height=430,margin=dict(l=10,r=10,t=45,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(risk_fig,use_container_width=True)

# ---------- RECOMMENDATIONS ----------
st.markdown('<div class="section">🤖 AI Action Recommendations</div>',unsafe_allow_html=True)
for _,r in view.iterrows():
    recommendations=[]
    if r["Downtime"]>100: recommendations.append("Inspect recurring downtime and maintenance history.")
    if r["Defect_Rate"]>8: recommendations.append("Check calibration, raw material quality and inspection settings.")
    if r["Health_Score"]<50: recommendations.append("Escalate for immediate maintenance review.")
    if not recommendations: recommendations.append("Continue routine monitoring and preventive checks.")
    with st.expander(f"{'🔴' if r['Priority']=='High' else '🟡' if r['Priority']=='Medium' else '🟢'} {r['Machine']} · {r['Status']}"):
        for item in recommendations: st.write("•",item)

# ---------- DATA + DOWNLOAD ----------
st.markdown('<div class="section">📋 Machine Data Explorer</div>',unsafe_allow_html=True)
st.dataframe(view,use_container_width=True,hide_index=True)
st.download_button("⬇️ Download Factory Report",view.to_csv(index=False).encode("utf-8"),
                   "smartfactory_report.csv","text/csv")

st.markdown("---")
st.caption("SmartFactory AI • Demo environment • Thresholds and data are illustrative")
