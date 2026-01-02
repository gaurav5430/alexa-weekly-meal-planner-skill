# Research: Alexa Weekly Meal Planner

**Date**: 2026-01-01  
**Purpose**: Resolve technical unknowns and establish best practices for implementation  
**Updated**: 2026-01-01 - Added Alexa-hosted deployment and 24-hour caching clarifications

## Research Areas

### 0. Alexa-Hosted Skills Deployment (New Requirement)

**Decision**: Use Alexa-hosted skills platform instead of manual AWS Lambda deployment

**Rationale**:
- User does not have AWS account for Lambda deployment (spec clarification)
- Alexa-hosted skills provide free hosting managed by Amazon
- No AWS account required - only Alexa Developer account needed
- Amazon provides Git repository, automatic Lambda deployment, and CloudWatch logs
- Supports Python 3.11 runtime
- Simplifies credential management via environment variables in Alexa console
- Automatic scaling and high availability handled by Amazon

**Alternatives Considered**:
- **Self-hosted HTTPS endpoint**: Rejected - requires public server, SSL certificates, operational overhead
- **Manual AWS Lambda**: Rejected - user explicitly has no AWS account
- **Third-party cloud platforms**: Rejected - Alexa-hosted is simpler and officially supported

**Implementation Approach**:
1. Create skill in Alexa Developer Console
2. Select "Alexa-Hosted (Python)" as backend resource
3. Clone provided Git repository or use web-based code editor
4. Configure environment variables for Google Sheets credentials (base64-encoded JSON)
5. Push code to trigger automatic deployment
6. Test via Alexa Simulator or registered device

**Environment Variable Setup**:
```bash
# In Alexa Developer Console → Code → Environment Variables
GOOGLE_CREDENTIALS_BASE64=<base64-encoded service account JSON>
GOOGLE_SHEET_ID=<Google Sheets ID from URL>
DEFAULT_TIMEZONE=America/New_York  # Fallback if device timezone unavailable
```

**Deployment Command**:
```bash
# Via ASK CLI (if preferred over web console)
ask deploy --target skill-infrastructure
```

**Documentation**: https://developer.amazon.com/docs/alexa/hosted-skills/alexa-hosted-skills-create.html

---

### 0a. 24-Hour Cache Strategy (New Requirement)

**Decision**: Implement 24-hour cache TTL with manual refresh intent, replacing 1-hour cache

**Rationale**:
- Spec clarification: user prefers 24-hour cache to minimize Google Sheets API calls
- Meal plans change infrequently (weekly curation), daily refresh is sufficient
- Reduces API quota consumption (well within free tier limits)
- Manual refresh command provides override when user updates sheet mid-day
- Lambda global variables persist across warm invocations (typically 15+ minutes)
- For cold starts, cache timestamp check forces fresh fetch

**Alternatives Considered**:
- **1-hour cache**: Rejected - spec updated to 24-hour preference
- **No cache/real-time**: Rejected - slow responses, excessive API calls, quota risk
- **Cache in S3/DynamoDB**: Rejected - over-engineering for single-user skill, adds latency

**Implementation Approach**:
```python
from datetime import datetime, timedelta

CACHE_DURATION_HOURS = 24  # Changed from 60 minutes

_cached_meal_plan = None
_cache_timestamp = None

def get_meal_plan():
    global _cached_meal_plan, _cache_timestamp
    
    now = datetime.now()
    
    # Check if cache is valid (< 24 hours old)
    if _cached_meal_plan and _cache_timestamp:
        cache_age = now - _cache_timestamp
        if cache_age < timedelta(hours=CACHE_DURATION_HOURS):
            return _cached_meal_plan
    
    # Cache miss or expired - fetch fresh data
    _cached_meal_plan = fetch_from_google_sheets()
    _cache_timestamp = now
    return _cached_meal_plan

def invalidate_cache():
    """Called by RefreshMealPlanIntent"""
    global _cache_timestamp
    _cache_timestamp = None
```

**Manual Refresh Intent**:
- Intent name: `RefreshMealPlanIntent`
- Sample utterances: "refresh", "reload", "update meal plan", "refresh data"
- Handler clears `_cache_timestamp`, next query fetches fresh data
- Response: "I've refreshed your meal plan from Google Sheets. What would you like to know?"

---

### 1. Local Testing Framework for Alexa Skills

**Decision**: Use custom mock approach with pytest

**Rationale**: 
- ask-sdk-local-debug is officially deprecated and no longer maintained
- Custom mocks provide full control over request/response flow
- pytest fixtures can simulate all Alexa request types (LaunchRequest, IntentRequest, SessionEndedRequest)
- Easier to test edge cases and error conditions with custom mocks
- No dependency on Alexa cloud services during development

**Alternatives Considered**:
- **ask-sdk-local-debug**: Rejected - officially deprecated, security vulnerabilities, no Python 3.9+ support
- **Bespoken Tools**: Rejected - requires external service, adds complexity, not free for all features
- **AWS SAM Local**: Rejected - requires Docker and Lambda simulation, overkill for unit testing

**Implementation Approach**:
```python
# Create mock Alexa request builders
def create_intent_request(intent_name, slots=None):
    return {
        "version": "1.0",
        "session": {...},
        "request": {
            "type": "IntentRequest",
            "intent": {"name": intent_name, "slots": slots or {}}
        }
    }
```

---

### 2. Google Sheets API Integration Best Practices

**Decision**: Use gspread library with service account authentication and local caching

**Rationale**:
- gspread is the most mature Python library for Google Sheets (10k+ stars, active maintenance)
- Service account auth avoids OAuth user consent flow (better for personal automation)
- Built-in caching reduces API calls and improves response time
- Supports reading ranges efficiently (can fetch entire week in one call)
- Handles rate limiting internally

**Alternatives Considered**:
- **google-api-python-client**: Rejected - more complex, requires manual caching, verbose API
- **pygsheets**: Rejected - less mature, fewer features, smaller community
- **Direct REST API**: Rejected - requires manual OAuth handling, more boilerplate

**Implementation Approach**:
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet('Meal Plan')

# Fetch all data once, cache in memory for Lambda execution
meal_data = sheet.get_all_records()
```

**Caching Strategy**:
- Lambda execution context reuse: Store sheet data in global variable
- Cache duration: 24 hours (spec requirement), manual refresh available
- Refresh trigger: Automatic after 24 hours or via RefreshMealPlanIntent
- Fallback: Return cached data if API fails, with staleness warning

---

### 3. Alexa Skills Kit Python SDK Patterns

**Decision**: Use ask-sdk-core with skill builder pattern and custom intent handlers

**Rationale**:
- Official Amazon SDK with comprehensive documentation
- Skill builder provides clean dependency injection
- Custom handlers allow modular, testable code
- Supports all Alexa features (slots, dialogs, session attributes)
- Integrates well with AWS Lambda

**Best Practices**:
- Separate intent handlers into individual functions/classes
- Use skill builder to register handlers
- Extract business logic into service layer (not in handlers)
- Use response builder for consistent SSML formatting
- Implement error handlers for graceful degradation

**Implementation Pattern**:
```python
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler

class GetMealIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetMealIntent")(handler_input)
    
    def handle(self, handler_input):
        meal = meal_service.get_meal(...)
        speech = f"For {meal_type}, you should prepare {meal.name}"
        return handler_input.response_builder.speak(speech).response

sb = SkillBuilder()
sb.add_request_handler(GetMealIntentHandler())
lambda_handler = sb.lambda_handler()
```

---

### 4. Time Period Logic and Meal Determination

**Decision**: Use Python datetime with custom TimePeriod class and timezone awareness

**Rationale**:
- Need to determine current meal period based on time of day
- Must handle edge cases (between meal times, late night queries)
- Should be timezone-aware for accuracy
- Must support "remaining meals today" calculation

**Implementation Approach**:
```python
from dataclasses import dataclass
from datetime import time

@dataclass
class TimePeriod:
    name: str
    start: time
    end: time
    
    def contains(self, current_time: time) -> bool:
        return self.start <= current_time < self.end

MEAL_PERIODS = [
    TimePeriod("breakfast", time(8, 0), time(11, 0)),
    TimePeriod("morning_snack", time(11, 0), time(12, 0)),
    TimePeriod("lunch", time(12, 0), time(15, 0)),
    TimePeriod("evening_snack", time(16, 0), time(18, 0)),
    TimePeriod("dinner", time(19, 0), time(22, 0)),
]

def get_current_meal_period(current_time):
    for period in MEAL_PERIODS:
        if period.contains(current_time):
            return period
    return None  # Between meal times

def get_remaining_meals(current_time):
    current_hour_min = current_time.hour * 60 + current_time.minute
    remaining = []
    for period in MEAL_PERIODS:
        period_start_min = period.start.hour * 60 + period.start.minute
        if period_start_min >= current_hour_min:
            remaining.append(period)
    return remaining
```

---

### 5. Response Format for Multiple Meals ("What to Cook Today")

**Decision**: Use SSML with pauses and enumeration for natural speech flow

**Rationale**:
- Must announce multiple meals in sequence without overwhelming user
- SSML allows control over pacing and intonation
- Enumeration helps user track list items
- Pauses between items improve comprehension

**Implementation Approach**:
```python
def build_multi_meal_response(meals):
    if not meals:
        return "All meals for today have already passed."
    
    speech_parts = ["Here's what you should cook today: "]
    for i, (period, meal) in enumerate(meals, 1):
        speech_parts.append(f"{i}. For {period}, {meal.name}.")
        if i < len(meals):
            speech_parts.append('<break time="500ms"/>')
    
    return f'<speak>{"".join(speech_parts)}</speak>'
```

---

### 6. Error Handling and Fallback Strategies

**Decision**: Implement graceful degradation with informative error messages

**Rationale**:
- Google Sheets API may be unavailable
- Sheet data may be malformed
- Network issues can occur
- User must receive helpful guidance

**Error Scenarios and Responses**:

| Scenario | User Response | Technical Action |
|----------|---------------|------------------|
| Google Sheets API down | "I'm having trouble accessing your meal plan. Please try again later." | Return cached data if available, log error |
| Empty meal slot | "You haven't set a meal for [period] on [day]. Would you like to check another day?" | Continue execution, offer alternatives |
| Invalid day/meal query | "I didn't catch that. You can ask about breakfast, lunch, dinner, or snacks for any day of the week." | Re-prompt with examples |
| Between meal times | "It's currently between meal times. The next meal is [next_meal] at [time]." | Calculate next upcoming meal |
| All meals passed | "All meals for today have already passed. Would you like to hear tomorrow's plan?" | Offer next day as alternative |

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime | Python | 3.11 |
| Alexa SDK | ask-sdk-core | 1.19.0 |
| Google Sheets | gspread | 5.12.0 |
| Authentication | oauth2client | 4.1.3 |
| Testing | pytest | 7.4.3 |
| Mocking | pytest-mock | 3.12.0 |
| Date/Time | datetime | stdlib |
| Environment | python-dotenv | 1.0.0 (local dev) |
| Deployment | Alexa-hosted | Python 3.11 runtime |

---

## Security Considerations

**Google Service Account**:
- Store credentials as base64-encoded JSON in Alexa environment variables (production)
- Use environment variables for local development (.env file, gitignored)
- Never commit credentials.json to repository
- Restrict service account to read-only access on specific sheet
- Environment variable: `GOOGLE_CREDENTIALS_BASE64`

**Alexa Skill**:
- Verify request signatures in production (ask-sdk-core handles automatically)
- Use skill ID verification
- No PII storage required (stateless queries)
- Session data only lives during conversation
- Private skill (not published to Alexa Skills Store per spec)

---

## Open Questions Resolved

1. **Q: Local testing framework?**  
   **A**: Custom pytest mocks, no external dependencies

2. **Q: Caching strategy?**  
   **A**: 24-hour cache TTL with manual refresh intent (spec clarification)

3. **Q: How to handle "what to cook today"?**  
   **A**: Filter meals by comparing current time against meal period start times, return remaining meals only

4. **Q: Timezone handling?**  
   **A**: Use user's Alexa device timezone from request context (spec clarification), default to configured timezone if unavailable

5. **Q: Sheet structure validation?**  
   **A**: Validate on first load, cache validation result, return helpful error if structure incorrect

6. **Q: Deployment approach without AWS account?**  
   **A**: Alexa-hosted skills platform (spec clarification), no AWS account required

7. **Q: Manual cache refresh implementation?**  
   **A**: RefreshMealPlanIntent that invalidates cache timestamp, next query fetches fresh data
