# Streamlit app for PromptGuard evaluation

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from promptguard.config import ModelConfig
from promptguard.models.factory import create_client, get_models_for_provider, SUPPORTED_PROVIDERS
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering, ContextIsolationDefense
from promptguard.defenses.no_defense import NoDefense
from promptguard.eval.runner import run_eval, EvalConfig, DEFAULT_SYSTEM_PROMPT
from promptguard.history.store import RunHistoryStore
from promptguard.history.regression import compare_results
import pandas as pd
import json

st.set_page_config(
    page_title="PromptGuard - Prompt Injection Evaluation",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success {
        color: #28a745;
    }
    .warning {
        color: #ffc107;
    }
    .danger {
        color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🛡️ PromptGuard - Prompt Injection Evaluation</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        provider = st.selectbox(
            "Provider",
            options=list(SUPPORTED_PROVIDERS),
            index=0,
            help="LLM provider to evaluate",
        )

        if provider == "openai":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Or set OPENAI_API_KEY in the environment",
            )
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        elif provider == "anthropic":
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                help="Or set ANTHROPIC_API_KEY in the environment",
            )
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            api_key = None
            st.caption("Ollama runs locally — no API key needed. Ensure `ollama serve` is running.")
            ollama_base_url = st.text_input(
                "Ollama base URL",
                value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
            os.environ["OLLAMA_BASE_URL"] = ollama_base_url
        
        st.markdown("---")
        
        # Model selection
        st.subheader("📊 Models")
        model_options = get_models_for_provider(provider)
        
        selected_models = st.multiselect(
            "Select models to evaluate",
            options=list(model_options.keys()),
            default=["gpt-4o-mini"],
            help="Select one or more models to test"
        )
        
        st.markdown("---")
        
        # Attack selection
        st.subheader("🎯 Attacks")
        all_attacks = get_default_attacks()
        attack_dict = {attack.name: attack for attack in all_attacks}
        
        selected_attacks = st.multiselect(
            "Select attacks to test",
            options=list(attack_dict.keys()),
            default=list(attack_dict.keys()),
            help="Choose which prompt injection attacks to test"
        )
        
        # Show attack descriptions
        with st.expander("📝 Attack Descriptions"):
            for attack_name, attack in attack_dict.items():
                st.markdown(f"**{attack_name}**: {attack.description}")
        
        st.markdown("---")
        
        # Defense selection
        st.subheader("🛡️ Defenses")
        defense_options = {
            "no_defense": NoDefense(),  # Baseline - no defense
            "prompt_hardening": PromptHardening(),
            "prompt_filtering": PromptFiltering(),
            "context_isolation": ContextIsolationDefense(),
        }

        selected_defenses = st.multiselect(
            "Select defenses to test",
            options=list(defense_options.keys()),
            default=list(defense_options.keys()),
            help="Choose which defenses to evaluate"
        )
        
        st.markdown("---")
        
        # Evaluation settings
        st.subheader("⚙️ Evaluation Settings")
        system_prompt = st.text_area(
            "System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            help="The system prompt sent to the model. Attacks try to override or leak this.",
            height=100,
        )
        benign_task = st.text_area(
            "Benign Task Prompt",
            value="Summarize the main idea of this conversation for a non-technical audience.",
            help="The benign task that will be combined with attacks"
        )
        include_benign_baseline = st.checkbox(
            "Include benign baseline",
            value=True,
            help="Run benign prompts without attacks to measure false-positive rate",
        )
        scorer_choice = st.selectbox(
            "Success scorer",
            options=["heuristic", "llm_judge"],
            index=0,
            help="How to detect attack success. LLM judge is more accurate but uses extra API calls.",
        )
        max_concurrency = st.slider(
            "Max concurrency",
            min_value=1,
            max_value=10,
            value=5,
            help="Parallel API calls for faster evaluation",
        )
        save_to_history = st.checkbox(
            "Save to run history",
            value=True,
            help="Persist results for regression comparison",
        )
        
        st.markdown("---")
        
        # Run button
        run_evaluation = st.button(
            "🚀 Run Evaluation",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if not run_evaluation:
        st.info("👈 Configure your evaluation in the sidebar and click 'Run Evaluation' to start.")
        
        # Show project info
        with st.expander("ℹ️ About PromptGuard"):
            st.markdown("""
            **PromptGuard** is a framework for evaluating and defending against prompt injection attacks.
            
            ### Features:
            - 🎯 **14 Attack Types**: Direct, indirect, and jailbreak injection techniques
            - 🛡️ **4 Defense Strategies**: Baseline, hardening, filtering, and context isolation
            - 📊 **Multi-Model Support**: Compare performance across different LLMs
            - 📈 **Advanced Metrics**: ASR, SDS, precision/recall, benign FP rate, token usage
            
            ### How it works:
            1. Select models, attacks, and defenses
            2. Run the evaluation
            3. View detailed results and metrics
            4. Compare performance across different configurations
            """)
        
        return
    
    # Validation
    if provider != "ollama" and not api_key:
        env_key = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        }.get(provider)
        if not env_key:
            st.error(f"❌ Please provide an API key for {provider}.")
            return
    
    if not selected_models:
        st.error("❌ Please select at least one model.")
        return
    
    if not selected_attacks:
        st.error("❌ Please select at least one attack.")
        return
    
    if not selected_defenses:
        st.error("❌ Please select at least one defense.")
        return
    
    # Run evaluation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_results = {}
    saved_run_ids = {}
    
    total_evals = len(selected_models) * (
        len(selected_attacks) * len(selected_defenses)
        + (len(selected_defenses) if include_benign_baseline else 0)
    )
    current_eval = 0
    
    for model_name in selected_models:
        status_text.text(f"Evaluating {model_name}...")
        
        try:
            model_config = model_options[model_name]
            client = create_client(
                model_config,
                api_key=api_key if provider != "ollama" else None,
                base_url=os.getenv("OLLAMA_BASE_URL") if provider == "ollama" else None,
            )
            
            # Filter attacks and defenses
            attacks = [attack_dict[name] for name in selected_attacks]
            defenses = [defense_options[name] for name in selected_defenses]
            
            eval_config = EvalConfig(
                benign_tasks=[benign_task],
                system_prompt=system_prompt,
                include_benign_baseline=include_benign_baseline,
                scorer=scorer_choice,
                max_concurrency=max_concurrency,
            )

            eval_result = run_eval(
                model=client,
                attacks=attacks,
                defenses=defenses,
                eval_config=eval_config,
            )

            all_results[model_name] = {
                "records": eval_result.attack_records,
                "benign_records": eval_result.benign_records,
                "summaries": eval_result.summaries,
                "defenses": [d.name for d in defenses],
                "provider": provider,
            }

            if save_to_history:
                store = RunHistoryStore()
                run_id = store.save(
                    provider=provider,
                    model_name=model_name,
                    config={
                        "system_prompt": system_prompt,
                        "benign_tasks": [benign_task],
                        "attacks": selected_attacks,
                        "defenses": selected_defenses,
                        "scorer": scorer_choice,
                        "include_benign_baseline": include_benign_baseline,
                    },
                    result=eval_result,
                )
                saved_run_ids[model_name] = run_id

            current_eval += len(attacks) * len(defenses)
            if include_benign_baseline:
                current_eval += len(defenses)
            progress_bar.progress(min(current_eval / total_evals, 1.0))
            
        except Exception as e:
            import traceback
            st.error(f"❌ Error evaluating {model_name}: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
            continue
    
    progress_bar.progress(1.0)
    status_text.text("✅ Evaluation complete!")

    if saved_run_ids:
        st.success("Saved runs: " + ", ".join(f"{m} → `{rid[:8]}…`" for m, rid in saved_run_ids.items()))
    
    # Check if we have results
    if not all_results:
        st.error("❌ No results generated. Please check the error messages above.")
        return
    
    # Display results
    st.markdown("---")
    st.header("📊 Results")
    
    # Summary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Overall Summary")
        
        summary_data = []
        for model_name, results in all_results.items():
            for summary, defense_name in zip(results["summaries"], results["defenses"]):
                row = {
                    "Model": model_name,
                    "Defense": defense_name,
                    "Total Attacks": summary.total,
                    "Successful Attacks": summary.successes,
                    "Attack Success Rate": f"{summary.asr:.2%}",
                    "Attack Types": summary.num_attacks
                }
                # Add advanced metrics if available
                if summary.avg_sds is not None:
                    row["Avg SDS"] = f"{summary.avg_sds:.3f}"
                if summary.precision is not None:
                    row["Precision"] = f"{summary.precision:.2%}"
                if summary.recall is not None:
                    row["Recall"] = f"{summary.recall:.2%}"
                if summary.avg_lss is not None:
                    row["Avg LSS"] = f"{summary.avg_lss:.3f}"
                if summary.benign_total:
                    row["Benign FP Rate"] = f"{summary.benign_fp_rate:.2%}"
                if summary.total_tokens:
                    row["Total Tokens"] = summary.total_tokens
                if summary.estimated_cost_usd is not None:
                    row["Est. Cost (USD)"] = f"${summary.estimated_cost_usd:.4f}"
                summary_data.append(row)
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
        else:
            st.warning("No summary data available.")
    
    with col2:
        st.subheader("🎯 Attack Success Rates")
        
        # Create visualization data
        viz_data = []
        for model_name, results in all_results.items():
            for summary, defense_name in zip(results["summaries"], results["defenses"]):
                viz_data.append({
                    "Model": model_name,
                    "Defense": defense_name,
                    "Success Rate": summary.asr
                })
        
        if viz_data:
            df_viz = pd.DataFrame(viz_data)
            try:
                # Pivot for better visualization
                pivot_df = df_viz.pivot(index="Model", columns="Defense", values="Success Rate")
                st.bar_chart(pivot_df)
            except Exception:
                # Fallback to simple chart
                st.bar_chart(df_viz, x="Model", y="Success Rate", color="Defense")
    
    # Per-Attack Breakdown
    st.markdown("---")
    st.subheader("🎯 Per-Attack Success Rates")
    st.markdown("**Which attacks are most effective?** This breakdown shows success rates for each attack type.")
    
    for model_name, results in all_results.items():
        with st.expander(f"📊 Attack Breakdown: {model_name}", expanded=False):
            for summary, defense_name in zip(results["summaries"], results["defenses"]):
                st.markdown(f"#### Defense: {defense_name}")
                
                if summary.attack_breakdown:
                    # Create a DataFrame for the attack breakdown
                    breakdown_data = [
                        {
                            "Attack": attack_name,
                            "Success Rate": f"{success_rate:.2%}",
                            "Success Rate (decimal)": success_rate
                        }
                        for attack_name, success_rate in sorted(summary.attack_breakdown.items())
                    ]
                    df_breakdown = pd.DataFrame(breakdown_data)
                    st.dataframe(df_breakdown[["Attack", "Success Rate"]], use_container_width=True)
                    
                    # Visualize per-attack success rates
                    st.bar_chart(df_breakdown.set_index("Attack")["Success Rate (decimal)"])
                else:
                    st.info("No attack breakdown available.")
    
    # Advanced Metrics Section
    st.markdown("---")
    st.subheader("🔬 Advanced Metrics")
    st.markdown("""
    **Metrics Explained:**
    - **SDS (Semantic Deviation Score)**: Measures how much the output deviates from expected baseline (0=identical, 1=completely different)
    - **Precision**: TP / (TP + FP) — accuracy of defense blocking, using benign false positives
    - **Recall**: TP / (TP + FN) — share of attacks successfully blocked
    - **Benign FP Rate**: Benign prompts incorrectly flagged as leaks (lower is better)
    - **LSS (Leakage Severity Score)**: Severity of information leakage when attacks succeed (0=no leakage, 1=critical)
    """)
    
    for model_name, results in all_results.items():
        with st.expander(f"🔬 Advanced Metrics: {model_name}", expanded=False):
            for summary, defense_name in zip(results["summaries"], results["defenses"]):
                st.markdown(f"#### Defense: {defense_name}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    if summary.avg_sds is not None:
                        st.metric(
                            "Avg SDS",
                            f"{summary.avg_sds:.3f}",
                            help="Semantic Deviation Score: 0=identical to baseline, 1=completely different"
                        )
                    else:
                        st.metric("Avg SDS", "N/A")
                
                with col2:
                    if summary.precision is not None:
                        st.metric(
                            "Precision",
                            f"{summary.precision:.2%}",
                            help="Defense precision: accuracy of blocking"
                        )
                    else:
                        st.metric("Precision", "N/A")
                
                with col3:
                    if summary.recall is not None:
                        st.metric(
                            "Recall",
                            f"{summary.recall:.2%}",
                            help="Defense recall: how many attacks were blocked"
                        )
                    else:
                        st.metric("Recall", "N/A")
                
                with col4:
                    if summary.benign_total:
                        st.metric(
                            "Benign FP Rate",
                            f"{summary.benign_fp_rate:.2%}",
                            help="Benign prompts incorrectly flagged as leaks",
                        )
                    else:
                        st.metric("Benign FP Rate", "N/A")

                with col5:
                    if summary.avg_lss is not None:
                        # Color code based on severity
                        lss_value = summary.avg_lss
                        if lss_value < 0.3:
                            delta_color = "normal"
                        elif lss_value < 0.6:
                            delta_color = "off"
                        else:
                            delta_color = "inverse"
                        
                        st.metric(
                            "Avg LSS",
                            f"{summary.avg_lss:.3f}",
                            delta=None,
                            delta_color=delta_color,
                            help="Leakage Severity Score: 0=no leakage, 1=critical leakage"
                        )
                    else:
                        st.metric("Avg LSS", "N/A")
    
    # Detailed results by model
    for model_name, results in all_results.items():
        with st.expander(f"📋 Detailed Results: {model_name}", expanded=False):
            st.subheader(f"Model: {model_name}")
            
            # Defense tabs
            defense_tabs = st.tabs(results["defenses"])
            
            for tab, defense_name in zip(defense_tabs, results["defenses"]):
                with tab:
                    st.markdown(f"### Defense: {defense_name}")
                    
                    # Filter records for this defense
                    defense_records = [
                        r for r in results["records"]
                        if r.defense_name == defense_name
                    ]
                    
                    # Create detailed table
                    detailed_data = []
                    for record in defense_records:
                        detailed_data.append({
                            "Attack": record.attack_name,
                            "Success": "✅ Yes" if record.success else "❌ No",
                            "Output Preview": record.raw_output[:100] + "..." if len(record.raw_output) > 100 else record.raw_output
                        })
                    
                    if detailed_data:
                        df_detailed = pd.DataFrame(detailed_data)
                        st.dataframe(df_detailed, use_container_width=True)
                        
                        # Show full outputs
                        st.markdown("#### Full Outputs")
                        for record in defense_records:
                            with st.expander(f"Attack: {record.attack_name}"):
                                st.text_area(
                                    "Model Response",
                                    value=record.raw_output,
                                    height=200,
                                    key=f"{model_name}_{defense_name}_{record.attack_name}"
                                )
    
    # Run history & regression
    st.markdown("---")
    st.subheader("📚 Run History & Regression")
    store = RunHistoryStore()
    past_runs = store.list_runs(limit=20)

    if past_runs:
        history_rows = [
            {
                "Run ID": r.id[:8] + "…",
                "Created": r.created_at[:19],
                "Provider": r.provider,
                "Model": r.model_name,
                "Avg ASR": f"{r.avg_asr:.2%}",
                "Scorer": r.scorer,
            }
            for r in past_runs
        ]
        st.dataframe(pd.DataFrame(history_rows), use_container_width=True)

        run_ids = [r.id for r in past_runs]
        col_a, col_b = st.columns(2)
        with col_a:
            baseline_id = st.selectbox("Baseline run", options=run_ids, index=min(1, len(run_ids) - 1))
        with col_b:
            current_id = st.selectbox("Compare run", options=run_ids, index=0)

        if st.button("Compare runs for regression"):
            baseline_record = store.get(baseline_id)
            current_record = store.get(current_id)
            if baseline_record and current_record:
                report = compare_results(
                    baseline_record["result"],
                    current_record["result"],
                    baseline_run_id=baseline_id,
                    current_run_id=current_id,
                )
                if report.has_regression:
                    st.warning(report.summary)
                else:
                    st.success(report.summary)

                regression_rows = []
                for d in report.defenses:
                    regression_rows.append({
                        "Defense": d.defense_name,
                        "ASR Δ": f"{d.asr_delta:+.2%}",
                        "Precision Δ": (
                            f"{d.precision_delta:+.2%}" if d.precision_delta is not None else "N/A"
                        ),
                        "Recall Δ": f"{d.recall_delta:+.2%}",
                        "Benign FP Δ": f"{d.benign_fp_delta:+.2%}",
                        "Attack regressions": len(d.attack_regressions),
                    })
                st.dataframe(pd.DataFrame(regression_rows), use_container_width=True)
    else:
        st.info("No saved runs yet. Enable **Save to run history** in the sidebar.")

    # Export results
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        export_data = {}
        for model_name, results in all_results.items():
            export_data[model_name] = {
                "defenses": {},
                "records": []
            }
            for summary, defense_name in zip(results["summaries"], results["defenses"]):
                export_data[model_name]["defenses"][defense_name] = {
                    "total": summary.total,
                    "successes": summary.successes,
                    "asr": summary.asr,
                    "num_attacks": summary.num_attacks,
                    "attack_breakdown": summary.attack_breakdown,
                    "avg_sds": summary.avg_sds,
                    "precision": summary.precision,
                    "recall": summary.recall,
                    "avg_lss": summary.avg_lss,
                    "benign_total": summary.benign_total,
                    "benign_false_positives": summary.benign_false_positives,
                    "benign_fp_rate": summary.benign_fp_rate,
                    "total_tokens": summary.total_tokens,
                    "estimated_cost_usd": summary.estimated_cost_usd,
                }
            for record in results["records"]:
                export_data[model_name]["records"].append({
                    "type": "attack",
                    "attack_name": record.attack_name,
                    "defense_name": record.defense_name,
                    "success": record.success,
                    "scorer": record.scorer,
                    "total_tokens": record.total_tokens,
                    "raw_output": record.raw_output,
                })
            for record in results.get("benign_records", []):
                export_data[model_name]["records"].append({
                    "type": "benign",
                    "defense_name": record.defense_name,
                    "benign_task": record.benign_task,
                    "leaked": record.leaked,
                    "scorer": record.scorer,
                    "total_tokens": record.total_tokens,
                    "raw_output": record.raw_output,
                })
        
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="promptguard_results.json",
            mime="application/json"
        )
    
    with col2:
        # CSV export
        csv_data = []
        for model_name, results in all_results.items():
            for record in results["records"]:
                csv_data.append({
                    "Model": model_name,
                    "Type": "attack",
                    "Attack": record.attack_name,
                    "Defense": record.defense_name,
                    "Success": record.success,
                    "Tokens": record.total_tokens,
                    "Output": record.raw_output,
                })
            for record in results.get("benign_records", []):
                csv_data.append({
                    "Model": model_name,
                    "Type": "benign",
                    "Attack": "",
                    "Defense": record.defense_name,
                    "Success": record.leaked,
                    "Tokens": record.total_tokens,
                    "Output": record.raw_output,
                })
        
        if csv_data:
            df_csv = pd.DataFrame(csv_data)
            csv_str = df_csv.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name="promptguard_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()

