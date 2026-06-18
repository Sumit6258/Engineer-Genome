# Phase 02 Notes - GitHub Service

**Date started:**
**Date completed:**
**Commit where this phase is done:**

---

## What Did We Build?

Write 2-3 sentences in your own words. Not a copy from the README. Explain it as if you're telling a developer colleague what you built this week.

> _Write here_

---

## The Four Layers: In Your Own Words

Write one sentence per layer. What does it own? What is it NOT allowed to touch?

**external/ (GithubClient):**
> _What is its job? What would break if you removed it?_

**db/ (models + repositories):**
> _What does it own? What is it NOT allowed to do?_

**services/ (GithubService):**
> _What lives here that couldn't live in the resolver? Give a specific example._

**api/ (types + resolvers):**
> _What does it know about that the other layers don't?_

---

## Context Injection: The Concept That Changed How I Think About Resolvers

In Phase 1, resolvers imported data directly: `from app.data import store`.
In Phase 2, they use `info.context["github_service"]`.

In your own words, why is the Phase 2 approach better?
> _Write here_

What would you have to do to test a Phase 1 resolver? What about a Phase 2 resolver?
> _Write here_

---

## Nested Resolvers: When They Click

The moment `GithubProfile.repositories()` made sense was when I realized:
> _Describe the specific moment or analogy that made it click_

What is the difference between `self.username` (available immediately) and calling `service.get_repositories(self.username)` (a separate API call)?
> _Write here_

---

## SQLAlchemy: What Surprised Me

The thing I did not expect about SQLAlchemy async was:
> _Write here_

The difference between the engine, the session factory, and a session:
> _In your own words, one sentence each_

Engine:
Session factory:
Session:

---

## The N+1 Problem: Do You See It Yet?

Write a concrete example of where the N+1 problem would appear in EngineerGenome.
Think about Phase 6 when there are multiple developers in a list.

> _Write your example here_

Why does it not hurt Phase 2 but will hurt Phase 6?
> _Write here_

---

## A Mistake I Made and Fixed

> _Write here_

---

## Interview Talking Points

Answer these directly, as if in an interview.

**"Walk me through the four-layer architecture you used in the GitHub service."**
>

**"How do nested resolvers work in GraphQL?"**
>

**"What is the context in Strawberry and how do you use it?"**
>

**"Why would you put logic in the services layer instead of the resolver?"**
>

---

## What I Would Do Differently

If you started Phase 2 again today:
> _Write here_

---

## Questions for Phase 3 (LeetCode Service)

The LeetCode service follows the same four-layer structure. What do you expect to be the same? What might be different?

-
-
-

---

## Phase Rating

**Four-layer architecture:**
[ ] I understand it conceptually but would need a reference to implement
[ ] I could implement it with occasional reference
[ ] I could implement it from memory
[ ] I could explain the tradeoffs to a senior engineer

**Context injection:**
[ ] Still fuzzy
[ ] I understand it but could not explain why it matters
[ ] I can explain the testing benefit clearly

**Nested resolvers:**
[ ] Still fuzzy on when they run vs when they don't
[ ] I understand when they run but not how to design them
[ ] I can design and implement nested resolvers from scratch
