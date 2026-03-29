# Deployment Guide - Vercel + Render

## 📋 Tổng Quan

- **Frontend**: Deploy lên Vercel (static/edge)
- **Backend**: Deploy lên Render.com (Python/FastAPI)
- **Database**: MongoDB Atlas (cloud)

## 🚀 Step 1: Setup MongoDB Atlas (Cloud Database)

1. Tạo account tại [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Tạo cluster (free tier đủ dùng)
3. Tạo database user và lấy connection string
4. Copy connection string, sẽ dùng ở bước tiếp

Ex: `mongodb+srv://user:pass@cluster.mongodb.net/shopping_list`

## 🔧 Step 2: Deploy Backend trên Render.com

### 2.1 Setup Render account
1. Tạo account tại [Render.com](https://render.com)
2. Connect GitHub account

### 2.2 Create Web Service
1. Vào Dashboard → New → Web Service
2. Select repository: `shopping-list`
3. Cấu hình:
   - **Name**: `shopping-list-api`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 2.3 Add Environment Variables
Vào Settings → Environment:
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/shopping_list?retryWrites=true&w=majority
DB_NAME=shopping_list
FRONTEND_URL=https://shopping-list-app.vercel.app
```

### 2.4 Deploy
Click "Deploy" → chờ build hoàn thành

**Backend URL**: `https://shopping-list-api.onrender.com`

## 🎨 Step 3: Deploy Frontend trên Vercel

### 3.1 Setup Vercel account
1. Tạo account tại [Vercel.com](https://vercel.com)
2. Connect GitHub account

### 3.2 Import Project
1. Vào Dashboard → Add New → Project
2. Select repository: `shopping-list`
3. Cấu hình:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.3 Add Environment Variables
Vào Settings → Environment Variables:
```
VITE_API_URL=https://shopping-list-api.onrender.com/api
```

### 3.4 Deploy
Click "Deploy" → chờ build hoàn thành

**Frontend URL**: `https://shopping-list-app.vercel.app`

## ✅ Verification

1. Test backend health check:
   ```
   curl https://shopping-list-api.onrender.com/
   ```
   Phải return `{"status": "ok", "app": "Shopping List API"}`

2. Seed milestones (chạy 1 lần):
   ```bash
   # SSH vào Render hoặc run terminal command
   python seed_pregnancy_calendar.py
   ```

3. Test frontend:
   - Mở https://shopping-list-app.vercel.app
   - Navigate đến tab Calendar
   - Verify dữ liệu load từ API

## 🔄 Continuous Deployment

- **Auto-deploy**: Khi push lên `main` branch, cả Render và Vercel sẽ tự deploy
- **Rollback**: Có thể rollback qua dashboard nếu có issue

## 📝 Environment Variables Summary

**Backend (Render)**:
```
MONGODB_URL=...
DB_NAME=shopping_list
FRONTEND_URL=https://shopping-list-app.vercel.app
```

**Frontend (Vercel)**:
```
VITE_API_URL=https://shopping-list-api.onrender.com/api
```

## 🆘 Troubleshooting

### Frontend không connect backend
- Kiểm tra VITE_API_URL đúng
- Check CORS settings ở backend (main.py)
- Verify backend server đang chạy

### MongoDB connection failed
- Kiểm tra connection string
- Verify IP whitelist ở MongoDB Atlas
- Check username/password đúng

### Build failed trên Render
- Check buildlogs
- Verify requirements.txt up-to-date
- Check Python version support

## 💰 Cost Estimate (Free Tier)

- MongoDB Atlas: Free (512MB storage)
- Render: Free ($0/month cho Python app)
- Vercel: Free (unlimited deployments)

**Total: $0/month** ✨

---

**Happy Deployment!** 🎉
