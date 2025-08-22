"""
Customer Analysis Module
Upload customer data and get AI-powered insights from Claude.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from pathlib import Path
import time
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.api_manager import APIManager
from ui.professional_theme import create_metric_card, create_professional_card
from business_rules.engine import BusinessRulesEngine

class CustomerAnalysisModule:
    """Customer Analysis Module for AI-powered customer insights."""
    
    def __init__(self):
        self.api_manager = None
        self.analysis_results = None
    
    def initialize_apis(self):
        """Initialize API connections."""
        try:
            self.api_manager = APIManager()
            return True
        except Exception as e:
            st.error(f"Failed to initialize APIs: {str(e)}")
            return False
    
    def render_file_upload_section(self):
        """Render the file upload interface."""
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #1A1A1A;">📊 Customer Data Upload</h3>
            <p style="color: #6B7280; margin-bottom: 1.5rem;">
                Upload your customer data file to begin AI analysis. Supported formats: CSV, Excel
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your customer data file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file containing customer information"
        )
        
        # Sample data option
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📁 Use Sample Data", use_container_width=True):
                return self.load_sample_data()
        
        with col2:
            if st.button("📋 View Data Template", use_container_width=True):
                self.show_data_template()
        
        if uploaded_file is not None:
            return self.process_uploaded_file(uploaded_file)
        
        return None
    
    def load_sample_data(self):
        """Load the sample customer data."""
        try:
            csv_path = Path("data/customer_profiles/sample_customers.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                st.success(f"✅ Loaded sample data: {len(df)} customers")
                return df
            else:
                st.error("Sample data not found. Please upload your own file.")
                return None
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")
            return None
    
    def process_uploaded_file(self, uploaded_file):
        """Process the uploaded customer data file."""
        try:
            # Read the file based on its type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:  # Excel file
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully: {len(df)} customers, {len(df.columns)} fields")
            
            # Show data preview
            with st.expander("📋 Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Customers", len(df))
                with col2:
                    st.metric("Data Fields", len(df.columns))
                with col3:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    st.metric("Numeric Fields", len(numeric_cols))
            
            return df
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None
    
    def show_data_template(self):
        """Show the expected data template."""
        st.info("""
        **Expected Customer Data Fields:**
        
        **Required Fields:**
        - customer_id: Unique identifier
        - name: Customer name
        - age: Customer age
        - account_balance: Current balance
        
        **Recommended Fields:**
        - digital_logins_per_month: Digital engagement
        - mobile_app_usage: App usage level (high/medium/low)
        - email_opens_per_month: Email engagement
        - phone_calls_per_month: Phone support usage
        - branch_visits_per_month: Branch visit frequency
        - prefers_digital: Boolean preference
        - requires_support: Support needs
        - accessibility_needs: Special requirements
        - income_level: Income bracket
        - employment_status: Employment info
        """)
    
    def render_analysis_controls(self, customer_data):
        """Render analysis configuration and controls."""
        if customer_data is None:
            return False
        
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #1A1A1A;">🤖 AI Analysis Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            batch_size = st.selectbox(
                "Batch Size",
                [5, 8, 10, 15],
                index=1,
                help="Number of customers to analyze per API call. Smaller = safer for rate limits."
            )
        
        with col2:
            max_customers = st.selectbox(
                "Max Customers",
                ["All", "10", "25", "50", "100"],
                index=0,
                help="Limit analysis for testing. Choose 'All' for production."
            )
        
        with col3:
            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Standard", "Detailed", "Comprehensive"],
                index=1,
                help="Depth of AI analysis. Detailed recommended for most use cases."
            )
        
        # Calculate customers to process
        if max_customers == "All":
            customers_to_process = len(customer_data)
        else:
            customers_to_process = min(int(max_customers), len(customer_data))
        
        # Analysis button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button(
                f"🚀 Analyze {customers_to_process} Customers",
                type="primary",
                use_container_width=True
            ):
                return self.run_customer_analysis(
                    customer_data.head(customers_to_process),
                    batch_size,
                    analysis_depth
                )
        
        return False
    
    def run_customer_analysis(self, customer_data, batch_size, analysis_depth):
        """Run the AI customer analysis."""
        if not self.initialize_apis():
            return False
        
        st.markdown("""
        <div class="modern-card primary">
            <h3 style="margin-top: 0; color: white;"> AI Analysis in Progress</h3>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
                Claude is analyzing your customer data. This may take 30-60 seconds...
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare customer data
        customers_list = customer_data.to_dict('records')
        total_customers = len(customers_list)
        
        try:
            status_text.text(f" Sending {total_customers} customers to Claude for analysis...")
            progress_bar.progress(0.1)
            
            # Run the analysis
            analysis_results = self.api_manager.analyze_customer_base(
                customers_list, 
                batch_size=batch_size
            )
            
            progress_bar.progress(0.8)
            status_text.text("📊 Processing analysis results...")
            
            if analysis_results:
                self.analysis_results = analysis_results
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis complete!")
                
                # Clear progress indicators after 2 seconds
                time.sleep(2)
                progress_bar.empty()
                status_text.empty()
                
                st.success(f"🎉 Successfully analyzed {len(analysis_results.get('customer_categories', []))} customers!")
                return True
            else:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ Analysis failed. Please check your API configuration and try again.")
                return False
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Analysis error: {str(e)}")
            return False
    
    def render_analysis_results(self):
        """Render the comprehensive analysis results."""
        if not self.analysis_results:
            return
        
        # Extract results
        customer_categories = self.analysis_results.get('customer_categories', [])
        aggregates = self.analysis_results.get('aggregates', {})
        segment_summaries = self.analysis_results.get('segment_summaries', [])
        
        # Results overview
        st.markdown("""
        <div class="modern-card primary">
            <h3 style="margin-top: 0; color: white;">📊 Analysis Results Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_analyzed = aggregates.get('total_customers', 0)
        upsell_eligible = aggregates.get('upsell_eligible_count', 0)
        vulnerable_count = aggregates.get('vulnerable_count', 0)
        accessibility_count = aggregates.get('accessibility_needs_count', 0)
        
        with col1:
            st.markdown(f"""
            <div class="modern-card">
                <div class="metric-value">{total_analyzed}</div>
                <div class="metric-label">CUSTOMERS ANALYZED</div>
                <div class="metric-delta positive">100% processed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            upsell_pct = (upsell_eligible / total_analyzed * 100) if total_analyzed > 0 else 0
            st.markdown(f"""
            <div class="modern-card">
                <div class="metric-value">{upsell_eligible}</div>
                <div class="metric-label">UPSELL ELIGIBLE</div>
                <div class="metric-delta positive">{upsell_pct:.0f}% of base</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="modern-card">
                <div class="metric-value">{vulnerable_count}</div>
                <div class="metric-label">VULNERABLE CUSTOMERS</div>
                <div class="metric-delta warning">Need protection</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="modern-card">
                <div class="metric-value">{accessibility_count}</div>
                <div class="metric-label">ACCESSIBILITY NEEDS</div>
                <div class="metric-delta warning">Special requirements</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Segment distribution chart
        self.render_segment_distribution(aggregates)
        
        # Customer insights
        self.render_customer_insights(aggregates)
        
        # Individual customer details
        self.render_customer_details(customer_categories)
        
        # Download results
        self.render_download_section()
    
    def render_segment_distribution(self, aggregates):
        """Render customer segment distribution chart."""
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">Customer Segment Distribution</div>
        </div>
        """, unsafe_allow_html=True)
        
        categories = aggregates.get('categories', {})
        
        if categories:
            # Create modern donut chart
            labels = list(categories.keys())
            values = list(categories.values())
            colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker_colors=colors[:len(labels)],
                textinfo='label+percent+value',
                textfont=dict(size=12, family="IBM Plex Sans"),
                hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Percentage: %{percent}<extra></extra>',
                marker=dict(line=dict(color='white', width=2))
            )])
            
            fig.update_layout(
                font=dict(family="IBM Plex Sans", size=12),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(t=0, b=0, l=0, r=0),
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_customer_insights(self, aggregates):
        """Render key customer insights."""
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #1A1A1A;">💡 Key Insights</h3>
        </div>
        """, unsafe_allow_html=True)
        
        insights = aggregates.get('insights', [])
        
        for i, insight in enumerate(insights):
            st.markdown(f"""
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #00A86B;">
                <strong>Insight {i+1}:</strong> {insight}
            </div>
            """, unsafe_allow_html=True)
    
    def render_customer_details(self, customer_categories):
        """Render detailed customer information."""
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #1A1A1A;">👥 Individual Customer Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create summary dataframe
        customer_summary = []
        
        for customer in customer_categories:
            customer_summary.append({
                'Customer ID': customer.get('customer_id', 'Unknown'),
                'Name': customer.get('name', 'Unknown'),
                'Category': customer.get('category', 'Unknown'),
                'Upsell Eligible': '✅' if customer.get('upsell_eligible') else '❌',
                'Account Health': customer.get('financial_indicators', {}).get('account_health', 'Unknown'),
                'Digital Maturity': customer.get('financial_indicators', {}).get('digital_maturity', 'Unknown'),
                'Risk Factors': len(customer.get('risk_factors', []))
            })
        
        if customer_summary:
            df = pd.DataFrame(customer_summary)
            st.dataframe(df, use_container_width=True, height=400)
            
            # Detailed customer cards
            with st.expander("🔍 Detailed Customer Analysis"):
                for customer in customer_categories:  # Show all customers
                    self.render_customer_card(customer)
    
    def render_customer_card(self, customer):
        """Render individual customer analysis card."""
        name = customer.get('name', 'Unknown')
        category = customer.get('category', 'Unknown')
        upsell_eligible = customer.get('upsell_eligible', False)
        reasoning = customer.get('category_reasoning', [])
        
        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1A1A1A;">{name}</h4>
                <span style="background: {'#10B981' if upsell_eligible else '#EF4444'}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                    {'Upsell Eligible' if upsell_eligible else 'No Upsell'}
                </span>
            </div>
            <p><strong>Category:</strong> {category}</p>
            <p><strong>Reasoning:</strong></p>
            <ul style="margin: 0.5rem 0;">
                {''.join([f'<li>{reason}</li>' for reason in reasoning[:3]])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_download_section(self):
        """Render download options for analysis results."""
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #1A1A1A;">📥 Download Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download CSV", use_container_width=True):
                self.download_csv_results()
        
        with col2:
            if st.button("📋 Download Report", use_container_width=True):
                self.download_report()
        
        with col3:
            if st.button("🔄 Download JSON", use_container_width=True):
                self.download_json_results()
    
    def download_csv_results(self):
        """Download results as CSV."""
        if not self.analysis_results:
            return
        
        customer_categories = self.analysis_results.get('customer_categories', [])
        
        # Convert to DataFrame
        df_data = []
        for customer in customer_categories:
            df_data.append({
                'customer_id': customer.get('customer_id'),
                'name': customer.get('name'),
                'category': customer.get('category'),
                'upsell_eligible': customer.get('upsell_eligible'),
                'account_health': customer.get('financial_indicators', {}).get('account_health'),
                'engagement_level': customer.get('financial_indicators', {}).get('engagement_level'),
                'digital_maturity': customer.get('financial_indicators', {}).get('digital_maturity'),
                'category_reasoning': '; '.join(customer.get('category_reasoning', [])),
                'risk_factors': '; '.join(customer.get('risk_factors', []))
            })
        
        df = pd.DataFrame(df_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download Customer Analysis CSV",
            data=csv,
            file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def download_json_results(self):
        """Download complete results as JSON."""
        if not self.analysis_results:
            return
        
        json_data = json.dumps(self.analysis_results, indent=2, default=str)
        
        st.download_button(
            label="🔄 Download Complete Analysis JSON",
            data=json_data,
            file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def download_report(self):
        """Download analysis report."""
        st.info("📋 Executive report generation coming in next update!")

def render_customer_analysis_page():
    """Main function to render the customer analysis page."""
    analysis_module = CustomerAnalysisModule()
    
    # File upload section
    customer_data = analysis_module.render_file_upload_section()
    
    if customer_data is not None:
        # Analysis controls
        analysis_started = analysis_module.render_analysis_controls(customer_data)
        
        # Show results if analysis was completed
        if analysis_started or analysis_module.analysis_results:
            analysis_module.render_analysis_results()