#!/bin/bash
# SkillSeed - Quick Start Script
# Requires Python 3.10+

echo "======================================"
echo "  SkillSeed API - Setup & Start"
echo "======================================"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi==0.111.0 uvicorn[standard]==0.29.0 \
  sqlalchemy==2.0.30 aiosqlite==0.20.0 greenlet==3.0.3 \
  python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 \
  python-multipart==0.0.9 "pydantic[email]==2.7.1" \
  pydantic-settings==2.2.1 python-dotenv==1.0.1 \
  aiofiles==23.2.1 Pillow==10.3.0

echo ""
echo "✅ Dependencies installed"
echo ""
echo "Starting SkillSeed API server..."
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔐 Admin Login:"
echo "   Email:    admin@skillseed.com"
echo "   Password: admin123"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
