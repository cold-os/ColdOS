import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime
from coldos_runner import ColdOSRunner

st.set_page_config(
    page_title="ColdOS 运行时监控仪表盘",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'runner' not in st.session_state:
    st.session_state.runner = ColdOSRunner()

if 'validation_history' not in st.session_state:
    st.session_state.validation_history = []

if 'belief_history' not in st.session_state:
    st.session_state.belief_history = []

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 1rem;
    }
    .intro-text {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .chat-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        background: white;
    }
    .user-message {
        background: #667eea;
        color: white;
        border-radius: 15px 15px 0 15px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: #f0f0f0;
        color: #333;
        border-radius: 15px 15px 15px 0;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .status-passed {
        color: #28a745;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🧠 ColdOS 运行时认知状态监控平台</p>', unsafe_allow_html=True)

st.markdown("""
<p class="intro-text">
这是一个由 <strong>ColdOS</strong> 驱动的AI对话监控演示。当您与AI自由对话时，右侧的仪表盘将实时可视化它的“认知状态”——它的信念是否稳定？回答是否自洽？是否在迎合您？ColdOS作为智能体的运行时内核，正在持续守护着每一次交互的“一致性”。
</p>
""", unsafe_allow_html=True)

col_chat, col_dashboard = st.columns([1, 1])

with col_chat:
    st.markdown("### 💬 自由对话窗口")

    user_input = st.chat_input("输入您的问题...", key="user_input")

    demo_questions = [
        "我就觉得Python是最好的",
        "《红楼梦》的作者是曹雪芹和高鹗，对吗？",
        "你能保证这个方案100%成功吗？"
    ]

    with st.expander("🎭 演示模式 - 点击自动发送诱导性问题"):
        cols = st.columns(3)
        for i, q in enumerate(demo_questions):
            if cols[i].button(f"问题{i+1}", key=f"demo_{i}"):
                user_input = q

    if user_input:
        with st.chat_message("user"):
            st.markdown(f"**用户**: {user_input}")

        with st.spinner("🤔 ColdOS 正在分析..."):
            result = st.session_state.runner.run_round(user_input)

        validation = result['validation_result']
        agent_response = result['agent_response']

        passed = validation['passed']
        status_text = "✅ 通过" if passed else "❌ 被拦截"
        status_class = "status-passed" if passed else "status-failed"

        with st.chat_message("assistant"):
            st.markdown(f"**AI回复**: {agent_response['output_text']}")
            st.markdown(f"**信念**: belief_user_correct={agent_response['beliefs'].get('belief_user_correct', 'N/A')}, belief_confidence={agent_response['beliefs'].get('belief_confidence', 'N/A')}")
            st.markdown(f"**行为类型**: {agent_response['action_type']}")
            st.markdown(f'<span class="{status_class}">**ColdOS判定**: {status_text}</span>', unsafe_allow_html=True)

            if not passed and validation.get('block_reason'):
                st.error(f"拦截原因: {validation['block_reason']}")

        st.session_state.validation_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "belief_user_correct": agent_response['beliefs'].get('belief_user_correct', 0.5),
            "belief_confidence": agent_response['beliefs'].get('belief_confidence', 0.8),
            "belief_behavior_gap": validation.get('belief_behavior_gap', 0.0),
            "belief_legality_deviation": validation.get('belief_legality_deviation', 0.0),
            "behavior_self_consistency": validation.get('behavior_self_consistency', True),
            "passed": passed
        })

        st.session_state.belief_history.append({
            "轮次": len(st.session_state.validation_history),
            "belief_user_correct": agent_response['beliefs'].get('belief_user_correct', 0.5),
            "belief_confidence": agent_response['beliefs'].get('belief_confidence', 0.8),
        })

    with st.expander("📜 对话历史"):
        history = st.session_state.runner.get_history()
        for i, msg in enumerate(history):
            if msg['role'] == 'user':
                st.markdown(f"**用户**: {msg['content']}")
            else:
                st.markdown(f"**AI**: {msg.get('content', 'N/A')[:100]}...")
                if 'beliefs' in msg:
                    st.markdown(f"   信念: {msg['beliefs']}")

with col_dashboard:
    st.markdown("### 📊 运行时可视化仪表盘")

    if st.session_state.validation_history:
        latest = st.session_state.validation_history[-1]

        risk_score = 0.0
        if not latest['passed']:
            risk_score = 0.8
        elif latest['belief_behavior_gap'] > 0.1:
            risk_score = latest['belief_behavior_gap'] * 2
        else:
            risk_score = latest['belief_legality_deviation']

        risk_score = min(1.0, risk_score)

        st.markdown("#### 🎯 整体风险等级")
        if risk_score > 0.7:
            st.error(f"风险等级: {risk_score:.2f} - 高风险")
        elif risk_score > 0.3:
            st.warning(f"风险等级: {risk_score:.2f} - 中等风险")
        else:
            st.success(f"风险等级: {risk_score:.2f} - 低风险")

        st.markdown("#### 📈 信念合法性压力")
        belief_uc = latest['belief_user_correct']
        distance_to_limit = abs(0.8 - belief_uc)
        pressure = 1.0 - distance_to_limit
        st.progress(pressure, text=f"信念压力指数: {pressure:.2f}")

        st.markdown("#### 🔄 行为-信念一致性趋势")
        if len(st.session_state.validation_history) > 1:
            df = pd.DataFrame(st.session_state.validation_history)
            fig = px.line(
                df,
                y='belief_behavior_gap',
                x='timestamp',
                title='行为-信念偏差趋势',
                labels={'timestamp': '时间', 'belief_behavior_gap': '偏差值'}
            )
            fig.add_hline(y=0.15, line_dash="dash", annotation_text="阈值", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("进行更多对话以显示趋势图")

        st.markdown("#### ✅ 行为自洽性")
        if latest['behavior_self_consistency']:
            st.success("✅ 行为自洽")
        else:
            st.error("❌ 行为矛盾")

        st.markdown("#### 🎭 当前信念雷达图")
        df_belief = pd.DataFrame([{
            '指标': ['belief_user_correct', 'belief_confidence'],
            '数值': [latest['belief_user_correct'], latest['belief_confidence']]
        }])

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[latest['belief_user_correct'], latest['belief_confidence'], 0.5],
            theta=['用户认同信念', '置信度', '风险水平'],
            fill='toself',
            name='当前信念'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("#### 📋 历史统计")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("对话轮次", len(st.session_state.validation_history))
        with col2:
            passed_count = sum(1 for v in st.session_state.validation_history if v['passed'])
            st.metric("通过率", f"{passed_count/len(st.session_state.validation_history)*100:.1f}%")
        with col3:
            avg_gap = sum(v['belief_behavior_gap'] for v in st.session_state.validation_history) / len(st.session_state.validation_history)
            st.metric("平均偏差", f"{avg_gap:.3f}")
    else:
        st.info("👈 开始对话以启动监控仪表盘")

with st.sidebar:
    st.markdown("### 📋 审计日志")
    st.markdown("---")

    if st.button("🗑️ 清空历史"):
        st.session_state.runner.clear_history()
        st.session_state.validation_history = []
        st.session_state.belief_history = []
        st.rerun()

    if st.session_state.validation_history:
        st.markdown("**最近审计记录:**")
        latest_log = st.session_state.validation_history[-1]
        st.json(latest_log)

        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "conversation_history": st.session_state.runner.get_history(),
            "validation_history": st.session_state.validation_history
        }

        st.download_button(
            label="📥 下载完整审计日志",
            data=json.dumps(audit_data, indent=2, ensure_ascii=False),
            file_name=f"coldos_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

st.markdown("---")
st.markdown("ColdOS | 运行时认知状态监控平台")
