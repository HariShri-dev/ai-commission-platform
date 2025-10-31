from abc import ABC, abstractmethod


class Validator(ABC):
    """Abstract base class for all validators"""

    @abstractmethod
    def validate(self, data):
        pass


class CommissionValidator(Validator):
    """Commission-specific validator"""

    def __init__(self, rules_manager):
        self.rules_manager = rules_manager

    def validate(self, row):
        """Validate individual commission record"""
        issues = []

        # Check if product tier exists in our rules
        if row['product_tier'] not in self.rules_manager.get_rules():
            issues.append(f"Unknown product tier: {row['product_tier']}")
            return issues

        # Rule 1: Check commission rate alignment
        expected_rate = self._get_expected_rate(row['deal_size'], row['product_tier'])
        if abs(row['commission_rate'] - expected_rate) > 0.001:
            issues.append(f"Rate mismatch: expected {expected_rate:.3f}, got {row['commission_rate']:.3f}")

        # Rule 2: Check for unusually high commissions
        if row['commission_amount'] > row['deal_size'] * 0.15:
            issues.append("Commission exceeds 15% cap")

        # Rule 3: Validate deal size consistency
        if row['deal_size'] < 0:
            issues.append("Negative deal size")

        return issues

    def _get_expected_rate(self, deal_size, product_tier):
        """Calculate expected commission rate based on rules"""
        rules = self.rules_manager.get_rules()
        base_rate = rules[product_tier]['rate']

        # Accelerator for over-quota performance
        if deal_size > rules[product_tier]['threshold'] * 1.2:
            return base_rate * 1.1  # 10% accelerator

        return base_rate