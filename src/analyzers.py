import pandas as pd
from sklearn.ensemble import IsolationForest


class DataAnalyzer:
    """Handles data analysis and ML operations"""

    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)

    def detect_anomalies(self, df):
        """Use ML to detect anomalous commission patterns"""
        features = df[['deal_size', 'commission_amount', 'commission_rate']].fillna(0)

        anomalies = self.anomaly_detector.fit_predict(features)

        df['anomaly_score'] = anomalies
        df['is_anomaly'] = df['anomaly_score'] == -1

        return df

    def calculate_metrics(self, df, validator):
        """Calculate key business metrics"""
        total_commissions = df['commission_amount'].sum()
        average_rate = df['commission_rate'].mean()
        total_deals = len(df)

        # Count flagged items
        flagged_count = len([issue for row in df.iterrows() for issue in validator.validate(row[1])])

        return {
            'total_commissions': total_commissions,
            'average_rate': average_rate,
            'total_deals': total_deals,
            'flagged_count': flagged_count
        }