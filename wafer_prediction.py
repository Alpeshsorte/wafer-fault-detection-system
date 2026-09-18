"""
Wafer Fault Detection Prediction Pipeline
=========================================
Use trained models to predict faults in new wafer data
Author: AI Assistant for Electronics Engineer
"""

import pandas as pd
import numpy as np
import glob
import os
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class WaferFaultPredictor:
    """
    Predict wafer faults using pre-trained models
    """
    
    def __init__(self, model_path=".", prediction_data_path="Prediction_Batch_files"):
        self.model_path = model_path
        self.prediction_data_path = prediction_data_path
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.predictions = {}
        
    def load_trained_models(self):
        """
        Load pre-trained models and preprocessing objects
        """
        print("📂 Loading trained models...")
        
        try:
            # Load models
            model_files = {
                'Random Forest': 'wafer_random_forest_model.pkl',
                'XGBoost': 'wafer_xgboost_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                if os.path.exists(filename):
                    self.models[model_name] = joblib.load(filename)
                    print(f"✅ Loaded: {model_name}")
                else:
                    print(f"⚠️  Model not found: {filename}")
            
            # Load scaler
            if os.path.exists('wafer_scaler.pkl'):
                self.scaler = joblib.load('wafer_scaler.pkl')
                print("✅ Loaded: Scaler")
            else:
                print("⚠️  Scaler not found")
            
            # Load feature names
            if os.path.exists('feature_names.txt'):
                with open('feature_names.txt', 'r') as f:
                    self.feature_names = [line.strip() for line in f.readlines()]
                print(f"✅ Loaded: {len(self.feature_names)} feature names")
            else:
                print("⚠️  Feature names not found")
                
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
        
        return len(self.models) > 0
    
    def load_prediction_data(self):
        """
        Load prediction batch files
        """
        print(f"\n📂 Loading prediction data from {self.prediction_data_path}...")
        
        csv_files = glob.glob(os.path.join(self.prediction_data_path, "*.csv"))
        print(f"Found {len(csv_files)} prediction files")
        
        all_prediction_data = []
        file_mapping = {}
        
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                df['source_file'] = os.path.basename(file)
                
                # Store mapping of wafer IDs to source files
                for idx, wafer_id in enumerate(df.iloc[:, 0]):
                    file_mapping[wafer_id] = os.path.basename(file)
                
                all_prediction_data.append(df)
                print(f"✅ Loaded: {os.path.basename(file)} - Shape: {df.shape}")
                
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")
        
        if not all_prediction_data:
            print("❌ No prediction data loaded!")
            return None, None
        
        # Combine all prediction data
        combined_data = pd.concat(all_prediction_data, ignore_index=True)
        print(f"📊 Combined prediction dataset shape: {combined_data.shape}")
        
        return combined_data, file_mapping
    
    def preprocess_prediction_data(self, data):
        """
        Preprocess prediction data using the same steps as training
        """
        print("\n🧹 Preprocessing prediction data...")
        
        # Extract wafer IDs
        wafer_ids = data.iloc[:, 0]
        
        # Get sensor columns (same as training)
        sensor_columns = [col for col in data.columns 
                         if col not in ['Unnamed: 0', 'source_file'] 
                         and not col.startswith('Wafer')]
        
        features = data[sensor_columns]
        
        # Ensure we have the same features as training
        missing_features = set(self.feature_names) - set(features.columns)
        extra_features = set(features.columns) - set(self.feature_names)
        
        if missing_features:
            print(f"⚠️  Missing features: {len(missing_features)}")
            # Add missing features with median values
            for feature in missing_features:
                features[feature] = 0  # or use median from training
        
        if extra_features:
            print(f"⚠️  Extra features found: {len(extra_features)}")
            # Remove extra features
            features = features.drop(columns=list(extra_features))
        
        # Reorder columns to match training
        features = features[self.feature_names]
        
        # Handle missing values
        features = features.fillna(features.median())
        
        # Scale features using the same scaler from training
        if self.scaler:
            scaled_features = self.scaler.transform(features)
            features_scaled = pd.DataFrame(
                scaled_features, 
                columns=features.columns,
                index=features.index
            )
        else:
            features_scaled = features
            print("⚠️  No scaler available, using raw features")
        
        print(f"✅ Preprocessed features shape: {features_scaled.shape}")
        
        return features_scaled, wafer_ids
    
    def make_predictions(self, features, wafer_ids):
        """
        Make predictions using all loaded models
        """
        print("\n🔮 Making predictions...")
        
        predictions_df = pd.DataFrame()
        predictions_df['Wafer_ID'] = wafer_ids
        
        for model_name, model in self.models.items():
            print(f"🤖 Predicting with {model_name}...")
            
            try:
                # Make predictions
                pred_labels = model.predict(features)
                pred_proba = model.predict_proba(features)[:, 1] if hasattr(model, 'predict_proba') else None
                
                # Store predictions
                predictions_df[f'{model_name}_Prediction'] = pred_labels
                predictions_df[f'{model_name}_Label'] = ['Faulty' if p == 1 else 'Good' for p in pred_labels]
                
                if pred_proba is not None:
                    predictions_df[f'{model_name}_Fault_Probability'] = pred_proba
                
                # Summary statistics
                fault_count = np.sum(pred_labels == 1)
                good_count = np.sum(pred_labels == 0)
                fault_rate = fault_count / len(pred_labels) * 100
                
                print(f"  📊 {model_name} Results:")
                print(f"     Good wafers: {good_count} ({100-fault_rate:.1f}%)")
                print(f"     Faulty wafers: {fault_count} ({fault_rate:.1f}%)")
                
            except Exception as e:
                print(f"❌ Error with {model_name}: {e}")
        
        return predictions_df
    
    def create_detailed_report(self, predictions_df, file_mapping):
        """
        Create detailed prediction report
        """
        print("\n📊 Creating detailed report...")
        
        # Add source file information
        predictions_df['Source_File'] = predictions_df['Wafer_ID'].map(file_mapping)
        
        # Create consensus prediction (majority vote)
        model_columns = [col for col in predictions_df.columns if col.endswith('_Prediction')]
        if len(model_columns) > 1:
            predictions_df['Consensus_Prediction'] = predictions_df[model_columns].mode(axis=1)[0]
            predictions_df['Consensus_Label'] = ['Faulty' if p == 1 else 'Good' 
                                               for p in predictions_df['Consensus_Prediction']]
        
        # Summary by source file
        file_summary = predictions_df.groupby('Source_File').agg({
            'Wafer_ID': 'count',
            'Consensus_Prediction': ['sum', 'mean']
        }).round(3)
        
        file_summary.columns = ['Total_Wafers', 'Faulty_Count', 'Fault_Rate']
        file_summary = file_summary.sort_values('Fault_Rate', ascending=False)
        
        print("\n📋 Summary by Source File:")
        print(file_summary)
        
        # Overall summary
        total_wafers = len(predictions_df)
        total_faulty = predictions_df['Consensus_Prediction'].sum() if 'Consensus_Prediction' in predictions_df.columns else 0
        overall_fault_rate = total_faulty / total_wafers * 100
        
        print(f"\n🎯 Overall Summary:")
        print(f"Total wafers analyzed: {total_wafers}")
        print(f"Predicted faulty wafers: {total_faulty}")
        print(f"Overall fault rate: {overall_fault_rate:.2f}%")
        
        return predictions_df, file_summary
    
    def save_results(self, predictions_df, file_summary):
        """
        Save prediction results to files
        """
        print("\n💾 Saving results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed predictions
        predictions_filename = f"wafer_predictions_{timestamp}.csv"
        predictions_df.to_csv(predictions_filename, index=False)
        print(f"✅ Saved: {predictions_filename}")
        
        # Save file summary
        summary_filename = f"wafer_summary_{timestamp}.csv"
        file_summary.to_csv(summary_filename)
        print(f"✅ Saved: {summary_filename}")
        
        # Save high-risk wafers (if any)
        if 'Consensus_Prediction' in predictions_df.columns:
            high_risk = predictions_df[predictions_df['Consensus_Prediction'] == 1]
            if len(high_risk) > 0:
                risk_filename = f"high_risk_wafers_{timestamp}.csv"
                high_risk.to_csv(risk_filename, index=False)
                print(f"⚠️  Saved high-risk wafers: {risk_filename}")
        
        return predictions_filename, summary_filename
    
    def run_prediction_pipeline(self):
        """
        Run the complete prediction pipeline
        """
        print("🚀 Wafer Fault Prediction Pipeline")
        print("=" * 40)
        
        # Step 1: Load trained models
        if not self.load_trained_models():
            print("❌ Cannot proceed without trained models!")
            return False
        
        # Step 2: Load prediction data
        prediction_data, file_mapping = self.load_prediction_data()
        if prediction_data is None:
            print("❌ Cannot proceed without prediction data!")
            return False
        
        # Step 3: Preprocess data
        features, wafer_ids = self.preprocess_prediction_data(prediction_data)
        
        # Step 4: Make predictions
        predictions_df = self.make_predictions(features, wafer_ids)
        
        # Step 5: Create detailed report
        predictions_df, file_summary = self.create_detailed_report(predictions_df, file_mapping)
        
        # Step 6: Save results
        pred_file, summary_file = self.save_results(predictions_df, file_summary)
        
        print("\n🎉 Prediction Pipeline Complete!")
        print(f"📊 Results saved to: {pred_file}")
        print(f"📋 Summary saved to: {summary_file}")
        
        return True

def main():
    """
    Main prediction function
    """
    predictor = WaferFaultPredictor()
    predictor.run_prediction_pipeline()

if __name__ == "__main__":
    main()
