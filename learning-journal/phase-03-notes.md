# Phase 03 Notes - LeetCode Service

**Date started:**
**Date completed:**
**Commit where this phase is done:**

---

## What Did We Build?

2-3 sentences in your own words.

> _Write here_

---

## The Three Kinds of Resolvers: In Your Own Words

**Root resolver (`Query.leetcode_profile`):**
> _What does it do? When does it run?_

**Field resolver (`LeetCodeProfile.contest_info`):**
> _Why is it a field resolver instead of embedded? What triggers it?_

**Computed field resolver (`ProblemStats.hard_percentage`):**
> _Why does this one need no API call? What makes it different?_

---

## Enum Types: What Clicked

The reason enums are better than plain strings is:
> _Write here_

What happens in GraphiQL when you send `solvedFor(difficulty: IMPOSSIBLE)`?
> _Write here (test it first)_

---

## Embedded Type vs Field Resolver

`ProblemStats` is embedded directly on `LeetCodeProfile`. `ContestInfo` is a field resolver.

Why is `ProblemStats` embedded and not a field resolver?
> _Write here_

Why is `ContestInfo` a field resolver and not embedded?
> _Write here_

---

## GraphQL Calling GraphQL

In your own words: what is actually happening at the network level when `LeetCodeClient._query()` runs?
> _Write here_

Why does this matter for understanding how the Apollo Gateway (Phase 6) will work?
> _Write here_

---

## Pagination: The Three Levels

**Limit-based (what we built):**
> _When is this appropriate? What's the limitation?_

**Offset-based (what we could add):**
> _What does offset give you? What problem does it have?_

**Cursor-based (Phase 8):**
> _Why is this better for production? What's the cost?_

---

## A Mistake I Made

> _Write here_

---

## The Pattern Is Getting Familiar

Phase 2 introduced the four-layer architecture. Phase 3 repeated it with three layers.
What felt different this time compared to Phase 2?

> _Write here_

---

## Interview Talking Points

**"What is a field resolver and when would you use one over embedding data?"**
>

**"Explain GraphQL enums and their advantage over strings."**
>

**"What is the N+1 problem and how does it relate to field resolvers?"**
>

**"Compare limit-based and cursor-based pagination."**
>

---

## Questions Going Into Phase 4

Phase 4 adds resume file uploads and background jobs (Celery). What are you curious or uncertain about?

-
-
-

---

## Phase Rating

**Three resolver types:**
[ ] I can name them but not explain the difference clearly
[ ] I can explain when to use each
[ ] I could implement all three from scratch

**Enums:**
[ ] I understand them conceptually
[ ] I can define them in Strawberry and use as arguments
[ ] I can explain why they're better than strings for closed value sets

**Pagination:**
[ ] Limit-based makes sense, offset and cursor are fuzzy
[ ] I understand all three patterns
[ ] I could implement cursor-based pagination from scratch
