"""
Wafer Fault Detection ML Training Pipeline
==========================================
Comprehensive machine learning pipeline for semiconductor wafer fault detection
Author: AI Assistant for Electronics Engineer
"""

import pandas as pd
import numpy as np
import glob
import os
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.pipeline import Pipeline
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class WaferFaultDetection:
    """
    Comprehensive wafer fault detection system using multiple ML approaches
    """
    
    def __init__(self, data_path="Training_Batch_Files"):
        self.data_path = data_path
        self.data = None
        self.features = None
        self.wafer_ids = None
        self.scaler = None
        self.models = {}
        self.results = {}
        
    def load_and_combine_data(self):
        """
        Load all training CSV files and combine them
        """
        print("📂 Loading training data...")
        
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        print(f"Found {len(csv_files)} training files")
        
        all_data = []
        
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                # Add source file as metadata
                df['source_file'] = os.path.basename(file)
                all_data.append(df)
                print(f"✅ Loaded: {os.path.basename(file)} - Shape: {df.shape}")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")
        
        # Combine all data
        self.data = pd.concat(all_data, ignore_index=True)
        print(f"\n📊 Combined dataset shape: {self.data.shape}")
        
        # Extract wafer IDs and features
        self.wafer_ids = self.data.iloc[:, 0]  # First column contains wafer IDs
        
        # Get sensor columns (exclude first column and source_file)
        sensor_columns = [col for col in self.data.columns 
                         if col not in ['Unnamed: 0', 'source_file'] 
                         and not col.startswith('Wafer')]
        
        self.features = self.data[sensor_columns]
        
        # Convert all columns to numeric, coercing errors to NaN
        for col in self.features.columns:
            self.features[col] = pd.to_numeric(self.features[col], errors='coerce')
        print(f"📈 Feature columns: {len(sensor_columns)}")
        print(f"🔍 Sample sensor names: {sensor_columns[:10]}")
        
        return self.data
    
    def data_preprocessing(self):
        """
        Clean and preprocess the sensor data
        """
        print("\n🧹 Data Preprocessing...")
        
        # Handle missing values
        missing_before = self.features.isnull().sum().sum()
        print(f"Missing values before cleaning: {missing_before}")
        
        # Fill missing values with median for each sensor
        # Use forward fill first, then backward fill, then median
        self.features = self.features.ffill().bfill()
        remaining_missing = self.features.isnull().sum().sum()
        
        if remaining_missing > 0:
            print(f"Filling remaining {remaining_missing} missing values with median...")
            self.features = self.features.fillna(self.features.median())
            
        # Final check and fill any remaining NaN with 0
        final_missing = self.features.isnull().sum().sum()
        if final_missing > 0:
            print(f"Filling final {final_missing} missing values with 0...")
            self.features = self.features.fillna(0)
        
        # Remove constant features (sensors that don't vary)
        constant_features = self.features.columns[self.features.var() == 0]
        if len(constant_features) > 0:
            print(f"🚫 Removing {len(constant_features)} constant features")
            self.features = self.features.drop(columns=constant_features)
        
        # Remove highly correlated features
        correlation_matrix = self.features.corr().abs()
        upper_triangle = correlation_matrix.where(
            np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
        )
        
        high_corr_features = [column for column in upper_triangle.columns 
                            if any(upper_triangle[column] > 0.95)]
        
        if len(high_corr_features) > 0:
            print(f"🔗 Removing {len(high_corr_features)} highly correlated features")
            self.features = self.features.drop(columns=high_corr_features)
        
        print(f"✅ Final feature count: {self.features.shape[1]}")
        
        # Scale features
        self.scaler = RobustScaler()  # Better for outliers than StandardScaler
        scaled_features = self.scaler.fit_transform(self.features)
        self.features_scaled = pd.DataFrame(
            scaled_features, 
            columns=self.features.columns,
            index=self.features.index
        )
        
        return self.features_scaled
    
    def exploratory_data_analysis(self):
        """
        Perform EDA to understand the data distribution
        """
        print("\n📊 Exploratory Data Analysis...")
        
        # Basic statistics
        print("📈 Feature Statistics:")
        print(self.features.describe())
        
        # Create visualizations
        plt.figure(figsize=(15, 10))
        
        # 1. Distribution of sensor readings
        plt.subplot(2, 3, 1)
        self.features.iloc[:, :10].boxplot()
        plt.title('Distribution of First 10 Sensors')
        plt.xticks(rotation=45)
        
        # 2. Correlation heatmap (sample)
        plt.subplot(2, 3, 2)
        sample_corr = self.features.iloc[:, :20].corr()
        sns.heatmap(sample_corr, cmap='coolwarm', center=0)
        plt.title('Correlation Heatmap (Sample)')
        
        # 3. PCA visualization
        plt.subplot(2, 3, 3)
        try:
            pca_temp = PCA(n_components=2)
            pca_result = pca_temp.fit_transform(self.features_scaled)
            plt.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.6)
            plt.title('PCA Visualization')
            plt.xlabel('First Principal Component')
            plt.ylabel('Second Principal Component')
        except Exception as e:
            plt.text(0.5, 0.5, f'PCA Error:\n{str(e)[:50]}...', ha='center', va='center')
            plt.title('PCA Visualization (Error)')
        
        # 4. Feature variance
        plt.subplot(2, 3, 4)
        feature_variance = self.features.var().sort_values(ascending=False)
        plt.plot(feature_variance[:50])
        plt.title('Top 50 Feature Variances')
        plt.xlabel('Feature Index')
        plt.ylabel('Variance')
        
        # 5. Missing values heatmap
        plt.subplot(2, 3, 5)
        missing_data = self.data.isnull().sum()
        if missing_data.sum() > 0:
            missing_data[missing_data > 0].plot(kind='bar')
            plt.title('Missing Values by Column')
        else:
            plt.text(0.5, 0.5, 'No Missing Values', ha='center', va='center')
            plt.title('Missing Values Status')
        
        # 6. Sample distribution
        plt.subplot(2, 3, 6)
        wafer_counts = self.data['source_file'].value_counts()
        plt.pie(wafer_counts[:10], labels=wafer_counts.index[:10], autopct='%1.1f%%')
        plt.title('Top 10 Source Files Distribution')
        
        plt.tight_layout()
        plt.savefig('wafer_eda_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 EDA plots saved as 'wafer_eda_analysis.png'")
    
    def create_anomaly_labels(self):
        """
        Create labels using multiple anomaly detection methods
        Since we don't have ground truth labels, we'll use unsupervised methods
        """
        print("\n🎯 Creating Anomaly Labels...")
        
        # Method 1: Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        iso_labels = iso_forest.fit_predict(self.features_scaled)
        
        # Method 2: One-Class SVM
        oc_svm = OneClassSVM(nu=0.1)
        svm_labels = oc_svm.fit_predict(self.features_scaled)
        
        # Method 3: Statistical outliers (Z-score based)
        z_scores = np.abs((self.features_scaled - self.features_scaled.mean()) / self.features_scaled.std())
        statistical_outliers = (z_scores > 3).any(axis=1).astype(int)
        statistical_labels = np.where(statistical_outliers, -1, 1)
        
        # Combine methods (consensus approach)
        label_matrix = np.column_stack([iso_labels, svm_labels, statistical_labels])
        consensus_labels = []
        
        for row in label_matrix:
            # If 2 or more methods agree on anomaly, mark as anomaly
            if np.sum(row == -1) >= 2:
                consensus_labels.append(1)  # Anomaly
            else:
                consensus_labels.append(0)  # Normal
        
        self.labels = np.array(consensus_labels)
        
        print(f"📊 Label Distribution:")
        print(f"Normal wafers: {np.sum(self.labels == 0)} ({np.mean(self.labels == 0)*100:.1f}%)")
        print(f"Anomalous wafers: {np.sum(self.labels == 1)} ({np.mean(self.labels == 1)*100:.1f}%)")
        
        return self.labels
    
    def train_supervised_models(self):
        """
        Train supervised models using the created labels
        """
        print("\n🤖 Training Supervised Models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            self.features_scaled, self.labels, 
            test_size=0.2, random_state=42, stratify=self.labels
        )
        
        # Model 1: Random Forest
        print("🌲 Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_score = rf_model.score(X_test, y_test)              
        
        self.models['Random Forest'] = rf_model
        self.results['Random Forest'] = {
            'accuracy': rf_score,
            'predictions': rf_pred,
            'feature_importance': rf_model.feature_importances_
        }
        
        # Model 2: XGBoost
        print("🚀 Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)
        xgb_score = xgb_model.score(X_test, y_test)
        
        self.models['XGBoost'] = xgb_model
        self.results['XGBoost'] = {
            'accuracy': xgb_score,
            'predictions': xgb_pred,
            'feature_importance': xgb_model.feature_importances_
        }
        
        # Model evaluation
        print("\n📊 Model Performance:")
        for model_name in ['Random Forest', 'XGBoost']:
            print(f"\n{model_name}:")
            print(f"Accuracy: {self.results[model_name]['accuracy']:.4f}")
            print("Classification Report:")
            print(classification_report(y_test, self.results[model_name]['predictions']))
        
        return X_test, y_test
    
    def feature_importance_analysis(self):
        """
        Analyze which sensors are most important for fault detection
        """
        print("\n🔍 Feature Importance Analysis...")
        
        # Get feature importance from Random Forest
        rf_importance = self.results['Random Forest']['feature_importance']
        feature_names = self.features.columns
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            'sensor': feature_names,
            'importance': rf_importance
        }).sort_values('importance', ascending=False)
        
        # Top 20 most important sensors
        top_sensors = importance_df.head(20)
        
        print("🏆 Top 20 Most Important Sensors:")
        for i, (_, row) in enumerate(top_sensors.iterrows(), 1):
            print(f"{i:2d}. {row['sensor']:<30} {row['importance']:.4f}")
        
        # Visualize feature importance
        plt.figure(figsize=(12, 8))
        plt.barh(range(20), top_sensors['importance'][:20])
        plt.yticks(range(20), top_sensors['sensor'][:20])
        plt.xlabel('Feature Importance')
        plt.title('Top 20 Most Important Sensors for Fault Detection')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Analyze by sensor category
        sensor_categories = {}
        for sensor in feature_names:
            category = sensor.split('_')[0]
            if category not in sensor_categories:
                sensor_categories[category] = []
            sensor_categories[category].append(sensor)
        
        print(f"\n📊 Importance by Sensor Category:")
        category_importance = {}
        for category, sensors in sensor_categories.items():
            category_sensors = [s for s in sensors if s in feature_names]
            if category_sensors:
                indices = [list(feature_names).index(s) for s in category_sensors]
                avg_importance = np.mean([rf_importance[i] for i in indices])
                category_importance[category] = avg_importance
                print(f"{category:<8}: {avg_importance:.4f} (avg of {len(category_sensors)} sensors)")
        
        return importance_df
    
    def save_models(self):
        """
        Save trained models and preprocessing objects
        """
        print("\n💾 Saving Models...")
        
        import joblib
        
        # Save models
        for model_name, model in self.models.items():
            filename = f"wafer_{model_name.lower().replace(' ', '_')}_model.pkl"
            joblib.dump(model, filename)
            print(f"✅ Saved: {filename}")
        
        # Save scaler
        joblib.dump(self.scaler, "wafer_scaler.pkl")
        print("✅ Saved: wafer_scaler.pkl")
        
        # Save feature names
        with open("feature_names.txt", "w") as f:
            for feature in self.features.columns:
                f.write(f"{feature}\n")
        print("✅ Saved: feature_names.txt")
        
        print("🎯 All models and preprocessing objects saved!")

def main():
    """
    Main training pipeline
    """
    print("🚀 Wafer Fault Detection Training Pipeline")
    print("=" * 50)
    
    # Initialize the system
    wafer_system = WaferFaultDetection()
    
    # Step 1: Load data
    wafer_system.load_and_combine_data()
    
    # Step 2: Preprocess data
    wafer_system.data_preprocessing()
    
    # Step 3: EDA
    wafer_system.exploratory_data_analysis()
    
    # Step 4: Create labels
    wafer_system.create_anomaly_labels()
    
    # Step 5: Train models
    wafer_system.train_supervised_models()
    
    # Step 6: Feature importance
    wafer_system.feature_importance_analysis()
    
    # Step 7: Save models
    wafer_system.save_models()
    
    print("\n🎉 Training Pipeline Complete!")
    print("📊 Check the generated plots and saved models.")

if __name__ == "__main__":
    main()
