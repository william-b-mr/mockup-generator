# Railway Deployment Guide

Complete guide for deploying the MBC Catalog Generator to Railway.

## Architecture Overview

This application consists of two services:
- **Backend**: FastAPI application (Python)
- **Frontend**: React/Vite SPA (Node.js)

Both services are configured in `railway.toml` for automatic deployment.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional but recommended):
   ```bash
   npm install -g @railway/cli
   ```
3. **Git Repository**: Push your code to GitHub/GitLab/Bitbucket
4. **External Services Ready**:
   - Supabase project (PostgreSQL + Storage)
   - n8n workflows deployed and accessible
   - Google API key

## Step-by-Step Deployment

### 1. Initial Setup

#### Option A: Using Railway CLI
```bash
# Login to Railway
railway login

# Initialize project (from repo root)
cd /path/to/mockup_generator
railway init

# Link to your project
railway link
```

#### Option B: Using Railway Dashboard
1. Go to [railway.app/new](https://railway.app/new)
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your repository
4. Select the `mockup_generator` repository

### 2. Configure Services

Railway will automatically detect the `railway.toml` and create two services:
- `backend`
- `frontend`

### 3. Environment Variables

#### Backend Service Environment Variables

Navigate to Backend service → Variables tab and add:

```bash
# Database (Supabase PostgreSQL)
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Google API
GOOGLE_API_KEY=your_google_api_key

# Supabase Storage
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
STORAGE_BUCKET_NAME=catalog-assets

# n8n Webhooks
N8N_WEBHOOK_BASE_URL=https://your-n8n-instance.app.n8n.cloud/webhook
N8N_LOGO_PROCESSING_WEBHOOK=logo-processing
N8N_PAGE_GENERATOR_WEBHOOK=page-generator
N8N_FRONT_PAGE_IMAGE_WEBHOOK=first-page-image

# Redis (if using Railway Redis addon)
REDIS_URL=${{Redis.REDIS_URL}}

# Application Config
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.railway.app

# Railway provides PORT automatically
PORT=${{PORT}}
```

#### Frontend Service Environment Variables

Navigate to Frontend service → Variables tab and add:

```bash
# API URL (use your backend Railway URL)
VITE_API_URL=https://your-backend.railway.app/api

# Railway provides PORT automatically
PORT=${{PORT}}
```

### 4. Deploy

#### Using Railway CLI
```bash
# Deploy both services
railway up

# Or deploy specific service
railway up --service backend
railway up --service frontend
```

#### Using Git Push (Auto-deploy)
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

Railway will automatically detect changes and redeploy.

### 5. Post-Deployment Configuration

#### Update CORS Origins
After deployment, update the backend's `ALLOWED_ORIGINS` with the actual frontend URL:
1. Copy the frontend service URL from Railway dashboard
2. Update backend environment variable: `ALLOWED_ORIGINS=https://your-frontend-xxxxx.railway.app`
3. Redeploy backend service

#### Update Frontend API URL
Ensure the frontend's `VITE_API_URL` points to the backend:
1. Copy the backend service URL from Railway dashboard
2. Update frontend environment variable: `VITE_API_URL=https://your-backend-xxxxx.railway.app/api`
3. Redeploy frontend service

### 6. Verify Deployment

#### Backend Health Check
```bash
curl https://your-backend.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-10-20T10:00:00.000Z"
}
```

#### Frontend Access
Open browser to: `https://your-frontend.railway.app`

#### API Documentation
Access Swagger UI: `https://your-backend.railway.app/api/docs`

## Database Setup

Ensure your Supabase database has the required tables:

```sql
-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL,
    catalog_type VARCHAR(50) NOT NULL,
    logo_url TEXT,
    items JSONB,
    progress INTEGER DEFAULT 0,
    pdf_url TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
```

## Storage Bucket Setup

In Supabase Storage:
1. Create bucket named `catalog-assets`
2. Set bucket to **Public** (or configure appropriate policies)
3. Create folders:
   - `logos/`
   - `logos/large/`
   - `logos/small/`
   - `catalogs/`
   - `pages/`

## Optional: Add Redis

For job caching and rate limiting:

1. In Railway dashboard, click "+ New"
2. Select "Database" → "Redis"
3. Railway will automatically inject `${{Redis.REDIS_URL}}`
4. Backend will use it automatically via `REDIS_URL` env var

## Monitoring & Logs

### View Logs
```bash
# Backend logs
railway logs --service backend

# Frontend logs
railway logs --service frontend
```

### Railway Dashboard
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history
- View service metrics

## Troubleshooting

### Backend Won't Start
1. Check logs: `railway logs --service backend`
2. Verify all environment variables are set
3. Ensure DATABASE_URL is correct
4. Test database connection from local machine

### Frontend Can't Connect to API
1. Verify `VITE_API_URL` is set correctly
2. Check backend `ALLOWED_ORIGINS` includes frontend URL
3. Ensure backend is running and healthy
4. Check browser console for CORS errors

### Database Connection Issues
1. Verify Supabase PostgreSQL is accessible
2. Check firewall rules (Railway IPs might need whitelisting)
3. Test connection string format
4. Ensure database exists and has required tables

### n8n Webhooks Failing
1. Verify n8n workflows are active
2. Check webhook URLs are correct
3. Ensure n8n instance is publicly accessible
4. Test webhooks manually using curl/Postman

## Cost Optimization

Railway pricing is based on resource usage:

### Estimated Monthly Costs (Hobby Plan - $5 credit/month)
- Backend: ~$3-8/month (depending on traffic)
- Frontend: ~$2-5/month (static serving is cheap)
- Redis (optional): ~$1-3/month

### Tips to Reduce Costs:
1. Use Railway's sleep feature for non-prod environments
2. Optimize backend cold start time
3. Enable Railway's autoscaling
4. Monitor resource usage in dashboard

## Updating the Application

### Deploy New Changes
```bash
# Commit changes
git add .
git commit -m "Your changes"
git push origin main

# Railway auto-deploys on push
```

### Manual Redeploy
```bash
railway up --service backend
railway up --service frontend
```

### Rollback to Previous Deployment
1. Go to Railway dashboard
2. Navigate to Deployments tab
3. Click "Rollback" on previous successful deployment

## Custom Domain (Optional)

### Add Custom Domain to Frontend
1. In Railway dashboard, go to Frontend service
2. Click "Settings" → "Domains"
3. Click "Add Domain"
4. Enter your domain (e.g., `catalog.yourdomain.com`)
5. Update DNS records as instructed by Railway
6. Update backend's `ALLOWED_ORIGINS` to include custom domain

### Add Custom Domain to Backend
1. In Railway dashboard, go to Backend service
2. Click "Settings" → "Domains"
3. Click "Add Domain"
4. Enter your domain (e.g., `api.yourdomain.com`)
5. Update DNS records as instructed by Railway
6. Update frontend's `VITE_API_URL` to use custom domain

## Security Checklist

- [ ] All environment variables are set correctly
- [ ] Supabase service role key is kept secret
- [ ] CORS origins are restricted to your frontend domains only
- [ ] Database has proper indexes
- [ ] API rate limiting is configured (if needed)
- [ ] n8n webhooks are secured (authentication if possible)
- [ ] Error messages don't expose sensitive information
- [ ] Logs don't contain secrets

## Backup Strategy

### Database Backups
- Supabase automatically backs up your PostgreSQL database
- Configure backup retention in Supabase dashboard

### Storage Backups
- Use Supabase Storage replication
- Consider periodic exports of critical assets

## Support & Resources

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Supabase Documentation: https://supabase.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- Vite Documentation: https://vitejs.dev

## Quick Reference Commands

```bash
# Login to Railway
railway login

# View service status
railway status

# View logs
railway logs

# Open dashboard
railway open

# SSH into service (for debugging)
railway shell

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# Delete environment variable
railway variables delete KEY
```
