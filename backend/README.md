# 15 Night Backend API (v1.0.0)

Base URL: `/api`

---

## Authentication

### POST /api/token

Login for Access Token

Request (x-www-form-urlencoded):

```json
{
  "username": "your_id",
  "password": "your_password"
}
```

Response (200):

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

## OAuth

### GET /api/oauth/login

Redirect to NYCU OAuth login

### GET /api/oauth/callback

Handle OAuth redirect

Query:

```
?code=abc123&state=xyz
```

Response (200):

```json
{
  "message": "OAuth login success",
  "access_token": "string"
}
```

---

## User

### GET /api/user/stats

Response:

```json
{
  "student_id": "string",
  "money": 100,
  "shovel_level": 1
}
```

### POST /api/user/upgrade-shovel

Response:

```json
{
  "message": "Shovel upgraded",
  "new_level": 2
}
```

### GET /api/user/backpack

Response:

```json
[
  {
    "id": 1,
    "name": "Block A",
    "quantity": 3
  }
]
```

---

## Blocks

### GET /api/blocks/available

Response:

```json
[
  {
    "id": 1,
    "name": "Iron Ore",
    "type": "metal",
    "enabled": true
  }
]
```

### POST /api/blocks/{block_id}/start

Response:

```json
{
  "message": "Mining started"
}
```

### POST /api/blocks/{block_id}/complete

Response:

```json
{
  "message": "Mining complete",
  "item": {
    "id": 1,
    "name": "Iron Ore",
    "type": "metal"
  }
}
```

---

## Leaderboard

### GET /api/leaderboard?limit=10

Response:

```json
[
  {
    "student_id": "123456",
    "shovel_level": 5,
    "money": 999
  }
]
```
