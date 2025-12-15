# MotivaTrack Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### Step 2: Set Up Supabase

1. **Create a Supabase account** at [supabase.com](https://supabase.com)
2. **Create a new project**
3. **Copy your credentials**:
   - Go to Settings → API
   - Copy the Project URL
   - Copy the `anon/public` key
4. **Run the database schema**:
   - Go to SQL Editor in Supabase
   - Copy and paste the entire contents of `schema.sql`
   - Click "Run" to create all tables

### Step 3: Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   SECRET_KEY=your-random-secret-key-generate-one
   FLASK_ENV=development
   
   SUPABASE_URL=https://yourproject.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   
   GEMINI_API_KEY=your-gemini-api-key
   ```

### Step 5: Run the Application

```powershell
python app.py
```

The app will start at **http://localhost:5000**

### Step 6: Create Your Account

1. Open http://localhost:5000 in your browser
2. Click "Register"
3. Create your account
4. Start tracking your goals!

---

## 📝 Quick Usage Tips

### Creating Your First Goal

1. Click **"Goals"** in the navigation
2. Click **"Create New Goal"**
3. Fill in:
   - Title (e.g., "Get Fit")
   - Description (optional)
   - Target type (daily/weekly/once)
   - Start and target dates
4. Click **"Create Goal"**

### Adding Habits

1. From the Goals page, click **"Manage Habits"** on a goal
2. Enter a habit name (e.g., "30 min workout")
3. Select frequency
4. Click **"Add Habit"**

### Daily Check-ins

1. Go to **Dashboard**
2. Check off completed habits
3. Watch your streaks grow! 🔥

### AI Motivation

1. On the Dashboard, click **"Generate Today's Motivation"**
2. Get personalized tips from Google Gemini AI
3. Come back daily for fresh motivation!

---

## 🛠️ Troubleshooting

### "SUPABASE_URL environment variable is required"

- Make sure you created the `.env` file
- Check that all values are filled in
- Restart the app after editing `.env`

### "Failed to initialize Supabase client"

- Verify your Supabase URL and key are correct
- Make sure your Supabase project is active
- Check your internet connection

### "Error calling Gemini API"

- Verify your Gemini API key is correct
- Check if you have API quota remaining
- Try regenerating your API key

### Database errors

- Make sure you ran the `schema.sql` in Supabase SQL Editor
- Check that all tables were created successfully
- Try running the schema again if tables are missing

---

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use strong, unique passwords
- In production, set `FLASK_ENV=production`
- Generate a strong `SECRET_KEY` for production

---

## 🎯 Next Steps

1. ✅ Set up your first goal
2. ✅ Add daily habits
3. ✅ Complete your first check-in
4. ✅ Get AI motivation
5. ✅ Track your progress in Stats

---

## 💡 Pro Tips

- **Consistent Habits**: Start with 2-3 habits you can realistically do daily
- **AI Motivation**: Regenerate throughout the day for fresh perspective
- **Streaks**: Don't break the chain! Check in daily
- **Review Stats**: Check your stats weekly to see patterns
- **Adjust Goals**: Update goals as you progress and learn

---

## 📚 Need Help?

- Check the full `README.md` for detailed documentation
- Review the code comments in service files
- Check Supabase and Flask documentation
- Open an issue if you find bugs

---

**Happy tracking! 🎉**
