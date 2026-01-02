# Feature Specification: Alexa Weekly Meal Planner

**Feature Branch**: `001-alexa-meal-planner`  
**Created**: 2026-01-01  
**Status**: Draft  
**Input**: User description: "Alexa skill which can help figure out the meal plan for a certain day and time in the week. The meal plan would be manually curated in a google sheet by me. Alexa skill would need to read from that google sheet, parse the data, and based on the time of the day and the current week, announce what should be prepared for the next meal."

## Clarifications

### Session 2026-01-01

- Q: Deployment & hosting approach (given no AWS Lambda account available) → A: Use Alexa-hosted skills (Amazon provides free hosting, requires minimal AWS credentials for Google Sheets API access only)
- Q: Google Sheets data refresh strategy → A: 24 hour cache with manual override as needed
- Q: Empty meal slot behavior → A: Announce "No meal planned for [meal time] on [day]" explicitly
- Q: Timezone handling → A: Use the timezone from the user's Alexa device/account settings (automatic, no config needed)
- Q: Off-hours query behavior (outside defined meal periods) → A: Announce next upcoming meal (e.g., "No meal now, but breakfast is scheduled at 8 AM tomorrow: [meal name]")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask About Next Meal (Priority: P1)

A user asks Alexa what meal to prepare next, and Alexa responds with the meal information based on the current time and day of the week from the Google Sheet meal plan.

**Why this priority**: This is the core value proposition - getting meal information quickly through voice interaction. Without this, the skill has no purpose.

**Independent Test**: Can be fully tested by asking "Alexa, what should I cook next?" at different times of day and verifying the response matches the Google Sheet data for that time slot and delivers the correct meal name.

**Acceptance Scenarios**:

1. **Given** it is Monday at 11:30 AM, **When** user asks "Alexa, what's for morning snack?", **Then** Alexa announces the Monday morning snack meal from the Google Sheet
2. **Given** it is Wednesday at 8:00 PM, **When** user asks "Alexa, what should I cook for dinner?", **Then** Alexa announces the Wednesday dinner meal from the Google Sheet
3. **Given** it is Sunday at 9:00 AM, **When** user asks "Alexa, what's for breakfast?", **Then** Alexa announces the Sunday breakfast meal from the Google Sheet
4. **Given** it is Tuesday at 5:00 PM, **When** user asks "Alexa, what's for evening snack?", **Then** Alexa announces the Tuesday evening snack meal from the Google Sheet

---

### User Story 2 - Ask What to Cook Today (Priority: P2)

A user asks Alexa in the morning "what to cook today" and receives all remaining meals for the current day, helping them plan their entire day's cooking.

**Why this priority**: This is a primary use case mentioned by the user - getting the full day's meal plan at once for comprehensive planning and preparation.

**Independent Test**: Can be fully tested by asking "Alexa, what should I cook today?" at different times and verifying all remaining meals for that day are announced in sequence.

**Acceptance Scenarios**:

1. **Given** it is Monday at 9:00 AM, **When** user asks "Alexa, what should I cook today?", **Then** Alexa announces breakfast, morning snack, lunch, evening snack, and dinner for Monday in sequence
2. **Given** it is Wednesday at 1:00 PM, **When** user asks "Alexa, what should I cook today?", **Then** Alexa announces lunch, evening snack, and dinner for Wednesday (skipping already-passed meals)
3. **Given** it is Friday at 11:30 PM, **When** user asks "Alexa, what should I cook today?", **Then** Alexa informs the user that all meals for today have passed

---

### User Story 3 - Ask About Specific Day and Meal (Priority: P3)

A user asks Alexa about a meal for a specific day and time (e.g., "What's for dinner on Friday?"), allowing meal planning ahead of time.

**Why this priority**: Enables proactive meal planning and grocery shopping, adding value beyond the immediate use cases.

**Independent Test**: Can be fully tested by asking "Alexa, what's for [meal] on [day]?" and verifying the response matches the Google Sheet data for that specific day and meal combination.

**Acceptance Scenarios**:

1. **Given** the current day is Monday, **When** user asks "Alexa, what's for dinner on Friday?", **Then** Alexa announces the Friday dinner meal from the Google Sheet
2. **Given** any day of the week, **When** user asks "Alexa, what's for lunch tomorrow?", **Then** Alexa announces the next day's lunch meal from the Google Sheet
3. **Given** user wants to know about evening snack, **When** user asks "Alexa, what's for evening snack on Saturday?", **Then** Alexa announces the Saturday evening snack meal

---

### Edge Cases

- What happens when the Google Sheet is unavailable or can't be accessed?
- Off-hours queries: When current time doesn't match any defined meal period (e.g., 3:30 AM or 10:30 PM), system announces next upcoming meal
- Empty meal slots: System announces "No meal planned for [meal time] on [day]" explicitly
- What happens when the user asks about a meal using different phrasing or synonyms (e.g., "snack" vs "evening snack")?
- Timezone: System uses user's Alexa device timezone automatically (no manual configuration needed)
- What happens during the first launch if data hasn't been loaded yet?
- What happens when user asks "what to cook today" and all meals have already passed?
- How does the system handle gaps between meal time periods (e.g., between 3 PM and 4 PM)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read meal plan data from a Google Sheet specified by the user
- **FR-002**: System MUST identify the current day of the week and time of day using the user's Alexa device timezone
- **FR-003**: System MUST determine which meal period applies based on the current time using these boundaries: Breakfast (8:00 AM - 11:00 AM), Morning Snack (11:00 AM - 12:00 PM), Lunch (12:00 PM - 3:00 PM), Evening Snack (4:00 PM - 6:00 PM), Dinner (7:00 PM - 10:00 PM)
- **FR-004**: System MUST match the day and meal period to the corresponding entry in the Google Sheet
- **FR-005**: System MUST respond via voice with the meal name/description from the matched entry
- **FR-006**: System MUST support queries about specific days (e.g., "What's for dinner on Friday?")
- **FR-007**: System MUST support queries about specific meal types (e.g., "What's for breakfast?", "What's for evening snack?")
- **FR-008**: System MUST handle natural language variations for queries (e.g., "lunch", "noon meal", "midday", "snack", "evening snack")
- **FR-009**: System MUST provide meaningful error messages when the Google Sheet is unavailable
- **FR-010**: System MUST provide helpful responses when no meal is defined for a requested time slot (announce "No meal planned for [meal time] on [day]")
- **FR-011**: System MUST be testable locally without deploying to Alexa cloud services
- **FR-012**: System MUST parse meal data from the Google Sheet where days are organized as rows and meal types as columns (Column A: Day, Column B: Breakfast, Column C: Morning Snack, Column D: Lunch, Column E: Evening Snack, Column F: Dinner)
- **FR-013**: System MUST support "what to cook today" queries by returning all remaining meals for the current day based on the current time
- **FR-014**: System MUST announce multiple meals in a natural, sequential manner when responding to "what to cook today" queries
- **FR-015**: System MUST be deployable using Alexa-hosted skills platform (no AWS Lambda account required)
- **FR-016**: System MUST cache Google Sheets data for 24 hours to minimize API calls
- **FR-017**: System MUST provide a manual refresh command to reload data from Google Sheets on-demand (bypassing cache)
- **FR-018**: System MUST announce the next upcoming meal when queried outside defined meal periods (e.g., "No meal scheduled now, but breakfast is at 8 AM tomorrow: [meal name]")

### Non-Functional Requirements

- **NFR-001**: Deployment uses Alexa-hosted skills infrastructure provided by Amazon
- **NFR-002**: Google Sheets API access configured using service account credentials (minimal AWS/cloud setup)
- **NFR-003**: Skill remains private to developer account (not published to Alexa Skills Store)
- **NFR-004**: Data cache expires after 24 hours, triggering automatic refresh on next query
- **NFR-005**: Manual refresh command available to force immediate cache invalidation and data reload
- **NFR-006**: Timezone determination uses Alexa device settings from request context (no user configuration required)

### Key Entities

- **Meal Plan**: Weekly schedule of meals organized by day and meal period, sourced from Google Sheet
  - Attributes: Day of week, meal period (breakfast/morning snack/lunch/evening snack/dinner), meal name/description
  - Relationships: Five meals per day, organized by time periods

- **Meal Query**: User's voice request for meal information
  - Attributes: Target day (current/specific), meal period (next/specific/all remaining), query timestamp, query type (single meal/what to cook today/specific day-meal)
  - Relationships: Maps to one or more meals in the meal plan

- **Time Period**: Definition of when each meal is served
  - Attributes: Start time, end time, meal type label
  - Relationships: Used to determine which meal period applies to current time and which meals remain for the day

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can get meal information within 3 seconds of asking Alexa
- **SC-002**: System correctly identifies the appropriate meal for the current time at least 95% of the time
- **SC-003**: Users successfully receive meal information on first query attempt in 90% of interactions
- **SC-004**: System handles Google Sheet data refresh without user intervention
- **SC-005**: Local testing environment allows developers to test all voice interactions without cloud deployment
- **SC-006**: System gracefully handles unavailable data and provides helpful guidance in 100% of error cases
