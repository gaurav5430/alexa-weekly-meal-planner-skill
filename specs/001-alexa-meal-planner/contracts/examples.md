# Alexa Voice Interaction Examples

This document provides example conversations for testing the meal planner skill.

## Conversation Flow 1: Ask About Specific Meal

**User**: "Alexa, ask meal planner what's for dinner"  
**Alexa**: "For dinner today, you should prepare Grilled Chicken with Vegetables."

---

## Conversation Flow 2: Ask About Specific Day and Meal

**User**: "Alexa, ask meal planner what's for breakfast on Friday"  
**Alexa**: "For breakfast on Friday, you should prepare Pancakes with Maple Syrup."

---

## Conversation Flow 3: What to Cook Today

**User**: "Alexa, ask meal planner what should I cook today"  
**Alexa**: "Here's what you should cook today: 1. For breakfast, Oatmeal with Berries. 2. For morning snack, Greek Yogurt. 3. For lunch, Caesar Salad. 4. For evening snack, Mixed Nuts. 5. For dinner, Grilled Chicken with Vegetables."

**User** (asking later in the day at 2 PM): "Alexa, ask meal planner what should I cook today"  
**Alexa**: "Here's what you should cook today: 1. For lunch, Caesar Salad. 2. For evening snack, Mixed Nuts. 3. For dinner, Grilled Chicken with Vegetables."

---

## Conversation Flow 4: Next Meal

**User** (at 10:30 AM): "Alexa, ask meal planner what's next"  
**Alexa**: "Your next meal is morning snack at 11 AM, and you should prepare Greek Yogurt."

---

## Conversation Flow 5: Error - Empty Meal Slot

**User**: "Alexa, ask meal planner what's for lunch on Saturday"  
**Alexa**: "You haven't set a meal for lunch on Saturday. Would you like to check another day?"

---

## Conversation Flow 6: Error - All Meals Passed

**User** (at 11 PM): "Alexa, ask meal planner what should I cook today"  
**Alexa**: "All meals for today have already passed. Would you like to hear tomorrow's plan?"

---

## Conversation Flow 7: Between Meal Periods

**User** (at 3:30 PM): "Alexa, ask meal planner what's next"  
**Alexa**: "It's currently between meal times. Your next meal is evening snack at 4 PM, and you should prepare Mixed Nuts."

---

## Conversation Flow 8: Using Synonyms

**User**: "Alexa, ask meal planner what's for supper"  
**Alexa**: "For dinner today, you should prepare Grilled Chicken with Vegetables."

**User**: "Alexa, ask meal planner what's for the noon meal"  
**Alexa**: "For lunch today, you should prepare Caesar Salad."

---

## Intent Mapping Reference

| User Utterance | Intent Name | Slots | Query Type |
|----------------|-------------|-------|------------|
| "what's for dinner" | GetMealIntent | MealType=dinner | specific_meal |
| "what's for breakfast on Friday" | GetSpecificDayMealIntent | MealType=breakfast, DayOfWeek=Friday | specific_day_meal |
| "what should I cook today" | GetTodayMealsIntent | (none) | today_meals |
| "what's next" | GetNextMealIntent | (none) | next_meal |
