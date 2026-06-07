# MediRun - Medical Delivery Optimization System

MediRun is a Flask-based delivery route optimization application designed for medical supply distribution across Paris and surrounding areas. The system intelligently assigns deliveries to drivers and vehicles based on route distance, delivery urgency, and vehicle capacity constraints.

## Project Overview

MediRun helps dispatch managers optimize daily delivery routes by:
- Categorizing routes as **short distance** (dense, central Paris ≤~80 km) or **long distance** (spread out suburbs)
- Assigning appropriate vehicle types (small van vs. large van) based on route characteristics
- Handling temperature-sensitive medical deliveries with refrigerated vehicle support
- Managing priority-based delivery constraints (critical, high, normal)
- Tracking driver assignments and route deadlines

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Virtual Environment** (recommended)

## Installation

### 1. Clone or Navigate to Project

```bash
cd c:\Users\suraj\OneDrive\MediRun
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r src/delivery_app/requirements.txt
```

## Running the Application

### 1. Initialize the Database (Optional)

If starting fresh, seed the database with test data:

```bash
python seed_db.py
```

### 2. Start the Flask Development Server

```bash
python run.py
```

The application will start on **http://127.0.0.1:5000**

### 3. Access the Application

1. Open your browser and navigate to `http://localhost:5000`
2. You will be redirected to the login page
3. Log in with seeded credentials
4. Access the **dashboard** to view and manage delivery routes

## Authentication & Authorization

MediRun implements role-based access control to ensure only authorized personnel can access the system.

### User Roles

- **CEO**: Full administrative access including dashboard, KPIs, all deliveries, and all drivers
- **Driver**: Limited access to view and update their own assigned deliveries

### Security Model

- **Pre-seeded Accounts**: Only accounts that have been created in the database can log in. Public self-registration is disabled.
- **Password Hashing**: All passwords are securely hashed using industry-standard algorithms
- **Session Management**: Authentication is maintained via secure sessions. Users must log in to access any route beyond the login page.
- **Role-based Routes**: Routes are protected with decorators that verify the user's role:
  - The `/dashboard` route is restricted to CEO-only access
  - The `/my-deliveries` route is restricted to authenticated drivers
  - Drivers cannot access other drivers' delivery lists or CEO features

### Adding New Users

New user accounts must be added to the database by an administrator. This can be done via:
- The `seed_db.py` script (for initial setup with test data)
- Direct database manipulation
- A future admin panel (if implemented)

## Project Structure

```
MediRun/
├── run.py                          # Entry point for Flask app
├── seed_db.py                      # Database initialization with test data
├── requirements.txt                # Root dependencies
├── tailwind.config.js              # Tailwind CSS configuration
├── src/
│   └── delivery_app/
│       ├── __init__.py
│       ├── app.py                  # Flask app factory and routes
│       ├── models.py               # Database models (User, Driver, Delivery, etc.)
│       ├── config.py               # Configuration settings
│       ├── requirements.txt        # App-specific dependencies
│       ├── static/
│       │   ├── style.css           # Compiled stylesheet (from Tailwind)
│       │   └── src.css             # Tailwind source
│       └── templates/
│           ├── base.html           # Base template (layout)
│           ├── login.html          # Login page
│           ├── signup.html         # Signup page
│           ├── dashboard.html      # Main manager dashboard
│           ├── driver_portal.html   # Driver portal page
│           ├── driver.html         # Individual driver details page
│           └── 403.html            # Authorization error page
├── services/
│   ├── assign_driver.py            # VRP service for driver assignment
│   └── test_dummy_data.py          # Test data fixtures
├── docs/
│   └── IDEAS.md                    # Project ideas and notes
└── instance/                       # Flask instance folder (database, local config)
```

## Key Features

### Database Models
- **Manager**: User accounts for dispatch managers
- **Driver**: Driver information (name, van type)
- **Delivery**: Individual delivery details (address, priority, temperature requirements)

### Core Functionality

#### Authentication
- User signup and login with password hashing
- Session management with login required decorator
- Secure account creation

#### Route Optimization
- **Short Distance Routes**: Dense, central Paris deliveries (11th, 13th, 20th, Ivry)
- **Long Distance Routes**: Geographically spread deliveries across suburbs
- **Smart Van Assignment**: Small vans for dense routes, large vans for spread routes

#### Delivery Management
- **Priority Levels**: Critical (before 9am), High, Normal
- **Temperature Control**: Refrigerated vans for temperature-sensitive medicines
- **Deadline Tracking**: Route completion windows (8:00–18:30)

### Test Data

The system includes **60 realistic test deliveries** across:
- **Hospitals & Clinics**: Hôpital Saint-Jean, multiple clinics (temperature-sensitive)
- **Pharmacies**: 50+ pharmacy locations across Paris and suburbs
- **Geographic Coverage**:
  - Ivry-sur-Seine warehouse (departure point)
  - Dense Paris clusters (11th, 13th, 15th, 20th arrondissements)
  - Suburban areas (Les Lilas, Fontenay, Montreuil)

**Run test data:**
```bash
python services/test_dummy_data.py
```

## Development

### Database
- SQLite database (default: `medirun.db`)
- Automatically created on first run
- Use Flask shell for database queries:
```bash
flask shell
```

### Environment Variables (Optional)

Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///medirun.db
```

### Debugging

The development server runs with **Debug Mode Enabled**:
- Auto-reload on file changes
- Interactive debugger on errors
- Debugger PIN: 112-196-548

## Typical Workflow

1. **Manager logs in** to the dashboard
2. **System loads** 60 test deliveries for the day
3. **Assignment algorithm** analyzes each route:
   - Calculates total distance and geographic spread
   - Determines if route is short distance (≤80 km, central) or long distance
   - Assigns appropriate vehicle type and driver
4. **Routes are optimized** and displayed on dashboard
5. **Manager reviews** assignments and can adjust as needed

## Route Classification Logic

| Factor | Short Distance | Long Distance |
|--------|---|---|
| **Total Route Distance** | ≤ ~70–80 km/day | > ~80 km/day |
| **Geographic Spread** | Dense, central Paris | Multiple suburbs |
| **Stop Density** | Geographically close | Dispersed, isolated clusters |
| **Vehicle Type** | Small van | Large van |
| **Example Zones** | Paris 11th, 13th, 20th | Les Lilas, Fontenay, Montreuil |

## Troubleshooting

### App won't start
- Ensure virtual environment is activated
- Check Python version: `python --version` (requires 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Database errors
- Delete `medirun.db` to reset database
- Restart the app to recreate tables

### Port already in use
- Change port in `run.py`: `app.run(port=5001)`
- Or kill existing process on port 5000

## Future Enhancements

- Real-time GPS tracking for drivers
- Google Maps API integration for actual distances
- Multi-day route planning
- Driver preferences and constraints
- Delivery confirmation and proof-of-delivery
- Performance analytics and reporting

## License

Private project for MediRun internal use.

## Support

For issues or questions, refer to the project documentation in `docs/IDEAS.md` or contact the development team.
