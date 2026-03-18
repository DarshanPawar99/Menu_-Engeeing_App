
## **Planning Config Note**

Added `include_weekends` Boolean flag (default `True`) to control whether Saturday/Sunday are included in planning dates. When `False`, `MenuSolver._get_planning_dates()` skips weekends and `CuisineMenuRule.apply()` ignores weekend days even if a rule lists them. This is set via `main.py` `--include-weekends/--no-include-weekends` and passed through `planning_config` to rule context.

## **Mathematical Formulation**

### **Decision Variables**

Let's say we have:
- **3 menu items**: Pasta (P), Chicken Curry (C), Ice Cream (I)
- **2 days**: Monday and Tuesday
- Each item belongs to a course: Pasta = main, Chicken = main, Ice Cream = dessert

We create **binary decision variables**:

**x_{i,d}** = 1 if item i is selected on day d, 0 otherwise

So we have 6 variables:
- x_{P,Mon}, x_{P,Tue} (Pasta on Monday/Tuesday)
- x_{C,Mon}, x_{C,Tue} (Chicken on Monday/Tuesday)  
- x_{I,Mon}, x_{I,Tue} (Ice Cream on Monday/Tuesday)

---

## **Concrete Example**

### **Menu Items Available:**

| Item ID | Name | Course Type | Cuisine Family |
|---------|------|-------------|----------------|
| 1 | Pasta Carbonara | main | italian |
| 2 | Chicken Tikka | main | indian |
| 3 | Rice Biryani | main | indian |
| 4 | Caesar Salad | starter | italian |
| 5 | Samosa | starter | indian |
| 6 | Tiramisu | dessert | italian |
| 7 | Gulab Jamun | dessert | indian |

### **Planning Period:**
- Monday, Tuesday, Wednesday

### **Meal Composition Requirements:**
Each day must have:
- Exactly **1 starter**
- Exactly **1 main course**
- Exactly **1 dessert**

### **Cuisine Constraint:**
- Italian cuisine can **only** be served on **Monday and Wednesday**
- Indian cuisine can be served **any day**

---

## **Decision Variables (21 total)**

x_{1,Mon}, x_{1,Tue}, x_{1,Wed} (Pasta Carbonara)  
x_{2,Mon}, x_{2,Tue}, x_{2,Wed} (Chicken Tikka)  
x_{3,Mon}, x_{3,Tue}, x_{3,Wed} (Rice Biryani)  
x_{4,Mon}, x_{4,Tue}, x_{4,Wed} (Caesar Salad)  
x_{5,Mon}, x_{5,Tue}, x_{5,Wed} (Samosa)  
x_{6,Mon}, x_{6,Tue}, x_{6,Wed} (Tiramisu)  
x_{7,Mon}, x_{7,Tue}, x_{7,Wed} (Gulab Jamun)

Each variable ∈ {0, 1}

---

## **Constraints**

### **1. Meal Composition Constraints (for each day)**

**Monday:**
- **Starters:** x_{4,Mon} + x_{5,Mon} = 1 (exactly 1 starter)
- **Mains:** x_{1,Mon} + x_{2,Mon} + x_{3,Mon} = 1 (exactly 1 main)
- **Desserts:** x_{6,Mon} + x_{7,Mon} = 1 (exactly 1 dessert)
- **Total items:** x_{1,Mon} + x_{2,Mon} + x_{3,Mon} + x_{4,Mon} + x_{5,Mon} + x_{6,Mon} + x_{7,Mon} = 3

**Tuesday:** (same pattern)
- x_{4,Tue} + x_{5,Tue} = 1
- x_{1,Tue} + x_{2,Tue} + x_{3,Tue} = 1
- x_{6,Tue} + x_{7,Tue} = 1
- Total = 3

**Wednesday:** (same pattern)
- x_{4,Wed} + x_{5,Wed} = 1
- x_{1,Wed} + x_{2,Wed} + x_{3,Wed} = 1
- x_{6,Wed} + x_{7,Wed} = 1
- Total = 3

### **2. Cuisine Constraints**

**Italian items can only appear on Monday & Wednesday:**

**Tuesday (NOT allowed for Italian):**
- x_{1,Tue} + x_{4,Tue} + x_{6,Tue} = 0 (no Italian items on Tuesday)

**Monday & Wednesday (Italian allowed):**
- No constraint (can be 0 or more)

---

## **Solving the System**

The solver searches for values of all x_{i,d} ∈ {0, 1} that satisfy ALL constraints.

### **One Valid Solution:**

**Monday:**
- x_{4,Mon} = 1 (Caesar Salad - Italian starter) ✓
- x_{1,Mon} = 1 (Pasta Carbonara - Italian main) ✓
- x_{6,Mon} = 1 (Tiramisu - Italian dessert) ✓
- All other Monday variables = 0

**Tuesday:**
- x_{5,Tue} = 1 (Samosa - Indian starter) ✓
- x_{2,Tue} = 1 (Chicken Tikka - Indian main) ✓
- x_{7,Tue} = 1 (Gulab Jamun - Indian dessert) ✓
- All other Tuesday variables = 0

**Wednesday:**
- x_{4,Wed} = 1 (Caesar Salad - Italian starter) ✓
- x_{3,Wed} = 1 (Rice Biryani - Indian main) ✓
- x_{6,Wed} = 1 (Tiramisu - Italian dessert) ✓
- All other Wednesday variables = 0

### **Verification:**

✅ **Meal composition**: Each day has 1 starter + 1 main + 1 dessert  
✅ **Cuisine constraint**: Tuesday has no Italian items, Monday/Wednesday can have Italian  
✅ **Binary constraint**: Each variable is 0 or 1

---

## **Why This Is Powerful**

### **Alternative formulation (what the constraint does mathematically):**

**Let:**
- M_main = {1, 2, 3} (set of main course item IDs)
- M_Italian = {1, 4, 6} (set of Italian item IDs)
- D_Italian = {Mon, Wed} (days Italian is allowed)

**For Tuesday (not in D_Italian):**

∑_{i ∈ M_Italian} x_{i,Tue} = 0

This says: "The sum of all Italian item variables on Tuesday must equal zero," which means none can be selected.

**For meal composition on any day d:**

∑_{i ∈ M_main} x_{i,d} = 1

This says: "Exactly one main course must be selected each day."

---

## **How the Solver Works (Conceptually)**

The CP-SAT solver uses:

1. **Constraint Propagation**: If x_{1,Tue} must be 0 (Italian not allowed), it removes that option immediately

2. **Search**: Tries assigning values systematically:
   - "Let's try x_{4,Mon} = 1"
   - Propagates: "Since starters = 1, then x_{5,Mon} must be 0"
   - Continues until all variables are assigned or finds a contradiction

3. **Backtracking**: If it reaches an impossible state, it backtracks and tries different values

4. **Optimization**: Among all valid solutions, it picks the one that maximizes the objective function (e.g., variety = maximize total unique items selected)

---

## **Summary in Mathematical Terms**

**Constraint Satisfaction Problem (CSP):**

- **Variables**: X = {x_{i,d} | i ∈ Items, d ∈ Days}
- **Domain**: D(x_{i,d}) = {0, 1} for all variables
- **Constraints**: C = {meal composition constraints} ∪ {cuisine constraints}
- **Objective**: max(∑ x_{i,d}) subject to C

The solver finds an assignment X* where every constraint in C is satisfied, and the objective is maximized.

Does this mathematical perspective make it clearer?
