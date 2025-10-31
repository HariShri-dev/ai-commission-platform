import streamlit as st


class RulesManager:
    """Manages commission rules with CRUD operations"""

    def __init__(self):
        self._initialize_rules()

    def _initialize_rules(self):
        """Initialize rules in session state if not present"""
        if 'commission_rules' not in st.session_state:
            st.session_state.commission_rules = {
                'standard': {'rate': 0.05, 'threshold': 0},
                'premium': {'rate': 0.07, 'threshold': 100000},
                'enterprise': {'rate': 0.10, 'threshold': 500000}
            }

    def get_rules(self):
        """Get current commission rules"""
        return st.session_state.commission_rules

    def add_rule(self, tier_name, rate, threshold):
        """Add a new commission rule"""
        if tier_name.strip() and tier_name not in st.session_state.commission_rules:
            st.session_state.commission_rules[tier_name] = {
                'rate': float(rate),
                'threshold': int(threshold)
            }
            return True, f"✅ Successfully added '{tier_name}' tier!"
        elif not tier_name.strip():
            return False, "❌ Please enter a tier name!"
        else:
            return False, f"❌ Rule '{tier_name}' already exists!"

    def remove_rule(self, tier_name):
        """Remove a commission rule"""
        rules = self.get_rules()
        if len(rules) > 1:
            if tier_name in rules:
                del st.session_state.commission_rules[tier_name]
                return True, f"✅ Successfully removed '{tier_name}' tier!"
            else:
                return False, f"❌ Rule '{tier_name}' not found!"
        else:
            return False, "❌ Cannot remove the last rule! You need at least one commission tier."

    def get_rules_list(self):
        """Get list of rule names for dropdowns"""
        return list(self.get_rules().keys())