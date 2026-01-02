# Implementation Plan: Alexa Weekly Meal Planner

**Branch**: `001-alexa-meal-planner` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-alexa-meal-planner/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an Alexa skill that reads a weekly meal plan from a user's Google Sheet and responds to voice queries about meals for specific days and times. The skill will be deployed using Alexa-hosted infrastructure, cache data for 24 hours with manual refresh capability, and handle edge cases like empty meal slots and off-hours queries by suggesting the next upcoming meal.

## Technical Context

**Language/Version**: Python 3.11 (Alexa-hosted skills support)  
**Primary Dependencies**: ask-sdk-core 1.19.0, gspread 5.12.0, oauth2client 4.1.3  
**Storage**: In-memory caching (24-hour TTL), Google Sheets API for persistent data  
**Testing**: pytest 7.4.3, pytest-mock 3.12.0, local mock framework for Alexa requests  
**Target Platform**: Alexa-hosted skills (Amazon-managed Python runtime)  
**Project Type**: single (voice interface backend only, no separate frontend)  
**Performance Goals**: <3s response time (FR success criteria), 95% accuracy in meal identification  
**Constraints**: 24-hour cache TTL, Google Sheets API quota limits, Alexa-hosted execution environment limits  
**Scale/Scope**: Single user (private skill), ~35 meal entries (7 days × 5 meals), minimal concurrent requests  
**Deployment**: NEEDS CLARIFICATION - Alexa-hosted skills deployment process, service account credential management  
**Cache Invalidation**: NEEDS CLARIFICATION - Implementation approach for manual refresh command in Alexa context

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: No active constitution principles defined in `.specify/memory/constitution.md` (template only).

**Phase 0 Result**: ✓ **PASS** - No gates to evaluate. Feature proceeded to Phase 0.

**Phase 1 Re-evaluation**: ✓ **PASS** - Design complete. No constitution violations detected.

**Action**: Consider establishing project constitution principles if recurring architectural patterns emerge across multiple features.

## Project Structure

### Documentation (this feature)

```text
specs/001-alexa-meal-planner/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── intents.json     # Alexa intent schemas
│   ├── slots.json       # Alexa slot type definitions
│   └── examples.md      # Sample request/response flows
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single project structure (Alexa skill backend)
src/
├── __init__.py
├── lambda_function.py        # Main Lambda handler, skill builder, caching logic
├── config/
│   ├── __init__.py
│   ├── settings.py           # Environment variables, Google Sheets config
│   └── meal_periods.py       # Time period definitions (8am-11am breakfast, etc.)
├── handlers/
│   ├── __init__.py
│   ├── intent_handlers.py    # Alexa intent handlers (GetMeal, GetTodayMeals, etc.)
│   └── response_builder.py   # Alexa response formatting
├── models/
│   ├── __init__.py
│   ├── meal_plan.py          # MealPlan entity, weekly data structure
│   └── time_period.py        # TimePeriod entity, meal period logic
└── services/
    ├── __init__.py
    ├── sheets_service.py     # Google Sheets API integration
    └── meal_service.py       # Meal lookup, next meal calculation

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_models.py        # MealPlan, TimePeriod unit tests
│   ├── test_time_periods.py  # Meal period boundary tests
│   └── test_meal_service.py  # Meal lookup logic tests
├── integration/
│   ├── __init__.py
│   └── test_intent_handlers.py  # Intent handler integration tests
└── fixtures/
    ├── mock_alexa_requests.json  # Sample Alexa request payloads
    └── sample_meal_data.json     # Mock Google Sheets data

local_test/
├── test_runner.py            # Local testing framework
├── mock_alexa.py             # Alexa request simulator
├── test_sheets.py            # Google Sheets connection test
└── manual_test.py            # Interactive testing script

alexa-skill/
├── skill.json                # Alexa skill manifest
└── interaction-model.json    # Alexa interaction model (intents, slots)

docs/
└── deployment.md             # Deployment guide for Alexa-hosted skills

credentials.json              # Google Sheets service account credentials (gitignored)
requirements.txt              # Python dependencies
.env                          # Environment variables (gitignored)
```

**Structure Decision**: Single-project structure selected. This is a voice-interface backend skill with no separate frontend UI. All code runs in the Alexa-hosted Python environment, with clear separation between Alexa handlers, business logic (meal service), external integration (Google Sheets), and data models.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
