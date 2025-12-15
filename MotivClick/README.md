# MotivaTrack – Goal Tracker with AI Motivation

A complete, production-ready personal goals and habit tracking web application with AI-powered daily motivation.

## Features

- 🎯 **Goal Management** – Create and track larger objectives
- ✅ **Habit Tracking** – Small, repeatable actions linked to goals
- 📊 **Daily Check-ins** – Mark completed habits each day
- 🔥 **Streaks & Stats** – View streaks, completion rates, and progress charts
- 🤖 **AI Motivation** – Get personalized daily tips powered by Google Gemini
- ⏰ **Reminder Settings** – Set preferred notification times
- 📱 **Fully Responsive** – Mobile-first design with Tailwind CSS

## Tech Stack

- **Backend**: Python 3 + Flask
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript
- **Authentication**: Custom auth with Supabase storage
- **AI**: Google Gemini API for motivational content

## Project Structure

```
motivatrack/
├── app.py                      # Main Flask application
├── config.py                   # Configuration and environment variables
├── supabase_client.py          # Supabase client initialization
├── requirements.txt            # Python dependencies
├── schema.sql                  # Database schema
├── .env.example               # Example environment variables
├── .env                       # Your actual environment variables (create this)
├── services/
│   ├── goal_service.py        # Goal management logic
│   ├── habit_service.py       # Habit tracking logic
│   ├── stats_service.py       # Statistics and analytics
│   └── ai_service.py          # Google Gemini AI integration
├── templates/
│   ├── base.html              # Base template with Tailwind
│   ├── auth_login.html        # Login page
│   ├── auth_register.html     # Registration page
│   ├── dashboard.html         # Main dashboard
│   ├── goals.html             # Goals management
│   ├── stats.html             # Statistics and charts
│   └── settings.html          # User settings
└── static/
    ├── css/
    │   └── styles.css         # Custom CSS tweaks
    └── js/
        ├── main.js            # Main JavaScript logic
        ├── reminders.js       # Reminder functionality
        └── ai_motivation.js   # AI motivation features
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- A Supabase account and project
- A Google Cloud account with Gemini API access

### 2. Clone or Create Project Directory

```bash
mkdir motivatrack
cd motivatrack
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Navigate to Project Settings → API
3. Copy your Project URL and anon/public key
4. Go to SQL Editor in Supabase dashboard
5. Run the SQL schema from `schema.sql` to create all tables

### 5. Set Up Google Gemini API

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key for Gemini
3. Copy the API key

### 6. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development

SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

GEMINI_API_KEY=your-gemini-api-key
```

### 7. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

### 8. Create Your First Account

1. Navigate to `http://localhost:5000`
2. Click "Register" and create an account
3. Log in and start tracking your goals!

## Usage Guide

### Creating Goals

1. Go to the **Goals** page
2. Click **"Create New Goal"**
3. Enter title, description, target type, and dates
4. Save the goal

### Adding Habits

1. From the Goals page, click **"Manage Habits"** on a goal
2. Add habits with names and frequency
3. Habits will appear on your dashboard

### Daily Check-ins

1. Visit the **Dashboard** each day
2. Check off completed habits
3. View your current streaks

### AI Motivation

1. On the Dashboard, click **"Get Today's AI Motivation"**
2. The system analyzes your progress
3. Receive personalized tips and encouragement from Gemini AI

### Viewing Stats

1. Go to the **Stats** page
2. View completion rates, streaks, and trends
3. Track your progress over time

### Setting Reminders

1. Go to **Settings**
2. Choose your preferred reminder time
3. Set your timezone
4. Save preferences

## API Endpoints

- `GET /` – Home (redirects to dashboard or login)
- `GET/POST /register` – User registration
- `GET/POST /login` – User login
- `GET /logout` – User logout
- `GET /dashboard` – Main dashboard
- `GET /goals` – List all goals
- `GET/POST /goals/new` – Create new goal
- `GET/POST /goals/<id>/edit` – Edit goal
- `GET/POST /goals/<id>/habits` – Manage goal habits
- `POST /habits/log` – Log habit completion
- `GET /stats` – View statistics
- `GET/POST /settings` – User settings
- `POST /ai/motivation/today` – Generate AI motivation

## Database Schema

### Tables

- **users** – User accounts and profiles
- **goals** – User goals and objectives
- **habits** – Repeatable actions linked to goals
- **habit_logs** – Daily habit completion records
- **reminder_settings** – User notification preferences
- **ai_suggestions** – AI-generated motivational content

See `schema.sql` for complete schema details.

## Production Deployment

### Environment Variables

Set `FLASK_ENV=production` and use a strong `SECRET_KEY`.

### WSGI Server

Use Gunicorn to run the app:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Security Considerations

- Always use HTTPS in production
- Enable Row Level Security (RLS) in Supabase
- Rotate API keys regularly
- Use strong password requirements
- Implement rate limiting for API endpoints

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues or questions, please open an issue on the project repository.

---

Built with ❤️ using Flask, Supabase, and Google Gemini
