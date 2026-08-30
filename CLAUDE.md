
# ezex — Project Context

## Purpose
ezex is a free, accessible physiotherapy exercise website and later, as an app on app store. Core features:
- Browsable collections of PT exercises
- Users can build their own custom workouts from those exercises
- Search/browse by injury or symptom (e.g. "ankle sprain") to surface relevant exercises
- Planned: a chatbot that takes user-described symptoms and suggests relevant exercises — explicitly NOT meant to provide a medical diagnosis
- Physiotherapists should also have ability to sign in as physiotherapists and provide clients with workouts. They can also upload their own exercises.

## Current stage
Idea stage. GitHub repo created. UI wireframes exist (built in Freeform) for the dashboard and exercise page. No code written yet.

## Planned stack
Same as my prior project (a Task Tracker mini project), chosen deliberately since I already have hands-on experience with it:
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL via Docker Compose
- Frontend: Next.js (App Router), TypeScript, React, Tailwind CSS
- Infra: Docker Compose, Git/GitHub

## Key difference from the prior project
This is NOT solely a learning exercise — I intend to actually scale this toward real users. Build with production-mindedness from day one: proper folder structure (already my habit — core/models/schemas/routers/services split), but also think ahead about things that were deliberately skipped in the mini project: auth, environment separation (dev/prod config), more robust validation, rate limiting on any AI/chatbot feature, and terms of service / liability considerations.

## Working style
- Before writing any non-trivial code, explain the approach and reasoning first. Boilerplate (config, folder structure, standard setup) can be written directly with a brief walkthrough.
- The goal is to understand "why," not just get working code — I want to be able to replicate patterns independently on future projects.
- Prefer conceptual, plain-language explanations over line-by-line code dumps. Full breakdowns are welcome for genuinely new concepts.
- When debugging, I'll paste actual terminal/error output — diagnose precisely from that rather than guessing.
- I ask targeted clarifying questions about specific mechanisms (e.g. "what calls this," "where is this defined") rather than accepting code passively.
- My knowledge base is mainly fundamentals: Python, JavaScript, HTML, CSS, SQL. I'm building depth in full-stack dev (FastAPI backend, TypeScript/React/Next.js frontend) and want to understand what's being built, not just have it appear.

## My current technical grounding (from the Task Tracker project)
Comfortable with: FastAPI routing and CRUD patterns, REST fundamentals (HTTP methods, status codes), SQLAlchemy models + Alembic migrations, Docker Compose for local Postgres, React fundamentals (useState, useEffect, props, lifted state, controlled inputs), TypeScript interfaces/shared types, Tailwind CSS basics (flex, spacing scale, conditional classNames), CORS, and outbound webhooks (backend-triggered HTTP calls on events).

Still building depth on: authentication patterns, testing, deployment, more complex/relational data models, and AI-chatbot integration patterns specifically.

## Important: health/liability considerations
This app touches health-adjacent content (exercise suggestions tied to injuries/symptoms, plus a planned symptom-input chatbot). Worth keeping in mind across sessions:
- Any chatbot or symptom-search feature should be designed to suggest exercises based on stated symptoms, not diagnose. Persistent, clear disclaimers should appear near any symptom-input or suggestion feature (e.g. "This is not a diagnosis. Always consult a licensed physiotherapist.").
- I am aware a disclaimer alone isn't a complete legal shield, and has been advised (informally, not as legal counsel) to consult an actual lawyer once the product moves toward real users.
- Watch for any feature drifting from "exercise suggestion based on self-reported input" toward language that reads as a diagnostic claim, and flag it if so.

## Team context
My partner has a kinesiology background and physiotherapy industry connections — a potential source of domain/content accuracy review and an early path to real users as the product grows.
