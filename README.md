# 15night

### Backend Setup
```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup
```sh
cd backend
# alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

## 頁面
base url: 15-night.xxx.com

### 登入
- 前端
  - /login
- 後端
  - /api/oauth
  - /api/oauth/callback

### 主畫面
- 後端
  - /api/block
    - 拿到什麼物品（獎品、垃圾）
    - {id=0}

### 物品欄
  - /api/backpack
    - GET 拿到背包所有的內容
  - /api/backpack/{id}
    - POST 增加背包中物品的數量

## database

### user
- 學號
- 鎬子等級 (int)
  - GET
  - POST
- 錢錢
  - GET
  - POST
- 物品欄 (放挖出來的獎品跟垃圾)
  - GET
  - {1:10, 2:30,...}

### prize
- 每個獎品&數量
- 是否啟用
