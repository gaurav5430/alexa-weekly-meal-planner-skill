# Tasks: Alexa Weekly Meal Planner

**Input**: Design documents from `/specs/001-alexa-meal-planner/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in the specification - focusing on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/, tests/, local_test/) per plan.md
- [X] T002 Initialize Python project with requirements.txt (ask-sdk-core, gspread, oauth2client, pytest)
- [X] T003 [P] Create .gitignore file (credentials.json, .env, venv/, __pycache__/, *.pyc)
- [X] T004 [P] Create README.md with project overview and link to quickstart.md
- [X] T005 [P] Setup .env template file (.env.example) with GOOGLE_SHEET_ID and CREDENTIALS_PATH placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create TimePeriod data class in src/models/time_period.py with 5 meal periods (breakfast 8-11am, morning snack 11am-12pm, lunch 12-3pm, evening snack 4-6pm, dinner 7-10pm)
- [X] T007 [P] Create Meal data class in src/models/meal_plan.py with day_of_week, meal_period, name, is_empty attributes
- [X] T008 [P] Create MealPlan data class in src/models/meal_plan.py with meals dict, last_updated, sheet_id, is_valid attributes
- [X] T009 [P] Create MealQuery data class in src/models/meal_plan.py with query_type enum, target_day, target_period, query_time, timezone
- [X] T010 Create meal period configuration in src/config/meal_periods.py defining all 5 TimePeriod instances
- [X] T011 [P] Create settings configuration in src/config/settings.py for Google Sheet ID and credentials path from environment variables
- [X] T012 Implement SheetsService in src/services/sheets_service.py with fetch_meal_plan() and validate_sheet_structure() methods
- [X] T013 Create test fixtures in tests/fixtures/sample_meal_data.json with example 7-day meal plan
- [X] T014 [P] Create test fixtures in tests/fixtures/mock_alexa_requests.json with sample Alexa request structures

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ask About Next Meal (Priority: P1) 🎯 MVP

**Goal**: User can ask Alexa for a specific meal type and get the meal name from Google Sheet

**Independent Test**: Ask "Alexa, what's for dinner?" at different times and verify correct meal is returned from Google Sheet

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement get_current_meal_period() function in src/models/time_period.py to determine current meal based on time
- [X] T016 [P] [US1] Implement get_meal_for_period() method in src/services/meal_service.py to lookup meal by day and period
- [X] T017 [US1] Create GetMealIntentHandler class in src/handlers/intent_handlers.py for GetMealIntent
- [X] T018 [US1] Implement build_meal_response() in src/handlers/response_builder.py to format single meal announcement
- [X] T019 [US1] Add GetMealIntentHandler registration in src/lambda_function.py
- [X] T020 [US1] Add error handling for empty meal slots in src/handlers/intent_handlers.py
- [X] T021 [US1] Add error handling for Google Sheets API failures with fallback to cached data

**Checkpoint**: At this point, User Story 1 should be fully functional - can query specific meals and get responses

---

## Phase 4: User Story 2 - Ask What to Cook Today (Priority: P2)

**Goal**: User can ask "what to cook today" and receive all remaining meals for the day in sequence

**Independent Test**: Ask "Alexa, what should I cook today?" at different times of day and verify only remaining meals are announced

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement get_remaining_meals() function in src/models/time_period.py to filter meals after current time
- [X] T023 [P] [US2] Implement get_today_meals() method in src/services/meal_service.py to get all meals for current day
- [X] T024 [US2] Create GetTodayMealsIntentHandler class in src/handlers/intent_handlers.py for GetTodayMealsIntent
- [X] T025 [US2] Implement build_multi_meal_response() in src/handlers/response_builder.py with SSML pauses and enumeration
- [X] T026 [US2] Add GetTodayMealsIntentHandler registration in src/lambda_function.py
- [X] T027 [US2] Add error handling for "all meals passed" scenario with tomorrow suggestion

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Ask About Specific Day and Meal (Priority: P3)

**Goal**: User can query meals for future days (e.g., "What's for dinner on Friday?")

**Independent Test**: Ask "Alexa, what's for breakfast on Saturday?" and verify correct future meal is returned

### Implementation for User Story 3

- [X] T028 [P] [US3] Implement parse_day_slot() utility in src/services/meal_service.py to handle day names and relative days (today, tomorrow)
- [X] T029 [P] [US3] Implement get_meal_for_day_and_period() method in src/services/meal_service.py
- [X] T030 [US3] Create GetSpecificDayMealIntentHandler class in src/handlers/intent_handlers.py for GetSpecificDayMealIntent
- [X] T031 [US3] Add GetSpecificDayMealIntentHandler registration in src/lambda_function.py
- [X] T032 [US3] Add validation for valid day names and meal periods with helpful error messages

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Additional Intent Handlers & Edge Cases

**Purpose**: Support intents and handle edge cases identified in spec.md

- [X] T033 [P] Create GetNextMealIntentHandler in src/handlers/intent_handlers.py for "what's next" queries
- [X] T034 [P] Create HelpIntentHandler in src/handlers/intent_handlers.py with usage examples
- [X] T035 [P] Create FallbackIntentHandler in src/handlers/intent_handlers.py with re-prompting
- [X] T036 [P] Create CancelAndStopIntentHandler in src/handlers/intent_handlers.py for AMAZON.CancelIntent and AMAZON.StopIntent
- [X] T037 Implement between_meal_periods handling in src/services/meal_service.py to calculate next meal
- [X] T038 Add Lambda execution context caching in src/lambda_function.py with global meal_plan variable
- [X] T039 Implement 24-hour cache TTL with _cache_timestamp tracking per spec clarification (FR-016)
- [X] T039a Create RefreshMealPlanIntent handler to invalidate cache for manual refresh (FR-017)

---

## Phase 7: Local Testing Infrastructure

**Purpose**: Enable local testing per FR-011 requirement

- [X] T040 [P] Create mock Alexa request builder functions in local_test/mock_alexa.py (create_intent_request, create_launch_request)
- [X] T041 [P] Create manual test script in local_test/manual_test.py with test cases for each intent
- [X] T042 [P] Create Google Sheets integration test script in local_test/test_sheets.py
- [X] T043 Create test runner in local_test/test_runner.py that executes all local tests and displays results
- [X] T044 Document local testing workflow in quickstart.md validation section

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T045 [P] Add comprehensive logging for all intent handlers using Python logging module
- [X] T046 [P] Add input validation for all Alexa slots with type checking
- [X] T047 [P] Create unit tests in tests/unit/test_time_periods.py for time period logic
- [X] T048 [P] Create unit tests in tests/unit/test_meal_service.py for meal lookup logic
- [X] T049 [P] Create unit tests in tests/unit/test_models.py for data class validation
- [X] T050 [P] Create integration tests in tests/integration/test_sheets_service.py with mock Google Sheets responses
- [X] T051 [P] Create integration tests in tests/integration/test_intent_handlers.py with mock Alexa events
- [X] T052 Add SSML enhancement for natural speech flow (pauses, emphasis) in all response builders
- [X] T053 Implement Alexa device timezone extraction from request context per spec clarification (NFR-006)
- [X] T054 Run quickstart.md setup and validation end-to-end
- [X] T055 Update docs/deployment.md for Alexa-hosted skills deployment (no AWS Lambda account required per NFR-001)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Additional Intents (Phase 6)**: Can start after Phase 3 (US1) is complete
- **Local Testing (Phase 7)**: Can start after Phase 3 (US1) is complete
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses US1 components but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Reuses US1 components but is independently testable

### Within Each User Story

- Models before services
- Services before handlers
- Handlers before Lambda registration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (T007-T009, T011, T014)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Phase 6 intent handlers (T033-T036) can all be implemented in parallel
- Phase 7 local test scripts (T040-T042) can all be created in parallel
- Phase 8 unit tests (T047-T049) can all be written in parallel
- Phase 8 integration tests (T050-T051) can be written in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models and utilities in parallel:
Task T015: "Implement get_current_meal_period() function in src/models/time_period.py"
Task T016: "Implement get_meal_for_period() method in src/services/meal_service.py"

# Then implement handler and response builder in parallel:
Task T017: "Create GetMealIntentHandler class in src/handlers/intent_handlers.py"
Task T018: "Implement build_meal_response() in src/handlers/response_builder.py"
```

---

## Parallel Example: Foundational Phase

```bash
# All data classes can be created in parallel:
Task T007: "Create Meal data class in src/models/meal_plan.py"
Task T008: "Create MealPlan data class in src/models/meal_plan.py"
Task T009: "Create MealQuery data class in src/models/meal_plan.py"

# Configuration files in parallel:
Task T011: "Create settings configuration in src/config/settings.py"

# Test fixtures in parallel:
Task T014: "Create test fixtures in tests/fixtures/mock_alexa_requests.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T015-T021)
4. **STOP and VALIDATE**: Test User Story 1 independently using local_test/manual_test.py
5. Deploy/demo if ready - you now have a working Alexa skill that answers "what's for dinner?"

### Incremental Delivery

1. Complete Setup + Foundational (T001-T014) → Foundation ready
2. Add User Story 1 (T015-T021) → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 (T022-T027) → Test independently → Deploy/Demo
4. Add User Story 3 (T028-T032) → Test independently → Deploy/Demo
5. Add Additional Intents (T033-T039) → Enhance UX → Deploy/Demo
6. Add Local Testing (T040-T044) → Improve developer experience
7. Polish (T045-T055) → Production-ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T005) + Foundational (T006-T014) together
2. Once Foundational is done:
   - Developer A: User Story 1 (T015-T021)
   - Developer B: User Story 2 (T022-T027)
   - Developer C: User Story 3 (T028-T032)
3. Developer A (after US1): Additional Intents (T033-T039)
4. Developer B (after US2): Local Testing (T040-T044)
5. Team: Polish together (T045-T055)

---

## Total Task Count

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 9 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 7 tasks 🎯 MVP
- **Phase 4 (User Story 2 - P2)**: 6 tasks
- **Phase 5 (User Story 3 - P3)**: 5 tasks
- **Phase 6 (Additional Intents)**: 8 tasks (includes RefreshMealPlanIntent)
- **Phase 7 (Local Testing)**: 5 tasks
- **Phase 8 (Polish)**: 11 tasks

**Total**: 56 tasks

---

## Suggested MVP Scope

**Minimum Viable Product** = Phases 1-3 only (21 tasks: T001-T021)

This delivers:
- ✅ Complete project setup
- ✅ Google Sheets integration
- ✅ Core meal query functionality ("What's for dinner?")
- ✅ Error handling for empty meals and API failures
- ✅ Testable locally per FR-011

**Time Estimate**: 2-3 days for experienced developer, 4-5 days for learning Python + Alexa SDK

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Foundational phase (T006-T014) is CRITICAL and blocks all user stories
- Local testing infrastructure (Phase 7) ensures FR-011 compliance
- Tests are not included in main flow but covered in Polish phase (optional)
