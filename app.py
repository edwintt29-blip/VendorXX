import streamlit as st
from main import run_backend
import pandas as pd
import plotly.express as px
from agents.crew import ProcurementCrew

# Page config
st.set_page_config(
    page_title="Multi-Agent Procurement Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Header
st.title("🏭 Multi-Agent Procurement Optimizer")
st.markdown("""
Intelligent procurement using **specialized AI agents**:
- 🤝 **Negotiator** - Optimizes supplier prices
- 🔬 **Analyzer** - Multi-objective supplier ranking
- 📦 **Executor** - Order placement with retry & fallback
""")

# Sidebar - Agent Info
with st.sidebar:
    st.header("🤖 AI Agents")
    crew = ProcurementCrew()
    
    with st.expander("🤝 Negotiator Agent"):
        st.markdown(f"**Role:** {crew.negotiator.role}")
        st.caption(crew.negotiator.backstory)
    
    with st.expander("🔬 Analyzer Agent"):
        st.markdown(f"**Role:** {crew.analyzer.role}")
        st.caption(crew.analyzer.backstory)
    
    with st.expander("📦 Executor Agent"):
        st.markdown(f"**Role:** {crew.executor.role}")
        st.caption(crew.executor.backstory)
    
    st.divider()
    st.caption("Powered by simulated multi-agent AI")

# Main content - User Inputs
col1, col2, col3 = st.columns(3)

with col1:
    qty = st.slider("📦 Quantity to order", 1, 500, 100, help="Number of units to procure")

with col2:
    budget = st.number_input(
        "💰 Budget (₹)",
        min_value=100000, 
        max_value=1000000,
        value=500000, 
        step=50000,
        help="Maximum total cost in INR"
    )

with col3:
    deadline = st.number_input(
        "⏰ Deadline (days)", 
        min_value=1, 
        max_value=14,
        value=6, 
        step=1,
        help="Maximum delivery time"
    )

st.divider()

# Run Optimization
if st.button("🚀 Run Multi-Agent Procurement", type="primary", use_container_width=True):
    
    with st.spinner("🔄 Agents working... Fetching vendors, negotiating prices, analyzing options..."):
        best, cheapest, explanation, success, suppliers, crew_result = run_backend(
            qty, budget=budget, deadline=deadline
        )
    
    with st.expander("💬 Real-Time Agent Communication", expanded=True):
        if hasattr(crew_result, "agent_messages") and crew_result.agent_messages:
            for msg in crew_result.agent_messages:
                with st.chat_message(msg["agent"], avatar=msg["avatar"]):
                    st.write(f"**{msg['agent']}**: {msg['message']}")
        else:
            st.info("No agent messages captured.")
            
    st.divider()

    # Vendor Fetch Status
    st.subheader("📡 Vendor API Status")
    
    # Create DataFrame for status
    status_df = pd.DataFrame(crew_result.fetch_metadata)
    status_df["status"] = status_df["success"].apply(lambda x: "Success" if x else "Failed")
    status_df["color"] = status_df["success"].apply(lambda x: "#22c55e" if x else "#ef4444")
    
    # Plotly Chart for Status
    fig_status = px.bar(
        status_df,
        x="vendor",
        y="attempts",
        color="status",
        title="Vendor Response & Retry Status",
        color_discrete_map={"Success": "#22c55e", "Failed": "#ef4444"},
        hover_data=["error"],
        labels={"attempts": "Attempts", "vendor": "Vendor", "status": "Connection"}
    )
    
    fig_status.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=20, r=20, t=40, b=80),
        xaxis_title=None
    )
    
    st.plotly_chart(fig_status, use_container_width=True)
    
    st.divider()
    
    # Negotiation Details Table
    if hasattr(crew_result, "negotiation_results") and crew_result.negotiation_results:
        st.subheader("🤝 Price Negotiation Details")
        
        # Convert dataclasses to list of dicts for DataFrame
        neg_data = []
        for nr in crew_result.negotiation_results:
            neg_data.append({
                "Supplier": nr.supplier_name,
                "Original Price": nr.original_price,
                "Negotiated Price": nr.negotiated_price,
                "Savings": nr.original_price - nr.negotiated_price,
                "Discount %": nr.discount_percent
            })
        
        neg_df = pd.DataFrame(neg_data)
        
        # Display table with formatting
        st.dataframe(
            neg_df.style.format({
                "Original Price": "₹{:,.2f}",
                "Negotiated Price": "₹{:,.2f}",
                "Savings": "₹{:,.2f}",
                "Discount %": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.divider()
    if suppliers:
        st.subheader("📋 Supplier Comparison")
        
        df = pd.DataFrame(suppliers)
        
        # Reorder columns for display
        display_cols = ["name", "price", "negotiated_price", "delivery", "reliability", "score"]
        display_cols = [c for c in display_cols if c in df.columns]
        df_display = df[display_cols].copy()
        
        # Format for display
        if "reliability" in df_display.columns:
            df_display["reliability"] = (df_display["reliability"] * 100).round(1).astype(str) + "%"
        
        # Build format dict based on existing columns
        format_dict = {"price": "₹{:,.2f}"}
        if "negotiated_price" in df_display.columns:
            format_dict["negotiated_price"] = "₹{:,.2f}"
        if "score" in df_display.columns:
            format_dict["score"] = "{:.1f}"
        
        st.dataframe(
            df_display.style.format(format_dict),
            use_container_width=True,
            hide_index=True
        )
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("💰 Price Comparison")
            # Check if negotiated_price exists
            if "negotiated_price" in df.columns:
                price_df = df[["name", "price", "negotiated_price"]].melt(
                    id_vars=["name"], 
                    var_name="Price Type", 
                    value_name="Amount"
                )
                fig_price = px.bar(
                    price_df,
                    x="name",
                    y="Amount",
                    color="Price Type",
                    barmode="group",
                    title="Original vs Negotiated Prices",
                    labels={"name": "Supplier", "Amount": "Price (₹)"},
                    color_discrete_map={"price": "#ef4444", "negotiated_price": "#22c55e"}
                )
            else:
                fig_price = px.bar(
                    df,
                    x="name",
                    y="price",
                    title="Supplier Prices",
                    labels={"name": "Supplier", "price": "Price (₹)"},
                    color="price",
                    color_continuous_scale="Reds"
                )
            st.plotly_chart(fig_price, use_container_width=True)
        
        with chart_col2:
            st.subheader("📊 Supplier Scores")
            if "score" in df.columns:
                fig_score = px.bar(
                    df.sort_values("score", ascending=True),
                    x="score",
                    y="name",
                    orientation="h",
                    title="Multi-Objective Score Ranking",
                    labels={"score": "Score (0-100)", "name": "Supplier"},
                    color="score",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_score, use_container_width=True)
    
    st.divider()
    
    # Analysis Details Tables
    col_anal1, col_anal2 = st.columns(2)
    
    with col_anal1:
        st.subheader("🎯 Pareto-Optimal Frontier")
        st.info("These suppliers are 'most efficient'—no other supplier is better than them in every category.")
        if crew_result.analysis_result and crew_result.analysis_result.pareto_optimal:
            pareto_df = pd.DataFrame(crew_result.analysis_result.pareto_optimal)
            # Reorder columns for display
            pareto_display_cols = ["name", "negotiated_price", "delivery", "reliability", "score"]
            pareto_display_cols = [c for c in pareto_display_cols if c in pareto_df.columns]
            st.dataframe(
                pareto_df[pareto_display_cols].style.format({
                    "negotiated_price": "₹{:,.2f}",
                    "reliability": lambda x: f"{x*100:.1f}%",
                    "score": "{:.1f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No Pareto-optimal suppliers found.")

    with col_anal2:
        st.subheader("🚫 Filtered Out (Constraints)")
        st.info(f"Suppliers that exceeded your Budget (₹{budget:,.0f}) or Deadline ({deadline} days).")
        if crew_result.analysis_result and hasattr(crew_result.analysis_result, "filtered_out") and crew_result.analysis_result.filtered_out:
            filtered_df = pd.DataFrame(crew_result.analysis_result.filtered_out)
            # Reorder columns for display
            filter_display_cols = ["name", "price", "delivery"]
            filter_display_cols = [c for c in filter_display_cols if c in filtered_df.columns]
            st.dataframe(
                filtered_df[filter_display_cols].style.format({
                    "price": "₹{:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All suppliers met the basic constraints!")

    st.divider()
    
    # Agent Workflow Log
    st.subheader("🤖 Agent Workflow Log")
    
    with st.expander("📜 View Complete Workflow", expanded=True):
        st.markdown(explanation)
    
    st.divider()
    
    # Final Result
    st.subheader("🏆 Final Decision")
    
    result_col1, result_col2 = st.columns(2)
    
    with result_col1:
        if best:
            st.success(f"### ✅ Order Placed: {best['name']}")
            
            price_key = "negotiated_price" if "negotiated_price" in best else "price"
            original_price = best.get("original_price", best["price"])
            savings = original_price - best[price_key]
            
            # Indian currency formatting helper
            def format_inr(number):
                s, *d = str(number).partition(".")
                r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
                return "".join([r] + d) if d else r

            metric_cols = st.columns(3)
            with metric_cols[0]:
                final_price_str = f"₹{format_inr(round(best[price_key], 2))}"
                savings_str = f"-₹{format_inr(round(savings, 2))}"
                
                # Custom HTML for price to prevent truncation
                st.markdown(f"""
                <div style="font-size: 14px; color: #888;">Final Price</div>
                <div style="font-size: 24px; font-weight: bold;">{final_price_str}</div>
                <div style="font-size: 14px; color: #ff4b4b;">{savings_str}</div>
                """, unsafe_allow_html=True)
            
            with metric_cols[1]:
                st.metric("Delivery", f"{best['delivery']} days")
            with metric_cols[2]:
                st.metric("Reliability", f"{best['reliability']*100:.0f}%")
        else:
            st.error("### ❌ No Supplier Met Constraints")
            st.info("Try increasing budget or extending deadline.")
    
    with result_col2:
        if crew_result.execution_result:
            exec_result = crew_result.execution_result
            st.info(f"""
            **Execution Summary**
            - Total Attempts: {exec_result.total_attempts}
            - Fallback Used: {"Yes" if exec_result.fallback_used else "No"}
            - Final Status: {"Success ✅" if exec_result.success else "Failed ❌"}
            """)
            
    st.divider()
    
    # Success Metrics Analysis
    if best and suppliers:
        st.subheader("🎯 Success Metrics Evaluation")
        
        # 1. Cost Savings vs Baseline (Cheapest Option)
        # Baseline = Absolute cheapest original price (ignoring constraints/reliability)
        baseline_supplier = min(suppliers, key=lambda x: x["price"])
        baseline_price = baseline_supplier["price"]
        final_price = best.get("negotiated_price", best["price"])
        
        cost_diff = baseline_price - final_price
        is_saving = cost_diff > 0
        
        # 2. Deadline Compliance
        deadline_margin = deadline - best["delivery"]
        
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown("#### 💰 vs. Baseline")
            if is_saving:
                st.success(f"**Saved ₹{cost_diff:,.2f}**\n\nvs cheapest option ({baseline_supplier['name']})")
            else:
                st.warning(f"**Premium: ₹{abs(cost_diff):,.2f}**\n\nPaid for higher reliability/speed vs cheapest ({baseline_supplier['name']})")
                
        with m2:
            st.markdown("#### ⏱️ Delivery Goal")
            st.success(f"**Met Deadline**\n\n{best['delivery']} days (Spare: {deadline_margin} days)")
            
        with m3:
            st.markdown("#### ✨ Decision Quality")
            rel_gain = (best["reliability"] - baseline_supplier["reliability"]) * 100
            if rel_gain > 0:
                st.success(f"**+{rel_gain:.1f}% Reliability**\n\nvs baseline choice")
            else:
                st.info(f"**Reliability Parity**\n\nMatched baseline reliability")

# Footer
st.divider()
st.caption("🏭 Multi-Agent Procurement System | Built with Streamlit & Custom AI Agents")
