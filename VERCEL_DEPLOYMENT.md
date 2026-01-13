# Vercel Deployment Guide

## ✅ Phase 1 Complete - Ready for Vercel!

This guide shows how to deploy the **frontend** to Vercel. The backend should be deployed separately (Render.com, AWS Lambda, etc.).

---

## 🚀 Quick Deploy to Vercel

### Step 1: Deploy Frontend to Vercel

1. **Push your code to GitHub** (already done! ✅)
   ```bash
   git push origin main
   ```

2. **Import project to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository: `MongoPete/ai-memory-demo`
   - Select the `figmaUI` folder as the root directory

3. **Configure Build Settings:**
   ```
   Framework Preset: Vite
   Root Directory: figmaUI
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Set Environment Variable:**
   ```
   VITE_API_BASE_URL=https://your-backend-url.render.com
   ```
   ⚠️ Replace with your actual backend URL from Render.com

5. **Deploy!** 
   - Click "Deploy"
   - Vercel will build and deploy automatically

---

## 🔧 Environment Variables

### Frontend (Vercel)

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Example |
|----------|-------|---------|
| `VITE_API_BASE_URL` | Your backend API URL | `https://ai-memory.onrender.com` |

### Backend (Render.com)

Set these in Render Dashboard → Environment Variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | ✅ | MongoDB Atlas connection string |
| `AWS_ACCESS_KEY_ID` | ✅ | AWS IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | AWS IAM user secret key |
| `AWS_REGION` | Optional | Default: `us-east-1` |
| `CORS_ORIGINS` | Optional | Your Vercel URL (e.g., `https://your-app.vercel.app`) |

---

## 🎯 Current Deployment Status

✅ **Code merged to `main` branch**
✅ **Vercel configuration ready** (`figmaUI/vercel.json`)
✅ **Environment variable system working**
✅ **CORS configured for cross-origin requests**
✅ **Production-ready features:**
   - Robust relevance scoring (55% threshold)
   - Case-insensitive search
   - Input validation
   - Global search with filtering
   - Educational score breakdowns

---

## 📋 Deployment Checklist

### Frontend (Vercel)
- [ ] Push `main` branch to GitHub
- [ ] Import project to Vercel
- [ ] Set root directory to `figmaUI`
- [ ] Add `VITE_API_BASE_URL` environment variable
- [ ] Deploy and test

### Backend (Render.com)
- [ ] Create Web Service on Render
- [ ] Connect to GitHub repository
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Add all required environment variables
- [ ] Add Vercel URL to `CORS_ORIGINS`
- [ ] Deploy and test `/health` endpoint

### Post-Deployment
- [ ] Test frontend loads on Vercel URL
- [ ] Test backend health: `https://your-backend.onrender.com/health`
- [ ] Test cross-origin requests work
- [ ] Try searching with global search
- [ ] Verify relevance scores display correctly
- [ ] Test all three demo users (Alice, Bob, Carol)

---

## 🔍 Testing Your Deployment

### 1. Test Backend Health
```bash
curl https://your-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI-Memory-Service",
  "version": "1.0",
  "dependencies": {
    "mongodb": "connected",
    "aws_bedrock": "available"
  }
}
```

### 2. Test Frontend
Visit your Vercel URL: `https://your-app.vercel.app`

- ✅ Page loads without errors
- ✅ "Healthy" status shows in header
- ✅ Can send messages
- ✅ Global search works
- ✅ Relevance scores display

### 3. Test CORS
Open browser console and check for CORS errors:
- ❌ If you see CORS errors: Add Vercel URL to `CORS_ORIGINS` on backend
- ✅ No CORS errors: Everything working!

---

## 🛠️ Troubleshooting

### Issue: "Failed to fetch" errors
**Solution:** Check `VITE_API_BASE_URL` is set correctly in Vercel
```bash
# Should be your Render backend URL
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### Issue: CORS errors
**Solution:** Add Vercel URL to backend `CORS_ORIGINS`
```python
# On Render, set environment variable:
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-preview.vercel.app
```

### Issue: "Service Unavailable"
**Solution:** Check backend is running on Render
- Visit Render dashboard
- Check logs for errors
- Verify environment variables are set

### Issue: Relevance scores not showing
**Solution:** This was fixed! Make sure you're on the latest `main` branch
```bash
git pull origin main
git push origin main  # Push to Vercel
```

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ **Fast frontend** on Vercel's global CDN
- ✅ **Scalable backend** on Render.com
- ✅ **Production-ready** MongoDB + AI demo
- ✅ **Robust filtering** (no more "pizza" = 80% relevant to "backend"!)
- ✅ **Educational** relevance scoring for learning

Share your demo: `https://your-app.vercel.app` 🚀

---

## 📚 Related Documentation

- [MongoDB Atlas Setup](docs/02-MONGODB-SETUP.md)
- [AWS Bedrock Setup](docs/04-AWS-BEDROCK.md)
- [Phase 1 Features](docs/09-PHASE1-FEATURES.md)
- [API Documentation](http://localhost:8182/docs) (when running locally)

---

**Last Updated:** January 2026  
**Branch:** `main` (Phase 1 Complete)
