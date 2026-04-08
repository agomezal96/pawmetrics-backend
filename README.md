The core engine behind Pawmetrics, providing real-time analytics for professional pet sitters. Built with a focus on data accuracy and performance-based metrics.

# 🛠 Tech Stack
- Framework: Django 6.0 + Django REST Framework (DRF)
- Database: PostgreSQL (Neon.tech)
- Deployment: RailwayKey 
- Libraries: python-dateutil (for calendar logic), corsheaders.

# ✨ Key Features
- Analytical Endpoints: Custom logic for calculating earnings (past vs. pending) and sitter performance.
- Star Sitter Engine: Automated tracking of "Star Sitter" requirements over rolling 6-month windows.
- Bento-Ready Data: Highly structured JSON responses designed specifically for a modular grid UI.
  
# 📡 API Endpoints
- /api/metrics/ --> GET --> Dashboard stats: earnings, pet species count, and recent reviews.
- /api/metrics/sitter-score/ --> GET --> Star Sitter progress (unique owners, repeat clients, rating).
- /api/bookings/ --> CRUD --> Management of pet sitting appointments.
- /api/pets/ --> CRUD --> Pet profiles including species and breed.
