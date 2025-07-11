# Deployment Guide - Financial Analytics API

## 🚀 Quick Deployment Options

### Option 1: Render (Recommended for SDE Portfolio)

#### Step 1: Prepare Your Repository
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial SDE portfolio project"
   git push origin main
   ```

2. **Verify Repository Structure**
   ```
   financial-analytics-api/
   ├── app/
   ├── frontend/
   ├── tests/
   ├── Dockerfile
   ├── docker-compose.yml
   ├── requirements.txt
   └── README.md
   ```

#### Step 2: Deploy on Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub account

2. **Deploy API Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure settings:
     ```
     Name: financial-analytics-api
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Set Environment Variables**
   ```
   DATABASE_URL=sqlite:///./financial_analytics.db
   SECRET_KEY=your-production-secret-key
   UPLOAD_PATH=./uploads/
   MODEL_PATH=./models/
   ```

4. **Deploy Frontend Service**
   - Click "New +" → "Web Service"
   - Same repository, different settings:
     ```
     Name: financial-analytics-frontend
     Build Command: pip install streamlit plotly
     Start Command: streamlit run frontend/dashboard.py --server.port $PORT --server.address 0.0.0.0
     ```

#### Step 3: Test Deployment
1. **API Health Check**
   ```bash
   curl https://your-api-name.onrender.com/health
   ```

2. **Frontend Access**
   - Visit: `https://your-frontend-name.onrender.com`

### Option 2: Docker Compose (Local/Server)

#### Step 1: Build and Run
```bash
# Build all services
docker-compose up --build

# Run in background
docker-compose up -d
```

#### Step 2: Access Services
- API: http://localhost:8000
- Frontend: http://localhost:8501
- Database: localhost:5432

### Option 3: Heroku

#### Step 1: Install Heroku CLI
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

#### Step 2: Deploy
```bash
heroku create your-app-name
git push heroku main
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=sqlite:///./financial_analytics.db
SECRET_KEY=your-secret-key

# Optional
UPLOAD_PATH=./uploads/
MODEL_PATH=./models/
LOG_LEVEL=INFO
```

### Database Setup
```bash
# For production (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# For development (SQLite)
DATABASE_URL=sqlite:///./financial_analytics.db
```

## 📊 Monitoring

### Health Checks
```bash
# API Health
curl https://your-api.onrender.com/health

# Expected Response
{
  "status": "healthy",
  "service": "Financial Analytics API"
}
```

### Logs
```bash
# Render logs
# Available in Render dashboard

# Docker logs
docker-compose logs api
docker-compose logs frontend
```

## 🧪 Testing Deployment

### 1. Test API Endpoints
```bash
# Health check
curl https://your-api.onrender.com/health

# Upload file
curl -X POST "https://your-api.onrender.com/api/v1/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test.csv"

# Get analysis
curl -X GET "https://your-api.onrender.com/api/v1/analysis/{file_id}"

# Get prediction
curl -X POST "https://your-api.onrender.com/api/v1/predict/{file_id}"
```

### 2. Test Frontend
- Visit your frontend URL
- Upload a test file
- Run analysis and predictions
- Verify visualizations work

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Check requirements.txt
pip install -r requirements.txt
```

#### 2. Database Connection
```bash
# Solution: Check DATABASE_URL
# For SQLite: sqlite:///./financial_analytics.db
# For PostgreSQL: postgresql://user:pass@host:port/db
```

#### 3. File Upload Issues
```bash
# Solution: Check UPLOAD_PATH
# Ensure directory exists and is writable
mkdir -p uploads
chmod 755 uploads
```

#### 4. Port Issues
```bash
# Solution: Use $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Debug Commands
```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

## 📈 Performance Optimization

### For Production
1. **Database**
   - Use PostgreSQL instead of SQLite
   - Add connection pooling
   - Implement caching

2. **File Storage**
   - Use cloud storage (S3, Azure)
   - Implement CDN for static files

3. **API Optimization**
   - Add Redis caching
   - Implement rate limiting
   - Use async processing

## 🔒 Security Checklist

### Before Production
- [ ] Change default SECRET_KEY
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Add input validation
- [ ] Implement authentication
- [ ] Set up monitoring

## 📞 Support

### Getting Help
1. Check logs in deployment platform
2. Verify environment variables
3. Test locally first
4. Check GitHub issues

### Useful Commands
```bash
# Local testing
uvicorn app.main:app --reload

# Docker testing
docker-compose up --build

# Check dependencies
pip list | grep -E "(fastapi|streamlit|pandas)"
```

---

**Ready for SDE Portfolio! 🎯**

Your Financial Analytics API is now production-ready and demonstrates:
- ✅ Modern API development (FastAPI)
- ✅ Frontend development (Streamlit)
- ✅ DevOps practices (Docker, CI/CD)
- ✅ Database design (SQLAlchemy)
- ✅ Testing (pytest)
- ✅ Documentation (README, API docs)
- ✅ Cloud deployment (Render)

Perfect for showcasing your full-stack development skills! 