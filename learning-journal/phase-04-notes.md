# Phase 04 Notes - Resume Service

**Date started:**
**Date completed:**
**Commit where this phase is done:**

---

## What Did We Build?

2-3 sentences in your own words.

> _Write here_

---

## The Background Job Pattern: In Your Own Words

Why couldn't we just parse the PDF synchronously inside the mutation and return the result?

> _Write here_

Describe the complete flow from "user uploads PDF" to "user sees their skills":

> _Step 1:_
> _Step 2:_
> _Step 3:_
> _Step 4:_
> _Step 5:_

---

## Two Processes, One Codebase

Phase 4 runs two separate processes from the same code.

What does uvicorn handle?
> _Write here_

What does the celery worker handle?
> _Write here_

Why do they need different database drivers (asyncpg vs psycopg2)?
> _Write here_

---

## The Upload Scalar

What is the `Upload` type in GraphQL?
> _Write here_

Why does `python-multipart` need to be installed for file uploads?
> _Write here_

What would happen if you forgot to `await file.read()` and tried to pass the file object to Celery?
> _Write here_

---

## Bytes and Celery: The Hex Trick

Celery serializes arguments to JSON before sending to Redis.
Why can't raw bytes be sent directly?
> _Write here_

How do we work around it? What does `.hex()` and `bytes.fromhex()` do?
> _Write here_

---

## The Job Status Machine

Draw the valid transitions:

```
PENDING → ________ → ________
                  ↘ ________
```

What would happen if a client polls `resumeJob` 100ms after uploading?
> _Write here_

What is polling? What are its downsides? What replaces it in Phase 7?
> _Write here_

---

## What `bind=True` Does in the Celery Task

> _Write here_

What does `self.retry(exc=exc, countdown=30)` do?
> _Write here_

---

## A Mistake I Made

> _Write here_

---

## Interview Talking Points

**"Why would you use background jobs for file processing?"**
>

**"Explain the job ID polling pattern."**
>

**"How do you pass data between FastAPI and Celery?"**
>

**"What is the difference between a Celery broker and a result backend?"**
>

**"What GraphQL type handles file uploads?"**
>

---

## Phase Rating

**Background job pattern:**
[ ] I understand it conceptually
[ ] I can implement it from scratch
[ ] I can explain the tradeoffs (polling vs subscriptions vs webhooks)

**File uploads in GraphQL:**
[ ] I know Upload exists but not the details
[ ] I can implement it correctly including multipart and python-multipart

**Celery + Redis:**
[ ] I can run it but don't fully understand broker vs backend
[ ] I understand broker vs backend and could configure them separately
[ ] I could explain task retries and idempotency
