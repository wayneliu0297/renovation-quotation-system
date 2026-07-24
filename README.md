# Renovation Quotation System

A portfolio project demonstrating an object-oriented cost-estimation engine for
home-renovation projects, with a rental-yield calculator, automatic Word/PDF
proposal generation, a Streamlit web UI, and a PostgreSQL backend.

> **Demo / portfolio only.** All data is fake and not tied to any real company.

## Features

- **OOP cost engine** — an abstract `CostModel` base class with 8 renovation
  category subclasses (painting, plumbing, electrical, flooring, carpentry,
  bathroom, kitchen, demolition). Each category holds line items with a
  quantity and unit price.
- **Dynamic difficulty multiplier (1.0×–1.5×)** derived from building age,
  floor level, elevator availability, and structural condition.
- **Rental-yield calculator** — gross/net yield, monthly profit and payback
  period for a buy-to-rent scenario.
- **Document generation** — one-click `.docx` and `.pdf` proposals.
- **Streamlit UI** — fill in a survey form, get an instant quote.
- **PostgreSQL persistence** — save quotes and retrieve them later
  (via SQLAlchemy).

## Architecture

A pure object-oriented core (`models` + `calculators`) wrapped by three
interchangeable interfaces (CLI, web UI, database). The core has **zero**
dependency on Streamlit, PostgreSQL or the document libraries, so it is fully
unit-testable in isolation.

![Architecture diagram](docs/architecture.svg)

### Domain model

```mermaid
classDiagram
    class CostModel {
        <<abstract>>
        +list~LineItem~ items
        +base_subtotal() float
        +subtotal(difficulty) float
        +description()* str
    }
    class LineItem {
        +str name
        +float quantity
        +float unit_price
        +base_cost() float
    }
    class DifficultyMultiplier {
        +int floor
        +bool has_elevator
        +int building_age
        +Condition condition
        +value() float
    }
    class Quotation {
        +list~CostModel~ categories
        +trade_subtotal() float
        +supervision_fee() float
        +grand_total() float
    }
    class RentalYieldCalculator {
        +float monthly_rent
        +float renovation_cost
        +net_yield() float
        +payback_months() float
    }

    CostModel "1" o-- "*" LineItem : contains
    CostModel <|-- Demolition
    CostModel <|-- Plumbing
    CostModel <|-- Electrical
    CostModel <|-- Carpentry
    CostModel <|-- Flooring
    CostModel <|-- Painting
    CostModel <|-- Bathroom
    CostModel <|-- Kitchen
    Quotation "1" o-- "*" CostModel : aggregates
    Quotation ..> DifficultyMultiplier : applies
    RentalYieldCalculator ..> Quotation : reads grand_total
```

### Source layout

```
src/renovation_quote/
├── models/            # OOP domain layer
│   ├── line_item.py       # LineItem value object
│   ├── cost_model.py      # abstract CostModel base class
│   ├── categories.py      # 8 concrete category subclasses
│   └── difficulty.py      # DifficultyMultiplier
├── calculators/       # business logic
│   ├── quotation.py       # Quotation aggregate (totals, supervision fee)
│   └── rental_yield.py    # RentalYieldCalculator
├── db/                # persistence (SQLAlchemy + PostgreSQL)
│   ├── database.py        # engine / session factory
│   ├── schema.py          # ORM tables
│   └── repository.py      # save / load quotes
├── documents/         # output generation
│   ├── word_generator.py
│   └── pdf_generator.py
└── data/
    └── sample_data.py     # fake seed data
```

## Quick start

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Try the engine without any database or UI
python -m scripts.demo

# 4. (Optional) start PostgreSQL and seed it
cp .env.example .env          # edit DATABASE_URL if needed
python -m scripts.seed_db

# 5. Launch the web UI
streamlit run app/streamlit_app.py
```

## Difficulty multiplier

```
multiplier = 1.0
           + floor_factor       # no elevator & floor >= 4: (floor-3) * 0.05
           + age_factor         # building age > 30 years: +0.10
           + condition_factor   # normal 0 / aging +0.05 / poor +0.10 / severe +0.15
multiplier = clamp(multiplier, 1.0, 1.5)
```

## Tech stack

Python 3.11+ · SQLAlchemy · python-docx · reportlab · Streamlit · PostgreSQL
