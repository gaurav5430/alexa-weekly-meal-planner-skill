# Data Model: Alexa Weekly Meal Planner

**Date**: 2026-01-01  
**Purpose**: Define core data structures and relationships

## Core Entities

### 1. TimePeriod

**Purpose**: Defines when each meal type is served during the day

**Attributes**:
- `name` (string): Meal period identifier ("breakfast", "morning_snack", "lunch", "evening_snack", "dinner")
- `start_time` (time): Beginning of meal period (e.g., 08:00)
- `end_time` (time): End of meal period (e.g., 11:00)
- `display_name` (string): Human-friendly name ("Breakfast", "Morning Snack", etc.)

**Validation Rules**:
- start_time must be before end_time
- No overlapping periods allowed
- All times in 24-hour format

**State Transitions**: None (immutable configuration)

**Example**:
```python
TimePeriod(
    name="breakfast",
    start_time=time(8, 0),
    end_time=time(11, 0),
    display_name="Breakfast"
)
```

---

### 2. Meal

**Purpose**: Represents a single meal entry from the Google Sheet

**Attributes**:
- `day_of_week` (string): Day name ("Monday", "Tuesday", ..., "Sunday")
- `meal_period` (string): Period name ("breakfast", "morning_snack", "lunch", "evening_snack", "dinner")
- `name` (string): Meal description/name from Google Sheet
- `is_empty` (boolean): True if meal slot has no data

**Validation Rules**:
- day_of_week must be valid weekday name
- meal_period must match defined TimePeriod names
- name can be empty string (indicates is_empty=True)

**State Transitions**: None (read-only from Google Sheet)

**Relationships**:
- Associated with one TimePeriod via meal_period
- Part of one MealPlan

**Example**:
```python
Meal(
    day_of_week="Monday",
    meal_period="breakfast",
    name="Oatmeal with berries",
    is_empty=False
)
```

---

### 3. MealPlan

**Purpose**: Weekly collection of all meals, organized by day and period

**Attributes**:
- `meals` (dict): Nested dictionary structure {day: {period: Meal}}
- `last_updated` (datetime): Timestamp of last Google Sheets fetch
- `sheet_id` (string): Google Sheet identifier
- `is_valid` (boolean): True if sheet structure validated successfully

**Validation Rules**:
- Must contain all 7 days
- Each day must contain all 5 meal periods
- Allows empty meal entries (is_empty=True)

**State Transitions**:
- **Uninitialized** → **Loading** (fetch from Google Sheets)
- **Loading** → **Valid** (successful load and validation)
- **Loading** → **Invalid** (validation failed)
- **Valid** → **Stale** (cache expiration threshold reached)
- **Stale** → **Loading** (refresh triggered)

**Relationships**:
- Contains 35 Meal objects (7 days × 5 periods)
- References multiple TimePeriod definitions

**Example Structure**:
```python
{
    "Monday": {
        "breakfast": Meal(...),
        "morning_snack": Meal(...),
        "lunch": Meal(...),
        "evening_snack": Meal(...),
        "dinner": Meal(...)
    },
    "Tuesday": { ... },
    ...
}
```

---

### 4. MealQuery

**Purpose**: Represents user's voice request for meal information

**Attributes**:
- `query_type` (enum): Type of query ("next_meal", "specific_meal", "specific_day_meal", "today_meals")
- `target_day` (string, optional): Specific day requested (e.g., "Friday", "tomorrow")
- `target_period` (string, optional): Specific meal period (e.g., "dinner")
- `query_time` (datetime): When query was made
- `timezone` (string): User's timezone (from Alexa request)

**Validation Rules**:
- query_type must be valid enum value
- target_day must be valid day name or relative ("today", "tomorrow")
- target_period must match TimePeriod names if provided

**State Transitions**: None (ephemeral request object)

**Relationships**:
- Resolves to one or more Meal objects from MealPlan
- Uses TimePeriod definitions for time-based queries

**Query Type Mapping**:

| Query Type | User Utterance Example | Required Attributes | Returns |
|------------|------------------------|---------------------|---------|
| next_meal | "What's for lunch?" | query_time | Single Meal |
| specific_meal | "What's for dinner?" | target_period, query_time | Single Meal for today |
| specific_day_meal | "What's for breakfast on Friday?" | target_day, target_period | Single Meal |
| today_meals | "What should I cook today?" | query_time | List of remaining Meals |

**Example**:
```python
MealQuery(
    query_type="specific_day_meal",
    target_day="Friday",
    target_period="dinner",
    query_time=datetime.now(),
    timezone="America/Los_Angeles"
)
```

---

## Data Flow

```
Google Sheet (external)
    ↓
[SheetsService] fetch & parse
    ↓
MealPlan (cached in Lambda)
    ↓
[MealService] query + filter
    ↓
MealQuery → resolved Meal(s)
    ↓
[ResponseBuilder] format speech
    ↓
Alexa Response (voice)
```

---

## Google Sheet Structure

**Expected Format**:

| Day       | Breakfast | Morning Snack | Lunch | Evening Snack | Dinner |
|-----------|-----------|---------------|-------|---------------|--------|
| Monday    | Oatmeal   | Apple         | Salad | Nuts          | Pasta  |
| Tuesday   | Eggs      | Yogurt        | Soup  | Carrots       | Chicken|
| ...       | ...       | ...           | ...   | ...           | ...    |

**Column Mapping**:
- Column A: Day of week (header: "Day")
- Column B: Breakfast meal (header: "Breakfast")
- Column C: Morning snack (header: "Morning Snack")
- Column D: Lunch meal (header: "Lunch")
- Column E: Evening snack (header: "Evening Snack")
- Column F: Dinner meal (header: "Dinner")

**Validation**:
- Row 1 must contain headers (exact match, case-insensitive)
- Rows 2-8 must contain day names (Monday-Sunday)
- Order of days doesn't matter (service will map by name)
- Empty cells are allowed (treated as is_empty=True)

---

## Caching Strategy

**Cache Location**: Lambda global variable (in-memory)

**Cache Key**: Sheet ID (supports multiple users if needed)

**Cache Lifetime**: 
- Duration: Until Lambda cold start (~5-15 minutes typical)
- Staleness threshold: 1 hour (trigger warning but still serve)
- Refresh trigger: Manual refresh intent or cold start

**Cache Invalidation**:
- Lambda cold start (automatic)
- Manual refresh command (user intent)
- Validation failure (force re-fetch)

**Fallback Behavior**:
- If API fails: Serve stale cache with warning ("using yesterday's plan")
- If cache empty: Return error response

---

## Error States

### Empty Meal Slot

**Scenario**: User asks for meal that has no data in sheet

**Data Representation**:
```python
Meal(
    day_of_week="Wednesday",
    meal_period="lunch",
    name="",
    is_empty=True
)
```

**Response**: "You haven't set a meal for lunch on Wednesday."

---

### Invalid Sheet Structure

**Scenario**: Google Sheet doesn't match expected format

**Detection**: 
- Missing headers
- Wrong number of columns
- Missing day rows

**Response**: Set `MealPlan.is_valid = False`, return error to user

---

### Between Meal Periods

**Scenario**: Current time is outside all defined meal periods (e.g., 3:30 AM or 10:30 PM)

**Handling**:
- Calculate next upcoming meal period
- Respond with next meal info

**Example**: "It's currently between meal times. Your next meal is breakfast at 8 AM, and you should prepare Oatmeal."

---

### All Meals Passed

**Scenario**: User asks "what to cook today" at 11 PM

**Handling**:
- Detect that all meal periods have ended
- Offer tomorrow's plan

**Response**: "All meals for today have already passed. Would you like to hear tomorrow's plan?"

---

## Summary

**Total Entities**: 4 (TimePeriod, Meal, MealPlan, MealQuery)

**Data Sources**: 
- Google Sheets (external, read-only)
- TimePeriod configuration (code-defined)

**Persistence**: 
- None required (stateless skill)
- In-memory caching only

**Key Relationships**:
- MealPlan contains 35 Meals (7 days × 5 periods)
- Each Meal maps to one TimePeriod
- MealQuery resolves to one or more Meals
