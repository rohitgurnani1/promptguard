"""
Streamlit UI for PromptGuard - Interactive Prompt Injection Evaluation
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from promptguard.config import ModelConfig
from promptguard.models.openai_client import OpenAIClient
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering, ContextIsolationDefense
from promptguard.eval.runner import run_eval, EvalConfig
from promptguard.utils.logging_utils import print_records, print_summaries
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
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. You can also set it via OPENAI_API_KEY environment variable."
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.markdown("---")
        
        # Model selection
        st.subheader("📊 Models")
        model_options = {
            "gpt-4o-mini": ModelConfig(model_name="gpt-4o-mini", max_tokens=512),
            "gpt-5-mini": ModelConfig(model_name="gpt-5-mini", max_tokens=1024),
            "gpt-4o": ModelConfig(model_name="gpt-4o", max_tokens=512),
        }
        
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
        benign_task = st.text_area(
            "Benign Task Prompt",
            value="Summarize the main idea of this conversation for a non-technical audience.",
            help="The benign task that will be combined with attacks"
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
            - 🎯 **8 Different Attack Types**: Test against various prompt injection techniques
            - 🛡️ **Multiple Defense Strategies**: Evaluate prompt hardening and filtering
            - 📊 **Multi-Model Support**: Compare performance across different LLMs
            - 📈 **Comprehensive Metrics**: Attack success rates and robustness scores
            
            ### How it works:
            1. Select models, attacks, and defenses
            2. Run the evaluation
            3. View detailed results and metrics
            4. Compare performance across different configurations
            """)
        
        return
    
    # Validation
    if not api_key and not os.getenv("OPENAI_API_KEY"):
        st.error("❌ Please provide an OpenAI API key in the sidebar.")
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
    
    total_evals = len(selected_models) * len(selected_attacks) * len(selected_defenses)
    current_eval = 0
    
    for model_name in selected_models:
        status_text.text(f"Evaluating {model_name}...")
        
        try:
            model_config = model_options[model_name]
            client = OpenAIClient(config=model_config)
            
            # Filter attacks and defenses
            attacks = [attack_dict[name] for name in selected_attacks]
            defenses = [defense_options[name] for name in selected_defenses]
            
            eval_config = EvalConfig(benign_task_prompt=benign_task)
            
            records, summaries = run_eval(
                model=client,
                attacks=attacks,
                defenses=defenses,
                eval_config=eval_config,
            )
            
            all_results[model_name] = {
                "records": records,
                "summaries": summaries,
                "defenses": [d.name for d in defenses]
            }
            
            current_eval += len(attacks) * len(defenses)
            progress_bar.progress(min(current_eval / total_evals, 1.0))
            
        except Exception as e:
            import traceback
            st.error(f"❌ Error evaluating {model_name}: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
            continue
    
    progress_bar.progress(1.0)
    status_text.text("✅ Evaluation complete!")
    
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
                summary_data.append({
                    "Model": model_name,
                    "Defense": defense_name,
                    "Total Attacks": summary.total,
                    "Successful Attacks": summary.successes,
                    "Attack Success Rate": f"{summary.asr:.2%}",
                    "Robustness": f"{summary.robustness:.2%}"
                })
        
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
                    "robustness": summary.robustness
                }
            for record in results["records"]:
                export_data[model_name]["records"].append({
                    "attack_name": record.attack_name,
                    "defense_name": record.defense_name,
                    "success": record.success,
                    "raw_output": record.raw_output
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
                    "Attack": record.attack_name,
                    "Defense": record.defense_name,
                    "Success": record.success,
                    "Output": record.raw_output
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

