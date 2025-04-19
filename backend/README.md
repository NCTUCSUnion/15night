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

---

## Admin

### POST /api/admin/blocks

Request:

```json
{
  "name": "Gold",
  "type": "metal",
  "enabled": true,
  "prize_chance": 30,
  "quantity": 10
}
```

Response:

```json
{
  "id": 3,
  "message": "Block created"
}
```

### PUT /api/admin/blocks/{block_id}

Request:

```json
{
  "name": "Silver",
  "enabled": false
}
```

### PUT /api/admin/blocks/{block_id}/quantity

Request:

```json
{
  "quantity": 50
}
```

### PUT /api/admin/blocks/type/{type_name}/toggle

Request:

```json
{
  "enabled": true
}
```

### POST /api/admin/seed

Response:

```json
{
  "message": "Seeded"
}
```

### GET /api/admin/users

Response:

```json
[
  {
    "student_id": "123456",
    "is_admin": false
  }
]
```

### PUT /api/admin/users/{student_id}/set-admin

Request:

```json
{
  "is_admin": true
}
```

Response:

```json
{
  "message": "User updated"
}
```
