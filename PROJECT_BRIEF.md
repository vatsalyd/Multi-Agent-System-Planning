# Project Brief

**Name:** HelixDesk
**Owner:** vatsalyd
**Created:** 2026-07-11
**Type:** Existing repo — onboarded on 2026-07-11

## What It Is
HelixDesk is an AI-powered multi-agent support ticket triage system. It processes incoming employee support tickets through a pipeline of specialized agents that classify (triage), research (RAG retrieval), and draft professional resolutions — all backed by a company knowledge base. Built as a portfolio project intended for production use.

## Primary Actors
- **End users** — employees submitting support tickets (via API, Slack, email, webhooks)
- **Human agents** — receive escalated low-confidence tickets
- **Developers** — maintain and extend the system (you)

## Problem Statement
Enterprise support teams are flooded with repetitive tickets (password resets, VPN issues, policy questions). Manual triage is slow, inconsistent, and wastes skilled agents on trivial tasks. Without automation, resolution times stretch from minutes to hours.

## Definition of Done
- Ticket submitted via API → classified, researched, and resolved with citations in <5s
- Low-confidence tickets automatically escalated to humans
- Knowledge base is searchable and up-to-date
- Deployed and accessible via REST API
- Tests pass, CI/CD pipeline functional

## Explicit Non-Scope
- No real-time chat or live agent handoff UI
- No ticketing system integration (Jira, ServiceNow) — API-only for now
- No multi-tenant or authentication layer
- No fine-tuning or custom model training
- No SLA tracking or analytics dashboard

## Hard Constraints
- Python 3.12+, FastAPI, LangGraph, Groq (free tier LLM)
- ChromaDB for vector storage (local persistent)
- Sentence Transformers for embeddings (CPU-only)
- Docker deployment, AWS ECR → EC2
- MIT license

## Known Gaps (Existing Repos)
- No agent context files (CLAUDE.md, INTENT.md)
- No spec files or task specifications
- No structured logging/error tracking directory
- `.env` contains a live API key (should be rotated or noted)
- No `.claude/rules/` for scoped instructions
