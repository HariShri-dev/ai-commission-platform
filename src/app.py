import streamlit as st
import pandas as pd
import plotly.express as px

from .managers import RulesManager
from .validators import CommissionValidator
from .analyzers import DataAnalyzer
from .generators import DataGenerator


class CommissionPlatform:
    """Main application class that orchestrates all components"""

    def __init__(self):
        self.setup_page()
        self.rules_manager = RulesManager()
        self.validator = CommissionValidator(self.rules_manager)
        self.analyzer = DataAnalyzer()
        self.data_generator = DataGenerator()

    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI Commission Platform",
            page_icon="💰",
            layout="wide"
        )

        # Custom CSS
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem;
            }
        </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        """Render application header"""
        st.markdown('<div class="main-header">🤖 AI Commission Validation Platform</div>', unsafe_allow_html=True)

    def render_sidebar(self):
        """Render sidebar for data input"""
        with st.sidebar:
            st.header("Data Input")

            upload_option = st.radio(
                "Choose data source:",
                ["Use Sample Data", "Upload Your Data"]
            )

            if upload_option == "Upload Your Data":
                uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
                if uploaded_file:
                    return pd.read_csv(uploaded_file)
                else:
                    st.info("Please upload a CSV file or use sample data")
                    return None
            else:
                df = self.data_generator.generate_sample_data()
                st.download_button(
                    label="Download Sample Data",
                    data=df.to_csv(index=False),
                    file_name="sample_commission_data.csv",
                    mime="text/csv"
                )
                return df

    def render_overview_tab(self, df):
        """Render overview dashboard tab"""
        with st.container():
            # Calculate metrics
            metrics = self.analyzer.calculate_metrics(df, self.validator)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Commissions", f"${metrics['total_commissions']:,.0f}")
            with col2:
                st.metric("Average Rate", f"{metrics['average_rate']:.1%}")
            with col3:
                st.metric("Total Deals", metrics['total_deals'])
            with col4:
                st.metric("Flagged Items", metrics['flagged_count'])

            # Charts
            fig1 = px.bar(df.groupby('region')['commission_amount'].sum().reset_index(),
                          x='region', y='commission_amount', title="Commissions by Region")
            st.plotly_chart(fig1, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                fig2 = px.histogram(df, x='deal_size', title="Deal Size Distribution")
                st.plotly_chart(fig2, use_container_width=True)

            with col2:
                fig3 = px.box(df, x='product_tier', y='commission_rate', title="Commission Rates by Product Tier")
                st.plotly_chart(fig3, use_container_width=True)

    def render_validation_tab(self, df):
        """Render validation results tab"""
        validation_results = []
        for idx, row in df.iterrows():
            issues = self.validator.validate(row)
            validation_results.append({
                'deal_id': row['deal_id'],
                'sales_rep': row['sales_rep'],
                'deal_size': row['deal_size'],
                'commission_amount': row['commission_amount'],
                'issues': issues,
                'issue_count': len(issues),
                'status': 'PASS' if len(issues) == 0 else 'FAIL'
            })

        results_df = pd.DataFrame(validation_results)
        st.dataframe(results_df, use_container_width=True)

        # Download results
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download Validation Results",
            data=csv,
            file_name="commission_validation_results.csv",
            mime="text/csv"
        )

    def render_analytics_tab(self, df):
        """Render analytics and anomaly detection tab"""
        df_with_anomalies = self.analyzer.detect_anomalies(df)

        fig_anomaly = px.scatter(df_with_anomalies,
                                 x='deal_size',
                                 y='commission_amount',
                                 color='is_anomaly',
                                 title="Anomaly Detection: Deal Size vs Commission Amount",
                                 hover_data=['sales_rep', 'product_tier'])
        st.plotly_chart(fig_anomaly, use_container_width=True)

        anomalies_df = df_with_anomalies[df_with_anomalies['is_anomaly'] == True]
        st.subheader(f"Detected Anomalies ({len(anomalies_df)} records)")
        st.dataframe(anomalies_df, use_container_width=True)

    def render_settings_tab(self):
        """Render settings and rules management tab"""
        st.subheader("Current Commission Structure")
        rules_df = pd.DataFrame(self.rules_manager.get_rules()).T
        st.dataframe(rules_df, use_container_width=True)

        # Remove Rule Section
        st.subheader("Remove Rule")
        rules = self.rules_manager.get_rules()
        if rules:
            rules_list = self.rules_manager.get_rules_list()
            rule_to_remove = st.selectbox(
                "Select a rule to remove:",
                rules_list,
                key="remove_rule_select"
            )

            if st.button("🗑️ Remove Selected Rule", key="remove_rule_btn"):
                success, message = self.rules_manager.remove_rule(rule_to_remove)
                st.write(message)
                if success:
                    st.rerun()
        else:
            st.warning("No rules available to remove.")

        st.divider()

        # Add Rule Section
        st.subheader("Add New Rule")
        with st.form("add_rule"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_tier = st.text_input("Tier Name", placeholder="e.g., platinum")
            with col2:
                new_rate = st.number_input("Commission Rate", min_value=0.0, max_value=1.0, value=0.05, step=0.01,
                                           format="%.3f")
            with col3:
                new_threshold = st.number_input("Threshold", min_value=0, value=0, step=10000)

            submitted = st.form_submit_button("➕ Add New Rule")
            if submitted:
                success, message = self.rules_manager.add_rule(new_tier, new_rate, new_threshold)
                st.write(message)
                if success:
                    st.rerun()

    def run(self):
        """Main application runner"""
        self.render_header()

        # Load data
        df = self.render_sidebar()
        if df is None:
            return

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Validation Results", "📈 Analytics", "⚙️ Settings"])

        with tab1:
            self.render_overview_tab(df)

        with tab2:
            self.render_validation_tab(df)

        with tab3:
            self.render_analytics_tab(df)

        with tab4:
            self.render_settings_tab()