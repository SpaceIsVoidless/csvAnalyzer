# 🔍 Activity Analyzer

The Activity Analyzer is a powerful web-based application that helps you analyze user activity data from CSV files. It provides valuable insights into user actions and automatically flags suspicious activities based on predefined criteria.

## ✨ Features

- 📤 Upload CSV files containing user activity data
- 📊 Analyze and display the top 5 users by action count
- 🚨 Detect suspicious activities (same action > 10 times within 5 minutes)
- 🖥️ Interactive web interface for easy data upload and analysis

## 🛠️ Prerequisites

- Python 3.x
- Required Python packages:
  - `http.server`
  - `socketserver`
  - `json`
  - `urllib`
  - `os`
  - `io`
  - `sys`
  - `email`
  - `tempfile`
  - `collections`
  - `datetime`
  - `csv`
  - `typing`
  - `operator`

## 🚀 Installation

1. Clone the repository or download the source code
2. Navigate to the project directory

## 💻 Usage

### Starting the Server

To start the web server and begin analyzing activity data, run:

```bash
python web_analyzer.py
```

### Generating Test Data

To generate sample test data for analysis:

```bash
python generate_test_data.py
```

## 📝 Note

Make sure all required Python packages are installed before running the application. The application will automatically detect suspicious activities and provide detailed analysis of user behavior patterns.