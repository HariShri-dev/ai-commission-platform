import pandas as pd
import numpy as np


class DataGenerator:
    """Handles data generation and sample data creation"""

    @staticmethod
    def generate_sample_data():
        """Generate realistic sample sales data"""
        np.random.seed(42)

        data = {
            'deal_id': [f'DEAL_{i:04d}' for i in range(1, 101)],
            'sales_rep': np.random.choice(['John Smith', 'Sarah Chen', 'Mike Johnson', 'Lisa Wang', 'David Brown'],
                                          100),
            'region': np.random.choice(['North America', 'Europe', 'Asia Pacific'], 100),
            'product_tier': np.random.choice(['standard', 'premium', 'enterprise'], 100, p=[0.5, 0.3, 0.2]),
            'deal_size': np.random.lognormal(10, 1, 100),
            'commission_rate': np.random.normal(0.06, 0.02, 100),
            'quota_achievement': np.random.normal(1.0, 0.3, 100)
        }

        df = pd.DataFrame(data)
        df['deal_size'] = df['deal_size'].clip(lower=1000)
        df['commission_rate'] = df['commission_rate'].clip(lower=0.01, upper=0.15)
        df['commission_amount'] = df['deal_size'] * df['commission_rate']

        # Introduce some anomalies
        anomaly_indices = np.random.choice(100, 10, replace=False)
        df.loc[anomaly_indices, 'commission_amount'] *= 2
        df.loc[anomaly_indices[5:], 'commission_rate'] = 0.20

        return df