# 🚀 VivikA Finance - Production Deployment Guide

This guide covers deploying the VivikA Finance application to production using Railway (backend) and Vercel (frontend).

## 📋 Prerequisites

- Git repository with your code
- Railway account (for backend API)
- Vercel account (for frontend)
- Domain name (optional)

## 🗄️ Backend Deployment (FastAPI on Railway)

### 1. Prepare Railway Deployment

1. **Connect Repository to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Create new project
   - Connect your GitHub repository
   - Select the root directory (contains `main.py`)

2. **Configure Environment Variables in Railway:**
   ```bash
   ENVIRONMENT=production
   DEBUG=false
   DATABASE_URL=sqlite:///./production.db
   ALLOWED_ORIGINS=["https://vivikafinance.vercel.app"]
   API_HOST=0.0.0.0
   PORT=8000
   ```

3. **Railway Configuration:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Health Check Path: `/api/health`

### 2. Alternative: Deploy to Render

If you prefer Render over Railway:

1. **Connect Repository to Render:**
   - Go to [Render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repository

2. **Configure in Render Dashboard:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Environment variables (same as Railway above)

### 3. Database Setup

For production database (optional):
- **SQLite (Simple)**: Already configured in DATABASE_URL
- **PostgreSQL (Recommended for scale)**: 
  ```bash
  DATABASE_URL=postgresql://user:password@host:port/dbname
  ```

### 4. Verify Backend Deployment

After deployment, test your API:
```bash
curl https://your-api-domain.railway.app/api/health
```

Expected response:
```json
{
  "status": "ok", 
  "timestamp": "2025-01-30T...",
  "environment": "production"
}
```

## 🎨 Frontend Deployment (Next.js on Vercel)

### 1. Prepare Vercel Deployment

1. **Connect Repository to Vercel:**
   - Go to [Vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set Root Directory to `frontend-modern`

2. **Configure Build Settings:**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next` (auto-detected)
   - Install Command: `npm install`

### 2. Environment Variables in Vercel

In Vercel dashboard, add these environment variables:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.railway.app
NEXT_PUBLIC_APP_NAME=VivikA Finance - Life Planning Tool
NEXT_PUBLIC_APP_VERSION=2.0.0
NEXT_PUBLIC_ENABLE_WEBSOCKETS=true
NEXT_PUBLIC_ENABLE_MONTE_CARLO=true
NEXT_PUBLIC_ENABLE_LIFE_PLANNING=true
```

### 3. Domain Configuration (Optional)

1. **Custom Domain:**
   - In Vercel dashboard, go to Domains
   - Add your custom domain (e.g., `vivikafinance.com`)
   - Configure DNS records as instructed

2. **Update Backend CORS:**
   Update the `ALLOWED_ORIGINS` in Railway/Render:
   ```bash
   ALLOWED_ORIGINS=["https://vivikafinance.com", "https://vivikafinance.vercel.app"]
   ```

## 🔐 Security Configuration

### 1. Backend Security

Update `.env.production` values:
```bash
SECRET_KEY=your-secure-random-secret-key-here
ALLOWED_ORIGINS=["https://your-actual-frontend-domain.com"]
```

### 2. Frontend Security

- All sensitive config is handled via environment variables
- API calls use HTTPS in production
- CORS properly configured

## 📊 Monitoring & Logging

### 1. Application Monitoring

**Railway/Render provide:**
- Built-in logging
- Performance metrics  
- Uptime monitoring
- Auto-scaling

**Vercel provides:**
- Analytics dashboard
- Performance insights
- Build logs
- Error tracking

### 2. Custom Monitoring (Optional)

Add monitoring services:
- **Uptime**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry
- **Analytics**: Google Analytics, Mixpanel

## 🧪 Testing Production Deployment

### 1. Backend Tests
```bash
# Health check
curl https://your-api.railway.app/api/health

# List scenarios
curl https://your-api.railway.app/api/dynamic-scenarios

# Generate scenario
curl -X POST https://your-api.railway.app/api/scenarios/generate \
  -H "Content-Type: application/json" \
  -d '{"location": "Mn", "spouse1Status": "Work", "spouse2Status": "Work", "housing": "Own", "schoolType": "Public", "projectionYears": 8}'
```

### 2. Frontend Tests
- Visit your Vercel URL
- Test scenario creation
- Verify API connectivity
- Check life planning features

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Check `ALLOWED_ORIGINS` in backend
   - Verify frontend URL is correct

2. **API Connection Failed:**
   - Check `NEXT_PUBLIC_API_URL` in frontend
   - Verify backend is deployed and healthy

3. **Build Failures:**
   - Check logs in Railway/Render/Vercel dashboards
   - Verify all dependencies in requirements.txt/package.json

4. **Database Issues:**
   - Check DATABASE_URL format
   - Verify database connectivity

### Getting Help

- Check deployment logs in platform dashboards
- Verify environment variables are set correctly
- Test API endpoints individually
- Check network connectivity between services

## 🎯 Production Checklist

- [ ] Backend deployed to Railway/Render
- [ ] Frontend deployed to Vercel  
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health checks passing
- [ ] Database connectivity verified
- [ ] All features tested in production
- [ ] Domain configured (optional)
- [ ] SSL certificates active
- [ ] Monitoring configured

## 🔄 Continuous Deployment

Both Railway and Vercel support automatic deployments:
- **Push to main branch** → Automatic production deployment
- **Push to develop branch** → Preview deployment (Vercel)
- **Pull requests** → Preview deployments for testing

Your VivikA Finance application is now live and accessible to users worldwide! 🌟