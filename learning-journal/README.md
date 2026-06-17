# Learning Journal

## What This Folder Is

This folder holds one reflection file per phase of the project. You write them in your own words as you finish each phase.

The point is not to summarize what you built. The point is to record **how your understanding changed**. What confused you? What clicked? What would you have done differently if you started over?

A recruiter who sees this folder can tell in 30 seconds whether you understood the project or just followed along.

---

## Why This Matters in Interviews

The biggest red flag in a senior backend interview is clean code that the candidate cannot explain.

When an interviewer asks "walk me through your GraphQL setup," the difference between a person who learned and a person who copied shows up immediately. Someone who wrote these notes can say:

> "In Phase 1 I was confused about why Strawberry uses `Optional[str]` to map to a nullable field instead of a separate annotation. Once I saw the SDL it generates, the mapping made sense: Python's type system and GraphQL's nullability model are actually quite similar."

That is an answer built from real experience. No amount of reading about GraphQL produces that kind of fluency.

---

## How to Use These Files

Each file has sections with prompts. The prompts are guides, not mandatory structure. Write what is true for you, not what sounds good.

**Write during, not after.**

The best time to write a reflection is while you are still in the phase, when the confusion and the breakthroughs are fresh. If you wait until all 8 phases are done, you will write vague summaries.

**One sentence per concept is enough.**

You do not need to write paragraphs. A note like "camelCase conversion was automatic, I expected to configure it" is more useful than a three-paragraph essay that does not reveal anything personal.

**Be honest about confusion.**

Saying "I do not fully understand how the gateway plans federated queries yet" is a good note. It tells you what to research. It also shows you know the limits of your understanding, which interviewers respect.

---

## File Naming

```
phase-01-notes.md
phase-02-notes.md
...
phase-08-notes.md
```

Keep the numbering consistent. Later you will link back to earlier phases from later ones, and consistent names make that easy.

---

## Do Not Edit These Files

Do not go back and clean up your notes to make them look better. The progression of understanding is the artifact. A note that says "I thought resolvers ran sequentially but they can run in parallel" followed by a later note that says "I now understand query planning because of the gateway phase" shows real learning. Editing it away removes the evidence.
