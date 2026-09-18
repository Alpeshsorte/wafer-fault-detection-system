# 🔬 Wafer Fault Detection System

An end-to-end Machine Learning application for detecting faulty semiconductor wafers using sensor data, advanced preprocessing techniques, and classification models such as Random Forest and XGBoost.

The project includes a Flask-based web interface that allows users to upload wafer sensor data, generate predictions, view prediction probabilities, analyze fault rates, and compare model results.

---

## 📌 Project Overview

Manufacturing semiconductor wafers requires accurate quality monitoring to identify defective wafers at an early stage.

This project uses machine learning to classify wafers into:

* ✅ Normal Wafer
* ❌ Faulty Wafer

The system processes sensor data, applies preprocessing and scaling, and uses trained machine learning models to generate predictions through a user-friendly Flask web application.

---

## 🚀 Key Features

* Upload wafer sensor data through CSV files
* Automated data preprocessing
* Missing-value handling
* Feature alignment with training data
* RobustScaler-based feature scaling
* Fault prediction using Random Forest
* Fault prediction using XGBoost
* Prediction probability analysis
* Faulty wafer count and fault-rate calculation
* Consensus prediction from multiple models
* High-risk wafer identification
* Prediction result export
* Flask-based web interface
* Data visualization and feature importance analysis
* Reusable trained models without retraining

---

## 🧠 Machine Learning Workflow

```text
Raw Wafer Sensor Data
        ↓
Data Validation
        ↓
Missing Value Handling
        ↓
Feature Alignment
        ↓
Data Preprocessing
        ↓
RobustScaler Transformation
        ↓
Random Forest / XGBoost Models
        ↓
Fault Prediction
        ↓
Prediction Analytics
        ↓
Flask Web Interface
```

---

## 🛠️ Technologies Used

### Programming Language

* Python

### Machine Learning & Data Science

* Pandas
* NumPy
* Scikit-learn
* XGBoost
* Random Forest
* RobustScaler
* Feature Engineering
* Data Preprocessing

### Backend & Web

* Flask
* HTML
* CSS
* JavaScript

### Model Persistence

* Joblib
* Pickle

### Development Tools

* Git
* GitHub
* VS Code

---

## 📂 Project Structure

```text
Project/
│
├── app.py
├── wafer_ml_training.py
├── wafer_prediction.py
├── requirements.txt
│
├── DATASET.md
├── PROJECT.md
├── README.md
│
├── templates/
│   └── HTML templates
│
├── static/
│   └── CSS, JavaScript, and visual assets
│
├── Training_Batch_Files/
│   └── Training datasets
│
├── Prediction_Batch_files/
│   └── Prediction datasets
│
├── wafer_random_forest_model.pkl
├── wafer_xgboost_model.pkl
├── wafer_scaler.pkl
├── feature_names.txt
├── sensor_name_mapping.csv
│
└── test_wafer_data.csv
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Alpeshsorte/wafer-fault-detection-system.git
```

### 2. Navigate to the Project Directory

```bash
cd wafer-fault-detection-system/Project
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 📊 Application Capabilities

The application provides:

| Feature                | Description                                   |
| ---------------------- | --------------------------------------------- |
| CSV Upload             | Upload wafer sensor data                      |
| Data Processing        | Automatically preprocess input data           |
| Model Prediction       | Predict normal or faulty wafers               |
| Prediction Probability | Display model confidence                      |
| Fault Analytics        | Calculate faulty wafer count and percentage   |
| Consensus Prediction   | Compare predictions from multiple models      |
| High-Risk Analysis     | Identify wafers with higher fault probability |
| Export Results         | Save prediction results for further analysis  |

---

## 🧪 Machine Learning Models

### Random Forest

Random Forest uses multiple decision trees to improve classification performance and reduce overfitting.

### XGBoost

XGBoost is a gradient boosting algorithm designed for efficient and accurate classification tasks.

Both models are used to identify potential faults in semiconductor wafer sensor data.

---

## 📈 Data Analysis

The project also includes:

* Exploratory Data Analysis
* Feature importance visualization
* Sensor feature analysis
* Prediction result analysis
* High-risk wafer reports
* Summary reports

---

## 🎯 Project Objectives

* Detect defective semiconductor wafers automatically
* Reduce manual quality inspection effort
* Improve manufacturing quality monitoring
* Provide explainable prediction analytics
* Build a reusable machine learning prediction pipeline
* Deploy machine learning models through a web application

---

## 🔮 Future Improvements

* Deploy the application on cloud platforms
* Add real-time sensor data monitoring
* Implement model performance dashboard
* Add authentication and user management
* Add database integration
* Improve model evaluation with additional metrics
* Add automated model retraining
* Implement Docker deployment
* Add REST API endpoints for external applications

---

## 👨‍💻 Author

**Alpesh Sorte**

Python Developer | AI/ML Enthusiast | Full Stack Developer

* GitHub: [Alpeshsorte](https://github.com/Alpeshsorte)
* Location: Nagpur, India

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ star on GitHub.
