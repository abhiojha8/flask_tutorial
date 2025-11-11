# Whiteboard Diagrams for Authentication (Chapter 4)

These ASCII diagrams can be drawn on a whiteboard during lectures to explain authentication concepts.

---

## DIAGRAM 1: Authentication vs Authorization

**Concept:** The fundamental difference between authn and authz

```
┌────────────────────────────────────────────────────────┐
│  AUTHENTICATION vs AUTHORIZATION                       │
└────────────────────────────────────────────────────────┘

AUTHENTICATION: "Who are you?"
┌─────────────────────────────────────┐
│                                     │
│  User: "I'm John Doe"               │
│                                     │
│  System: "Prove it!"                │
│                                     │
│  User: Shows password               │
│                                     │
│  System: ✓ "Yes, you are John"      │
│                                     │
└─────────────────────────────────────┘

AUTHORIZATION: "What can you do?"
┌─────────────────────────────────────┐
│                                     │
│  John: "I want to delete this post" │
│                                     │
│  System: "Are you the author?"      │
│                                     │
│  John: "No"                         │
│                                     │
│  System: ✗ "Not authorized!"        │
│                                     │
└─────────────────────────────────────┘

REAL WORLD ANALOGY:

Airport Security:
┌──────────────────────────────────────────┐
│ AUTHENTICATION (Security Checkpoint)     │
│   • Show passport (prove identity)       │
│   • Verify name matches ticket           │
│   • ✓ You are who you claim to be        │
└──────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────┐
│ AUTHORIZATION (Boarding Gate)            │
│   • Check ticket class                   │
│   • Economy → No lounge access           │
│   • Business → Lounge access granted     │
│   • ✓ You can access what you paid for  │
└──────────────────────────────────────────┘
```

---

## DIAGRAM 2: Sessions vs Tokens

**Concept:** Traditional sessions vs modern JWT tokens

```
┌────────────────────────────────────────────────────────┐
│  SESSIONS (Traditional Web Apps)                       │
└────────────────────────────────────────────────────────┘

1. User logs in
   ↓
2. Server creates session
   ┌─────────────────────┐
   │ Server Memory/DB    │
   │ ─────────────────── │
   │ session_123:        │
   │   user_id: 5        │
   │   username: john    │
   │   role: admin       │
   │   expires: ...      │
   └─────────────────────┘
   ↓
3. Server sends session ID cookie
   ↓
4. Browser stores cookie
   ┌─────────────────┐
   │ Browser Cookies │
   │ ─────────────── │
   │ session_id: 123 │
   └─────────────────┘
   ↓
5. Every request includes cookie
   ↓
6. Server looks up session
   ┌──────────────────────────────┐
   │ Problem: Must query          │
   │ database on EVERY request!   │
   └──────────────────────────────┘

❌ Doesn't scale (need shared session store)
❌ Server must track all sessions
❌ Doesn't work well for mobile apps

┌────────────────────────────────────────────────────────┐
│  JWT TOKENS (Modern APIs)                              │
└────────────────────────────────────────────────────────┘

1. User logs in
   ↓
2. Server creates JWT token
   ┌──────────────────────────────────┐
   │ Token (self-contained):          │
   │ ──────────────────────────────── │
   │ {                                │
   │   "user_id": 5,                  │
   │   "username": "john",            │
   │   "role": "admin",               │
   │   "exp": 1234567890              │
   │ }                                │
   │ + SIGNATURE (proves authentic)   │
   └──────────────────────────────────┘
   ↓
3. Returns token to client
   ↓
4. Client stores token (localStorage)
   ┌─────────────────────────┐
   │ localStorage            │
   │ ─────────────────────── │
   │ token: "eyJhbGc..."     │
   └─────────────────────────┘
   ↓
5. Include in Authorization header
   Authorization: Bearer eyJhbGc...
   ↓
6. Server verifies signature
   ┌──────────────────────────────┐
   │ Benefit: No database lookup! │
   │ Just verify signature        │
   └──────────────────────────────┘

✅ Stateless (no server-side storage)
✅ Scales horizontally
✅ Works great for mobile/SPA
✅ Can include user data in token
```

---

## DIAGRAM 3: JWT Structure

**Concept:** The three parts of a JWT token

```
┌────────────────────────────────────────────────────────┐
│  JWT TOKEN STRUCTURE                                   │
└────────────────────────────────────────────────────────┘

A JWT has three parts separated by dots (.):

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.xyz123
└──────── HEADER ────────┘ └── PAYLOAD ──┘ └ SIGNATURE ┘

PART 1: HEADER (Algorithm & Type)
┌─────────────────────────────┐
│ {                           │
│   "alg": "HS256",          │ ← Which algorithm to use
│   "typ": "JWT"             │ ← Token type
│ }                           │
└─────────────────────────────┘
        ↓ Base64 encode
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9

PART 2: PAYLOAD (Claims/Data)
┌─────────────────────────────┐
│ {                           │
│   "user_id": 123,          │ ← Custom claim
│   "username": "john",      │ ← Custom claim
│   "role": "admin",         │ ← Custom claim
│   "exp": 1735689600       │ ← Expiration (standard)
│ }                           │
└─────────────────────────────┘
        ↓ Base64 encode
eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiam9obiJ9

⚠️  IMPORTANT: Payload is NOT encrypted!
    Anyone can decode and read it.
    Don't put passwords or sensitive data here!

PART 3: SIGNATURE (Proof of Authenticity)
┌─────────────────────────────────────────┐
│ HMACSHA256(                             │
│   base64(header) + "." + base64(payload),│
│   secret_key                            │
│ )                                       │
└─────────────────────────────────────────┘
        ↓
xyz123abc...

The signature proves:
  ✓ Token was created by us (has our secret)
  ✓ Token hasn't been tampered with

HOW VERIFICATION WORKS:

Server receives token:
┌──────────────────────────────────────┐
│ 1. Split into 3 parts                │
│                                      │
│ 2. Recreate signature using same     │
│    algorithm and secret key          │
│                                      │
│ 3. Compare signatures:               │
│    Received:  xyz123abc...           │
│    Recreated: xyz123abc...           │
│                                      │
│ 4. If match → ✓ Token is valid       │
│    If no match → ✗ Token is invalid  │
└──────────────────────────────────────┘
```

---

## DIAGRAM 4: Password Hashing with bcrypt

**Concept:** Why we never store plain-text passwords

```
┌────────────────────────────────────────────────────────┐
│  PASSWORD SECURITY: Plain Text vs Hashing             │
└────────────────────────────────────────────────────────┘

❌ NEVER DO THIS:
┌─────────────────────────────┐
│ Database (users table)      │
├──────┬──────────────────────┤
│ id   │ password             │
├──────┼──────────────────────┤
│ 1    │ password123          │ ← Anyone with DB access sees it!
│ 2    │ qwerty               │ ← If database is hacked, game over
│ 3    │ letmein              │ ← Can't be undone
└──────┴──────────────────────┘

✅ ALWAYS DO THIS (bcrypt):
┌────────────────────────────────────────────────────────┐
│ Database (users table)                                 │
├──────┬─────────────────────────────────────────────────┤
│ id   │ password_hash                                   │
├──────┼─────────────────────────────────────────────────┤
│ 1    │ $2b$12$LQv3c1yqBWVHxkd0LHAkCOem...             │
│ 2    │ $2b$12$KIRWVHxkd0LHAkCOemLQv3c1...             │
│ 3    │ $2b$12$CoemLQv3c1yqBWVHxkd0LHA...             │
└──────┴─────────────────────────────────────────────────┘
     ✓ Even if DB is hacked, passwords are safe
     ✓ One-way function (can't reverse)
     ✓ Each hash is unique (salted)

HOW BCRYPT WORKS:

Registration:
┌──────────────────────────────────────────────────┐
│ User enters: "password123"                       │
│        ↓                                         │
│ bcrypt.hashpw(password, salt)                    │
│        ↓                                         │
│ 1. Generate random salt                          │
│    salt: "$2b$12$LQv3c1yqBWVHxkd0"              │
│                                                  │
│ 2. Combine password + salt                       │
│    "password123" + salt                          │
│                                                  │
│ 3. Run through bcrypt algorithm (slow!)          │
│    ↓ (takes ~100ms deliberately)                 │
│                                                  │
│ 4. Result: Hash                                  │
│    "$2b$12$LQv3c1yqBWVHxkd0LHAkCOem..."         │
│        ↑     ↑            ↑                      │
│        │     │            └─ Hash part           │
│        │     └─ Work factor (12 = 2^12 rounds)   │
│        └─ Algorithm version                      │
│                                                  │
│ 5. Store hash in database                        │
└──────────────────────────────────────────────────┘

Login:
┌──────────────────────────────────────────────────┐
│ User enters: "password123"                       │
│        ↓                                         │
│ 1. Get stored hash from database                 │
│    stored: "$2b$12$LQv3c1yqBWVH..."             │
│                                                  │
│ 2. Extract salt from stored hash                 │
│    salt: "$2b$12$LQv3c1yqBWVHxkd0"              │
│                                                  │
│ 3. Hash entered password with same salt          │
│    bcrypt.hashpw("password123", salt)            │
│    ↓                                             │
│    new_hash: "$2b$12$LQv3c1yqBWVH..."           │
│                                                  │
│ 4. Compare hashes                                │
│    if new_hash == stored_hash:                   │
│        ✓ Password correct!                       │
│    else:                                         │
│        ✗ Password wrong!                         │
└──────────────────────────────────────────────────┘

WHY BCRYPT?

1. SLOW BY DESIGN
   ┌────────────────────────────────────┐
   │ Attacker tries to brute force:     │
   │                                    │
   │ Try "password1" → Wait 100ms       │
   │ Try "password2" → Wait 100ms       │
   │ Try "password3" → Wait 100ms       │
   │                                    │
   │ 1 billion guesses = 3 years!       │
   └────────────────────────────────────┘

2. AUTOMATIC SALTING
   ┌────────────────────────────────────┐
   │ Same password, different hashes:   │
   │                                    │
   │ User A: "password123"              │
   │ Hash: $2b$12$abc...                │
   │                                    │
   │ User B: "password123"              │
   │ Hash: $2b$12$xyz...                │
   │             ↑                      │
   │       Different salt!              │
   └────────────────────────────────────┘

3. ADJUSTABLE WORK FACTOR
   ┌────────────────────────────────────┐
   │ As computers get faster,           │
   │ increase work factor:              │
   │                                    │
   │ 2015: factor = 10 (fast enough)    │
   │ 2020: factor = 12 (CPUs faster)    │
   │ 2025: factor = 14 (even faster)    │
   └────────────────────────────────────┘
```

---

## DIAGRAM 5: Complete Registration Flow

**Concept:** Step-by-step user registration

```
┌────────────────────────────────────────────────────────┐
│  USER REGISTRATION FLOW                                │
└────────────────────────────────────────────────────────┘

CLIENT                         SERVER
  │                              │
  │ 1. POST /auth/register       │
  │    {                         │
  │      username: "john",       │
  │      email: "john@ex.com",   │
  │      password: "Pass123"     │
  │    }                         │
  ├──────────────────────────────>│
  │                              │
  │                              │ 2. Validate email format
  │                              │    ┌──────────────────┐
  │                              │    │ Regex check      │
  │                              │    │ Must contain @   │
  │                              │    └──────────────────┘
  │                              │    ✓ john@ex.com is valid
  │                              │
  │                              │ 3. Validate password strength
  │                              │    ┌──────────────────┐
  │                              │    │ Min 8 chars      │
  │                              │    │ Has letter       │
  │                              │    │ Has number       │
  │                              │    └──────────────────┘
  │                              │    ✓ Pass123 is valid
  │                              │
  │                              │ 4. Check for duplicates
  │                              │    ┌──────────────────────────┐
  │                              │    │ SELECT * FROM users      │
  │                              │    │ WHERE username = 'john'  │
  │                              │    └──────────────────────────┘
  │                              │    ✓ No duplicates
  │                              │
  │                              │ 5. Hash password
  │                              │    ┌──────────────────────────┐
  │                              │    │ bcrypt.hashpw(           │
  │                              │    │   "Pass123",             │
  │                              │    │   salt                   │
  │                              │    │ )                        │
  │                              │    │ ↓                        │
  │                              │    │ $2b$12$LQv3c1yq...       │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 6. Create user record
  │                              │    ┌──────────────────────────┐
  │                              │    │ INSERT INTO users (      │
  │                              │    │   username,              │
  │                              │    │   email,                 │
  │                              │    │   password_hash,         │
  │                              │    │   role,                  │
  │                              │    │   created_at             │
  │                              │    │ ) VALUES (...)           │
  │                              │    └──────────────────────────┘
  │                              │
  │ 7. 201 Created               │
  │    {                         │
  │      id: 5,                  │
  │      username: "john",       │
  │      email: "john@ex.com",   │
  │      role: "reader",         │
  │      created_at: "2024-..."  │
  │    }                         │
  │<──────────────────────────────┤
  │                              │

ERROR SCENARIOS:

1. Invalid Email:
   "invalid-email" → ✗ 400 Bad Request
                     {"error": "Invalid email format"}

2. Weak Password:
   "pass" → ✗ 400 Bad Request
            {"error": "Password must be at least 8 characters"}

3. Duplicate Username:
   "john" (exists) → ✗ 409 Conflict
                     {"error": "Username already exists"}

4. Duplicate Email:
   "john@ex.com" (exists) → ✗ 409 Conflict
                            {"error": "Email already exists"}
```

---

## DIAGRAM 6: Complete Login Flow

**Concept:** Step-by-step user login with JWT

```
┌────────────────────────────────────────────────────────┐
│  USER LOGIN FLOW                                       │
└────────────────────────────────────────────────────────┘

CLIENT                         SERVER
  │                              │
  │ 1. POST /auth/login          │
  │    {                         │
  │      email: "john@ex.com",   │
  │      password: "Pass123"     │
  │    }                         │
  ├──────────────────────────────>│
  │                              │
  │                              │ 2. Find user by email
  │                              │    ┌──────────────────────────┐
  │                              │    │ SELECT * FROM users      │
  │                              │    │ WHERE email =            │
  │                              │    │   'john@ex.com'          │
  │                              │    └──────────────────────────┘
  │                              │    ↓
  │                              │    User found: {
  │                              │      id: 5,
  │                              │      password_hash: "$2b$..."
  │                              │    }
  │                              │
  │                              │ 3. Verify password
  │                              │    ┌──────────────────────────┐
  │                              │    │ bcrypt.checkpw(          │
  │                              │    │   "Pass123",             │
  │                              │    │   stored_hash            │
  │                              │    │ )                        │
  │                              │    └──────────────────────────┘
  │                              │    ✓ Password correct
  │                              │
  │                              │ 4. Check account status
  │                              │    ┌──────────────────────────┐
  │                              │    │ if user.is_active:       │
  │                              │    │   ✓ Account active       │
  │                              │    │ else:                    │
  │                              │    │   ✗ Account disabled     │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 5. Generate JWT tokens
  │                              │    ┌──────────────────────────┐
  │                              │    │ Access Token (1 hour):   │
  │                              │    │ {                        │
  │                              │    │   user_id: 5,            │
  │                              │    │   exp: now + 1h          │
  │                              │    │ }                        │
  │                              │    │ + sign with secret       │
  │                              │    │ ↓                        │
  │                              │    │ eyJhbGciOi...            │
  │                              │    │                          │
  │                              │    │ Refresh Token (30 days): │
  │                              │    │ {                        │
  │                              │    │   user_id: 5,            │
  │                              │    │   exp: now + 30d         │
  │                              │    │ }                        │
  │                              │    │ + sign with secret       │
  │                              │    │ ↓                        │
  │                              │    │ eyJhbGciOj...            │
  │                              │    └──────────────────────────┘
  │                              │
  │ 6. 200 OK                    │
  │    {                         │
  │      access_token: "eyJ...", │
  │      refresh_token: "eyJ...",│
  │      token_type: "Bearer",   │
  │      expires_in: 3600        │
  │    }                         │
  │<──────────────────────────────┤
  │                              │
  │ 7. Store tokens              │
  │    ┌──────────────────────┐  │
  │    │ localStorage:        │  │
  │    │ access_token: "..." │  │
  │    │ refresh_token: "..." │  │
  │    └──────────────────────┘  │
  │                              │

ERROR SCENARIOS:

1. User Not Found:
   "unknown@ex.com" → ✗ 401 Unauthorized
                      {"error": "Invalid email or password"}

2. Wrong Password:
   Correct email, wrong password → ✗ 401 Unauthorized
                                   {"error": "Invalid email or password"}

   Note: Same error message! Don't reveal which one is wrong!

3. Account Disabled:
   Correct credentials, is_active=false → ✗ 403 Forbidden
                                          {"error": "Account is disabled"}
```

---

## DIAGRAM 7: Protected Route Flow

**Concept:** How JWT tokens protect endpoints

```
┌────────────────────────────────────────────────────────┐
│  PROTECTED ENDPOINT FLOW                               │
└────────────────────────────────────────────────────────┘

CLIENT                         SERVER
  │                              │
  │ 1. GET /posts                │
  │    Headers:                  │
  │      Authorization:          │
  │        Bearer eyJhbGc...     │
  ├──────────────────────────────>│
  │                              │
  │                              │ 2. Extract token from header
  │                              │    ┌──────────────────────────┐
  │                              │    │ Header value:            │
  │                              │    │ "Bearer eyJhbGciOiJ..."   │
  │                              │    │      ↓ Remove "Bearer "  │
  │                              │    │ Token: eyJhbGciOiJ...    │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 3. Verify token signature
  │                              │    ┌──────────────────────────┐
  │                              │    │ Split token:             │
  │                              │    │   header.payload.sig     │
  │                              │    │                          │
  │                              │    │ Recreate signature:      │
  │                              │    │   HMAC(header.payload,   │
  │                              │    │        secret_key)       │
  │                              │    │                          │
  │                              │    │ Compare:                 │
  │                              │    │   received_sig ==        │
  │                              │    │   recreated_sig          │
  │                              │    └──────────────────────────┘
  │                              │    ✓ Signature valid
  │                              │
  │                              │ 4. Check expiration
  │                              │    ┌──────────────────────────┐
  │                              │    │ Token payload:           │
  │                              │    │ {                        │
  │                              │    │   user_id: 5,            │
  │                              │    │   exp: 1735689600        │
  │                              │    │ }                        │
  │                              │    │                          │
  │                              │    │ Current time: 1735680000 │
  │                              │    │                          │
  │                              │    │ if current < exp:        │
  │                              │    │   ✓ Token not expired    │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 5. Check blacklist
  │                              │    ┌──────────────────────────┐
  │                              │    │ SELECT * FROM            │
  │                              │    │ token_blacklist          │
  │                              │    │ WHERE jti = '...'        │
  │                              │    └──────────────────────────┘
  │                              │    ✓ Not blacklisted
  │                              │
  │                              │ 6. Decode user info
  │                              │    ┌──────────────────────────┐
  │                              │    │ Payload:                 │
  │                              │    │   user_id: 5             │
  │                              │    │                          │
  │                              │    │ Get user from DB:        │
  │                              │    │ SELECT * FROM users      │
  │                              │    │ WHERE id = 5             │
  │                              │    │                          │
  │                              │    │ User: {                  │
  │                              │    │   id: 5,                 │
  │                              │    │   role: "author"         │
  │                              │    │ }                        │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 7. Check authorization
  │                              │    ┌──────────────────────────┐
  │                              │    │ Endpoint requires:       │
  │                              │    │   role = "author"        │
  │                              │    │                          │
  │                              │    │ User has:                │
  │                              │    │   role = "author"        │
  │                              │    │                          │
  │                              │    │ ✓ Authorized!            │
  │                              │    └──────────────────────────┘
  │                              │
  │                              │ 8. Process request
  │                              │    Query posts, apply filters
  │                              │
  │ 9. 200 OK                    │
  │    {                         │
  │      posts: [...]            │
  │    }                         │
  │<──────────────────────────────┤
  │                              │

ERROR SCENARIOS:

1. No Token:
   Missing Authorization header → ✗ 401 Unauthorized
                                  {"msg": "Missing Authorization Header"}

2. Invalid Format:
   "InvalidToken123" → ✗ 422 Unprocessable Entity
                       {"msg": "Bad Authorization header"}

3. Invalid Signature:
   Token tampered with → ✗ 422 Unprocessable Entity
                         {"msg": "Signature verification failed"}

4. Expired Token:
   exp < current_time → ✗ 401 Unauthorized
                        {"msg": "Token has expired"}

5. Blacklisted Token:
   Token in blacklist → ✗ 401 Unauthorized
                        {"msg": "Token has been revoked"}

6. Wrong Role:
   User is "reader", needs "author" → ✗ 403 Forbidden
                                      {"error": "Requires author role"}
```

---

## DIAGRAM 8: Role-Based Access Control (RBAC)

**Concept:** Different permissions for different roles

```
┌────────────────────────────────────────────────────────┐
│  ROLE-BASED ACCESS CONTROL (RBAC)                     │
└────────────────────────────────────────────────────────┘

ROLES HIERARCHY:
┌────────────────────────────────────┐
│                                    │
│           ADMIN                    │ ← Full control
│             │                      │
│     ┌───────┴───────┐              │
│     │               │              │
│   AUTHOR         MODERATOR         │ ← Can create content
│     │               │              │
│     └───────┬───────┘              │
│             │                      │
│          READER                    │ ← Read-only
│                                    │
└────────────────────────────────────┘

PERMISSIONS MATRIX:

┌────────────────┬────────┬────────┬────────┐
│ Action         │ Reader │ Author │ Admin  │
├────────────────┼────────┼────────┼────────┤
│ Register       │   ✓    │   ✓    │   ✓    │
│ Login          │   ✓    │   ✓    │   ✓    │
│ View profile   │   ✓    │   ✓    │   ✓    │
│ Edit profile   │   ✓    │   ✓    │   ✓    │
├────────────────┼────────┼────────┼────────┤
│ Read posts     │   ✓    │   ✓    │   ✓    │
│ Create post    │   ✗    │   ✓    │   ✓    │
│ Edit own post  │   ✗    │   ✓    │   ✓    │
│ Edit any post  │   ✗    │   ✗    │   ✓    │
│ Delete own     │   ✗    │   ✓    │   ✓    │
│ Delete any     │   ✗    │   ✗    │   ✓    │
├────────────────┼────────┼────────┼────────┤
│ View users     │   ✗    │   ✗    │   ✓    │
│ Delete users   │   ✗    │   ✗    │   ✓    │
│ Change roles   │   ✗    │   ✗    │   ✓    │
└────────────────┴────────┴────────┴────────┘

IMPLEMENTATION:

1. Store role in user record:
┌────────────────────────────┐
│ users table:               │
├────┬──────────┬────────────┤
│ id │ username │ role       │
├────┼──────────┼────────────┤
│ 1  │ john     │ reader     │
│ 2  │ jane     │ author     │
│ 3  │ admin    │ admin      │
└────┴──────────┴────────────┘

2. Include role in JWT token:
┌────────────────────────────┐
│ Token payload:             │
│ {                          │
│   "user_id": 2,            │
│   "role": "author"   ← !   │
│ }                          │
└────────────────────────────┘

3. Check role in decorator:
┌────────────────────────────────────┐
│ @require_role('author', 'admin')   │
│ def create_post():                 │
│     # Only author or admin can     │
│     # execute this function        │
│     ...                            │
└────────────────────────────────────┘

AUTHORIZATION FLOW:

Request: POST /posts
         Authorization: Bearer <token>
         ↓
Extract token
         ↓
Decode payload: { user_id: 1, role: "reader" }
         ↓
Check endpoint requirements: @require_role('author')
         ↓
Is "reader" in ['author', 'admin']?
         ↓
NO → ✗ 403 Forbidden
     {"error": "Requires author role"}

Request: POST /posts
         Authorization: Bearer <token>
         ↓
Extract token
         ↓
Decode payload: { user_id: 2, role: "author" }
         ↓
Check endpoint requirements: @require_role('author')
         ↓
Is "author" in ['author', 'admin']?
         ↓
YES → ✓ Proceed with request
```

---

## DIAGRAM 9: Token Refresh Flow

**Concept:** Getting new access token without re-login

```
┌────────────────────────────────────────────────────────┐
│  TOKEN REFRESH FLOW                                    │
└────────────────────────────────────────────────────────┘

WHY REFRESH TOKENS?

Access Token (Short-lived: 1 hour)
┌──────────────────────────────────┐
│ • Used for API requests          │
│ • Expires quickly (security)     │
│ • If stolen, limited damage      │
└──────────────────────────────────┘

Refresh Token (Long-lived: 30 days)
┌──────────────────────────────────┐
│ • Used only to get new access    │
│ • Expires slowly (convenience)   │
│ • Stored more securely           │
└──────────────────────────────────┘

TYPICAL FLOW:

Time 0: User logs in
┌───────────────────────────────────────┐
│ Receives:                             │
│   access_token (expires: 1h)          │
│   refresh_token (expires: 30d)        │
└───────────────────────────────────────┘

Time 30 min: Make API request
┌───────────────────────────────────────┐
│ POST /posts                           │
│ Authorization: Bearer <access_token>  │
│                                       │
│ ✓ Success (token still valid)        │
└───────────────────────────────────────┘

Time 65 min: Make API request
┌───────────────────────────────────────┐
│ POST /posts                           │
│ Authorization: Bearer <access_token>  │
│                                       │
│ ✗ 401 Unauthorized                    │
│ {"msg": "Token has expired"}          │
└───────────────────────────────────────┘

CLIENT                         SERVER
  │                              │
  │ Access token expired!        │
  │                              │
  │ POST /auth/refresh           │
  │ Authorization:               │
  │   Bearer <refresh_token>     │
  ├──────────────────────────────>│
  │                              │
  │                              │ Verify refresh token:
  │                              │   ✓ Valid signature
  │                              │   ✓ Not expired
  │                              │   ✓ Not blacklisted
  │                              │
  │                              │ Generate new access token:
  │                              │   {
  │                              │     user_id: 5,
  │                              │     exp: now + 1h
  │                              │   }
  │                              │
  │ 200 OK                       │
  │ {                            │
  │   access_token: "eyJ...",    │
  │   expires_in: 3600           │
  │ }                            │
  │<──────────────────────────────┤
  │                              │
  │ Store new access token       │
  │                              │
  │ Retry original request       │
  │ POST /posts                  │
  │ Authorization:               │
  │   Bearer <NEW_access_token>  │
  ├──────────────────────────────>│
  │                              │
  │ ✓ Success!                   │
  │<──────────────────────────────┤
  │                              │

BENEFIT: User stays logged in for 30 days
         without repeatedly entering password!

SECURITY:

1. Access token exposed more often
   (every API request)
   → Short lifetime limits damage if stolen

2. Refresh token used rarely
   (only when access expires)
   → Can be stored more securely
   → Longer lifetime OK

3. Both can be blacklisted on logout
```

---

## DIAGRAM 10: Logout & Token Blacklisting

**Concept:** Revoking tokens before expiration

```
┌────────────────────────────────────────────────────────┐
│  LOGOUT & TOKEN BLACKLISTING                           │
└────────────────────────────────────────────────────────┘

THE PROBLEM:

JWTs are stateless → Server doesn't track them
                  → Can't "delete" a token!

Once issued, JWT is valid until expiration:
┌──────────────────────────────────────────┐
│ Token issued: 10:00 AM                   │
│ Expires: 11:00 AM (1 hour later)         │
│                                          │
│ User logs out at 10:30 AM                │
│                                          │
│ Without blacklist:                       │
│   Token still works until 11:00 AM! ✗    │
│                                          │
│ With blacklist:                          │
│   Token invalidated at 10:30 AM! ✓       │
└──────────────────────────────────────────┘

THE SOLUTION: Token Blacklist

DATABASE TABLE:
┌────────────────────────────────────┐
│ token_blacklist_auth               │
├────┬───────────────────┬───────────┤
│ id │ jti               │created_at │
├────┼───────────────────┼───────────┤
│ 1  │ abc123-uuid-here  │ 10:30 AM  │
│ 2  │ xyz789-uuid-here  │ 10:45 AM  │
└────┴───────────────────┴───────────┘

JTI = JWT ID (unique identifier in token)

LOGOUT FLOW:

CLIENT                         SERVER
  │                              │
  │ POST /auth/logout            │
  │ Authorization:               │
  │   Bearer <access_token>      │
  ├──────────────────────────────>│
  │                              │
  │                              │ 1. Extract JTI from token
  │                              │    ┌──────────────────────┐
  │                              │    │ Token payload:       │
  │                              │    │ {                    │
  │                              │    │   user_id: 5,        │
  │                              │    │   jti: "abc123..."   │
  │                              │    │ }                    │
  │                              │    └──────────────────────┘
  │                              │
  │                              │ 2. Add to blacklist
  │                              │    ┌──────────────────────┐
  │                              │    │ INSERT INTO          │
  │                              │    │ token_blacklist (    │
  │                              │    │   jti,               │
  │                              │    │   created_at         │
  │                              │    │ ) VALUES (           │
  │                              │    │   'abc123...',       │
  │                              │    │   NOW()              │
  │                              │    │ )                    │
  │                              │    └──────────────────────┘
  │                              │
  │ 200 OK                       │
  │ {"message": "Logged out"}    │
  │<──────────────────────────────┤
  │                              │
  │ Delete tokens from storage   │
  │ ┌────────────────────────┐   │
  │ │ localStorage.clear()   │   │
  │ └────────────────────────┘   │
  │                              │

SUBSEQUENT REQUEST:

CLIENT                         SERVER
  │                              │
  │ GET /posts                   │
  │ Authorization:               │
  │   Bearer <same_token>        │
  ├──────────────────────────────>│
  │                              │
  │                              │ 1. Decode token
  │                              │    jti: "abc123..."
  │                              │
  │                              │ 2. Check blacklist
  │                              │    ┌──────────────────────┐
  │                              │    │ SELECT * FROM        │
  │                              │    │ token_blacklist      │
  │                              │    │ WHERE jti =          │
  │                              │    │   'abc123...'        │
  │                              │    └──────────────────────┘
  │                              │    ✓ Found in blacklist!
  │                              │
  │ ✗ 401 Unauthorized           │
  │ {"msg": "Token revoked"}     │
  │<──────────────────────────────┤
  │                              │

CLEANUP:

Blacklist grows over time → Need to clean old tokens

┌────────────────────────────────────────┐
│ Periodic cleanup (e.g., daily):       │
│                                        │
│ DELETE FROM token_blacklist            │
│ WHERE created_at < NOW() - INTERVAL    │
│   '30 days'                            │
│                                        │
│ (Remove entries older than longest    │
│  token lifetime)                       │
└────────────────────────────────────────┘
```

---

These diagrams cover all major authentication concepts in Chapter 4!
