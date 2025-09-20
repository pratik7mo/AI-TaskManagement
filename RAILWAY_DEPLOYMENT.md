# 🚀 Railway Deployment Guide for AI PowerTMS

This guide will help you deploy your AI PowerTMS application using Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Have your API keys ready

## 🔧 Setup Steps

### 1. Prepare Your Repository

Your repository should have the following structure:
```
AI_PowerTMS/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   └── ...
├── railway.json
├── nixpacks.toml
└── .env (create this with your variables)
```

### 2. Environment Variables

Create a `.env` file in your project root with the following variables:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/task_management
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

### 3. Deploy to Railway

1. **Connect GitHub Repository**:
   - Go to your Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `AI_PowerTMS` repository

2. **Configure Environment Variables**:
   - In your Railway project settings
   - Go to "Variables" tab
   - Add the following environment variables:
     - `DATABASE_URL` (Railway will provide a PostgreSQL database)
     - `GEMINI_API_KEY`
     - `SECRET_KEY`
     - `ENVIRONMENT=production`
     - `NEXT_PUBLIC_API_URL` (set to your Railway app URL)

3. **Deploy**:
   - Railway will automatically detect your Python/Node.js setup
   - It will use the `nixpacks.toml` configuration
   - Your app will be available at the provided URL

## 🗄️ Database Setup

Railway provides a MySQL database:

1. **Add Database Service**:
   - In your Railway project
   - Click "New" → "Database" → "MySQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

2. **Run Migrations**:
   - Railway will automatically run your database migrations
   - Check the deployment logs for any migration issues

**Note**: If Railway doesn't have MySQL available, you can:
- Use a third-party MySQL service like PlanetScale, AWS RDS, or Google Cloud SQL
- Set the `DATABASE_URL` environment variable to your external MySQL database

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check that all dependencies are in `requirements.txt` and `package.json`
   - Ensure Python 3.11+ and Node.js 18+ are specified

2. **Port Configuration**:
   - Railway automatically sets the `PORT` environment variable
   - Your app should use `PORT` instead of hardcoded ports

3. **Database Connection**:
   - Use the `DATABASE_URL` provided by Railway
   - Ensure your database models are properly configured

4. **Environment Variables**:
   - Double-check all required variables are set in Railway
   - Ensure API keys are valid

### Debug Commands:

```bash
# Check Railway logs
railway logs

# Connect to Railway shell
railway shell

# Check environment variables
railway variables
```

## 📊 Monitoring

Once deployed, you can monitor your application:

1. **Logs**: Check Railway dashboard for application logs
2. **Health**: Visit `https://your-app.railway.app/health` for backend health
3. **Metrics**: Monitor CPU, memory, and network usage

## 🔄 Updates

To update your application:

1. Push changes to your GitHub repository
2. Railway will automatically detect changes
3. It will rebuild and redeploy your application

## 📞 Support

If you encounter issues:

1. Check the Railway documentation: https://docs.railway.app
2. Review your application logs in the Railway dashboard
3. Ensure all environment variables are properly set
4. Verify your GitHub repository is properly connected

---

**Note**: This deployment configuration is optimized for Railway's native Python/Node.js support without requiring Docker.
