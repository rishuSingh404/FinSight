# Financial Analytics Dashboard

A comprehensive financial data analysis and risk prediction platform with an improved, modern user interface.

## 🚀 Recent Improvements

### Frontend UX Enhancements
- **Unified Workflow**: Streamlined 4-step process (Upload → Analyze → Predict → Results)
- **Modern UI**: Glassmorphism design with smooth animations and better visual hierarchy
- **Progress Tracking**: Visual progress indicator showing current step
- **Auto-advancement**: Automatic progression between steps for smoother workflow
- **Real-time Status**: API health monitoring and connection status
- **Responsive Design**: Better mobile and desktop experience
- **Interactive Elements**: Hover effects, smooth transitions, and better button styling

### Backend Fixes
- **Fixed Monitoring Service**: Resolved format string error in system metrics logging
- **Added Missing Endpoints**: 
  - `/api/v1/analyze` - POST endpoint for analysis with type selection
  - `/api/v1/predict` - POST endpoint for predictions with type selection
- **Improved Error Handling**: Better error messages and status codes
- **Health Check**: Enhanced health endpoint with detailed service status

## 🏗️ Architecture

### Frontend (Streamlit)
- **Modern UI Components**: Custom CSS with glassmorphism effects
- **Step-by-Step Workflow**: Intuitive 4-step process
- **Real-time Updates**: Live status indicators and progress tracking
- **Interactive Visualizations**: Plotly charts with modern styling

### Backend (FastAPI)
- **RESTful API**: Clean, documented endpoints
- **Caching Layer**: Redis-based caching for performance
- **Monitoring**: Real-time system and request metrics
- **Authentication**: JWT-based security
- **File Processing**: Support for CSV, TXT, PDF, and Excel files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Financial_Dashboard-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend API**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start the frontend dashboard**
   ```bash
   streamlit run frontend/dashboard.py --server.port 8503
   ```

5. **Access the application**
   - Frontend: http://localhost:8503
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Features

### 1. File Upload & Processing
- Support for multiple file formats (CSV, TXT, PDF, Excel)
- Automatic file validation and metadata extraction
- File size limits and security checks

### 2. Data Analysis
- **Basic Analysis**: Statistical summaries and data quality assessment
- **Sentiment Analysis**: Text sentiment scoring and analysis
- **Topic Extraction**: Key topic identification from text data
- **Text Summarization**: Automated document summarization

### 3. Risk Prediction
- **Risk Assessment**: Financial risk scoring with confidence levels
- **Trend Prediction**: Market trend forecasting
- **Anomaly Detection**: Identification of unusual patterns

### 4. Results Dashboard
- **Comprehensive Overview**: Summary of all analysis and predictions
- **Interactive Visualizations**: Charts and graphs for data exploration
- **Export Capabilities**: Download results and reports
- **Sharing Features**: Share analysis reports with stakeholders

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/v1/upload` - Upload financial data files
- `POST /api/v1/analyze` - Perform data analysis
- `POST /api/v1/predict` - Generate risk predictions
- `GET /health` - API health check

### Analysis Endpoints
- `GET /api/v1/analysis/{file_id}` - Get analysis results
- `POST /api/v1/analysis/{file_id}` - Force re-run analysis
- `GET /api/v1/analysis/{file_id}/enhanced` - Enhanced analysis with ML
- `GET /api/v1/analysis/{file_id}/summary` - Analysis summary

### Prediction Endpoints
- `POST /api/v1/predict/{file_id}` - Basic risk prediction
- `POST /api/v1/predict/{file_id}/enhanced` - Enhanced prediction
- `GET /api/v1/predict/{file_id}/summary` - Prediction summary
- `GET /api/v1/predict/{file_id}/compare` - Compare predictions

## 🎨 UI/UX Improvements

### Design Philosophy
- **Minimalist**: Clean, uncluttered interface
- **Intuitive**: Logical flow and clear navigation
- **Responsive**: Works seamlessly on all devices
- **Accessible**: High contrast and readable typography

### Key UI Components
- **Glassmorphism Cards**: Semi-transparent cards with blur effects
- **Gradient Buttons**: Modern button styling with hover effects
- **Progress Indicators**: Visual feedback for multi-step processes
- **Status Indicators**: Real-time connection and processing status
- **Interactive Charts**: Plotly visualizations with modern styling

### Workflow Improvements
1. **Upload Step**: Drag-and-drop interface with file validation
2. **Analysis Step**: Type selection with clear descriptions
3. **Prediction Step**: ML model selection with confidence indicators
4. **Results Step**: Tabbed interface for different result types

## 🔍 Monitoring & Health

### System Monitoring
- Real-time CPU, memory, and disk usage tracking
- Request/response time monitoring
- Error rate tracking and alerting
- Performance metrics and thresholds

### Health Checks
- API endpoint availability
- Service status monitoring
- Cache service health
- Database connectivity

## 🛠️ Development

### Project Structure
```
Financial_Dashboard-main/
├── app/                    # Backend application
│   ├── api/               # API versioning
│   ├── database/          # Database models and connections
│   ├── routers/           # API route handlers
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── frontend/              # Streamlit frontend
├── datasets/              # Sample data files
├── models/                # ML model files
├── tests/                 # Test suite
└── uploads/               # File upload directory
```

### Adding New Features
1. **Backend**: Add new endpoints in `app/routers/`
2. **Services**: Implement business logic in `app/services/`
3. **Frontend**: Add new UI components in `frontend/dashboard.py`
4. **Testing**: Add tests in `tests/` directory

## 📈 Performance

### Optimization Features
- **Caching**: Redis-based result caching
- **Async Processing**: Non-blocking API operations
- **File Streaming**: Efficient large file handling
- **Connection Pooling**: Database connection optimization

### Scalability
- **Microservices Ready**: Modular architecture
- **Load Balancing**: Horizontal scaling support
- **Monitoring**: Performance tracking and alerting
- **Caching Strategy**: Multi-level caching approach

## 🔒 Security

### Security Features
- **File Validation**: Type and size checking
- **Input Sanitization**: XSS and injection prevention
- **Rate Limiting**: API abuse prevention
- **Authentication**: JWT-based access control

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health endpoint at `/health`

---

**Note**: This is a demonstration project showcasing modern financial analytics capabilities with improved user experience and robust backend architecture.


