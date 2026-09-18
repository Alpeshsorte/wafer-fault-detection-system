"""
Wafer Fault Detection Flask Web Application
==========================================
Web interface for semiconductor wafer fault detection system
Author: AI Assistant for Electronics Engineer
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import json
warnings.filterwarnings('ignore')

# Custom JSON encoder to handle numpy data types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

app = Flask(__name__)
app.secret_key = 'wafer_detection_secret_key_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.json_encoder = NumpyEncoder

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class WaferDetectionSystem:
    """
    Core wafer detection system for Flask app
    """
    
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.load_models()
    
    def load_models(self):
        """Load trained models and preprocessing objects"""
        try:
            # Load models
            if os.path.exists('wafer_random_forest_model.pkl'):
                self.models['Random Forest'] = joblib.load('wafer_random_forest_model.pkl')
            
            if os.path.exists('wafer_xgboost_model.pkl'):
                self.models['XGBoost'] = joblib.load('wafer_xgboost_model.pkl')
            
            # Load scaler
            if os.path.exists('wafer_scaler.pkl'):
                self.scaler = joblib.load('wafer_scaler.pkl')
            
            # Load feature names
            if os.path.exists('feature_names.txt'):
                with open('feature_names.txt', 'r') as f:
                    self.feature_names = [line.strip() for line in f.readlines()]
            
            return len(self.models) > 0
            
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def preprocess_data(self, df):
        """Preprocess uploaded data"""
        try:
            # Extract wafer IDs
            wafer_ids = df.iloc[:, 0]
            
            # Get sensor columns
            sensor_columns = [col for col in df.columns 
                            if col not in ['Unnamed: 0', 'source_file'] 
                            and not col.startswith('Wafer')]
            
            features = df[sensor_columns]
            
            # Convert to numeric
            for col in features.columns:
                features[col] = pd.to_numeric(features[col], errors='coerce')
            
            # Handle missing features
            missing_features = set(self.feature_names) - set(features.columns)
            extra_features = set(features.columns) - set(self.feature_names)
            
            if missing_features:
                for feature in missing_features:
                    features[feature] = 0
            
            if extra_features:
                features = features.drop(columns=list(extra_features))
            
            # Reorder columns
            features = features[self.feature_names]
            
            # Handle missing values
            features = features.fillna(features.median()).fillna(0)
            
            # Scale features
            if self.scaler:
                scaled_features = self.scaler.transform(features)
                features_scaled = pd.DataFrame(
                    scaled_features, 
                    columns=features.columns,
                    index=features.index
                )
            else:
                features_scaled = features
            
            return features_scaled, wafer_ids
            
        except Exception as e:
            raise Exception(f"Preprocessing error: {str(e)}")
    
    def predict(self, features):
        """Make predictions using loaded models"""
        results = {}
        
        for model_name, model in self.models.items():
            try:
                predictions = model.predict(features)
                probabilities = model.predict_proba(features)[:, 1] if hasattr(model, 'predict_proba') else None
                
                results[model_name] = {
                    'predictions': predictions,
                    'probabilities': probabilities,
                    'fault_count': np.sum(predictions == 1),
                    'fault_rate': np.mean(predictions == 1) * 100
                }
                
            except Exception as e:
                results[model_name] = {'error': str(e)}
        
        return results

# Initialize the detection system
detector = WaferDetectionSystem()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """File upload page"""
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle file upload and prediction"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('upload_page'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload_page'))
        
        if file and file.filename.endswith('.csv'):
            # Save uploaded file
            filename = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load and process data
            df = pd.read_csv(filepath)
            features, wafer_ids = detector.preprocess_data(df)
            
            # Make predictions
            results = detector.predict(features)
            
            # Create results dataframe
            results_df = pd.DataFrame()
            results_df['Wafer_ID'] = wafer_ids
            
            consensus_predictions = []
            for model_name, result in results.items():
                if 'error' not in result:
                    results_df[f'{model_name}_Prediction'] = result['predictions']
                    results_df[f'{model_name}_Label'] = ['Faulty' if p == 1 else 'Good' for p in result['predictions']]
                    if result['probabilities'] is not None:
                        results_df[f'{model_name}_Probability'] = result['probabilities']
            
            # Consensus prediction
            pred_columns = [col for col in results_df.columns if col.endswith('_Prediction')]
            if len(pred_columns) > 1:
                results_df['Consensus_Prediction'] = results_df[pred_columns].mode(axis=1)[0]
                results_df['Consensus_Label'] = ['Faulty' if p == 1 else 'Good' for p in results_df['Consensus_Prediction']]
            
            # Summary statistics
            summary = {
                'total_wafers': len(results_df),
                'filename': file.filename,
                'models': {}
            }
            
            for model_name, result in results.items():
                if 'error' not in result:
                    summary['models'][model_name] = {
                        'fault_count': result['fault_count'],
                        'fault_rate': result['fault_rate'],
                        'good_count': len(features) - result['fault_count']
                    }
            
            # Save results
            results_filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results_path = os.path.join(app.config['UPLOAD_FOLDER'], results_filename)
            results_df.to_csv(results_path, index=False)
            
            return render_template('results.html', 
                                 summary=summary, 
                                 results=results_df.to_dict('records')[:50],  # Show first 50 results
                                 results_file=results_filename,
                                 analysis_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(url_for('upload_page'))
            
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    try:
        # Get recent results files
        results_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith('results_')]
        results_files.sort(reverse=True)
        
        recent_analyses = []
        for file in results_files:  # All analyses
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file)
            try:
                df = pd.read_csv(filepath)
                analysis = {
                    'filename': file,
                    'timestamp': file.split('_')[1] + '_' + file.split('_')[2].replace('.csv', ''),
                    'total_wafers': int(len(df)),
                    'faulty_wafers': int(df['Consensus_Prediction'].sum()) if 'Consensus_Prediction' in df.columns else 0,
                    'fault_rate': float(df['Consensus_Prediction'].mean() * 100) if 'Consensus_Prediction' in df.columns else 0.0
                }
                recent_analyses.append(analysis)
            except:
                continue
        
        return render_template('dashboard.html', analyses=recent_analyses)
        
    except Exception as e:
        return render_template('dashboard.html', analyses=[], error=str(e))

@app.route('/download/<filename>')
def download_file(filename):
    """Download results file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Process file
        df = pd.read_csv(file)
        features, wafer_ids = detector.preprocess_data(df)
        results = detector.predict(features)
        
        # Format response
        response = {
            'total_wafers': int(len(wafer_ids)),
            'models': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for model_name, result in results.items():
            if 'error' not in result:
                response['models'][model_name] = {
                    'fault_count': int(result['fault_count']),
                    'fault_rate': float(result['fault_rate']),
                    'good_count': int(len(features) - result['fault_count'])
                }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system_status')
def system_status():
    """System status page"""
    status = {
        'models_loaded': len(detector.models),
        'models': list(detector.models.keys()),
        'scaler_loaded': detector.scaler is not None,
        'features_count': len(detector.feature_names),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)  # MB
    }
    
    return render_template('status.html', status=status)

if __name__ == '__main__':
    print("🚀 Starting Wafer Fault Detection Web Application...")
    print(f"📊 Models loaded: {len(detector.models)}")
    print(f"🔧 Features available: {len(detector.feature_names)}")
    print("🌐 Access the application at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
