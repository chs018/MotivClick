"""
Sample Data Seeder for MotivaTrack
Run this to populate your database with sample data for testing

Usage: python seed_data.py
"""

from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from supabase_client import get_supabase
import random

def seed_sample_data():
    """
    Seed the database with sample data for testing.
    Creates a demo user with goals, habits, and logs.
    """
    supabase = get_supabase()
    
    print("🌱 Seeding sample data...")
    
    # 1. Create demo user
    print("\n👤 Creating demo user...")
    demo_user_email = "demo@motivatrack.com"
    demo_password = "demo123"
    
    # Check if user exists
    existing_user = supabase.table('users')\
        .select('id')\
        .eq('email', demo_user_email)\
        .execute()
    
    if existing_user.data:
        user_id = existing_user.data[0]['id']
        print(f"   ℹ️  User already exists: {demo_user_email}")
    else:
        user_data = {
            'email': demo_user_email,
            'password_hash': generate_password_hash(demo_password),
            'display_name': 'Demo User'
        }
        user_response = supabase.table('users').insert(user_data).execute()
        user_id = user_response.data[0]['id']
        print(f"   ✅ Created user: {demo_user_email} / {demo_password}")
    
    # 2. Create sample goals
    print("\n🎯 Creating sample goals...")
    goals_data = [
        {
            'user_id': user_id,
            'title': 'Learn Python Programming',
            'description': 'Master Python to build web applications and automate tasks',
            'target_type': 'daily',
            'start_date': (date.today() - timedelta(days=30)).isoformat(),
            'target_date': (date.today() + timedelta(days=60)).isoformat(),
            'is_archived': False
        },
        {
            'user_id': user_id,
            'title': 'Get Physically Fit',
            'description': 'Improve health through regular exercise and healthy habits',
            'target_type': 'daily',
            'start_date': (date.today() - timedelta(days=20)).isoformat(),
            'is_archived': False
        },
        {
            'user_id': user_id,
            'title': 'Read More Books',
            'description': 'Develop reading habit and expand knowledge',
            'target_type': 'weekly',
            'start_date': (date.today() - timedelta(days=15)).isoformat(),
            'is_archived': False
        }
    ]
    
    goals = []
    for goal_data in goals_data:
        response = supabase.table('goals').insert(goal_data).execute()
        goals.append(response.data[0])
        print(f"   ✅ Created goal: {goal_data['title']}")
    
    # 3. Create habits for each goal
    print("\n✅ Creating sample habits...")
    habits_data = [
        # Python goal habits
        {'goal_id': goals[0]['id'], 'user_id': user_id, 'name': 'Study Python for 30 minutes', 'frequency': 'daily'},
        {'goal_id': goals[0]['id'], 'user_id': user_id, 'name': 'Complete one coding challenge', 'frequency': 'daily'},
        {'goal_id': goals[0]['id'], 'user_id': user_id, 'name': 'Build a mini project', 'frequency': 'weekly'},
        
        # Fitness goal habits
        {'goal_id': goals[1]['id'], 'user_id': user_id, 'name': 'Morning workout (30 min)', 'frequency': 'daily'},
        {'goal_id': goals[1]['id'], 'user_id': user_id, 'name': 'Walk 10,000 steps', 'frequency': 'daily'},
        {'goal_id': goals[1]['id'], 'user_id': user_id, 'name': 'Drink 8 glasses of water', 'frequency': 'daily'},
        
        # Reading goal habits
        {'goal_id': goals[2]['id'], 'user_id': user_id, 'name': 'Read for 20 minutes', 'frequency': 'daily'},
        {'goal_id': goals[2]['id'], 'user_id': user_id, 'name': 'Finish one book chapter', 'frequency': 'weekly'},
    ]
    
    habits = []
    for habit_data in habits_data:
        response = supabase.table('habits').insert(habit_data).execute()
        habits.append(response.data[0])
        print(f"   ✅ Created habit: {habit_data['name']}")
    
    # 4. Create habit logs for the past 30 days
    print("\n📊 Creating sample habit logs...")
    today = date.today()
    log_count = 0
    
    for habit in habits:
        # Create logs for the past 30 days with some variation
        for days_ago in range(30, -1, -1):
            log_date = (today - timedelta(days=days_ago)).isoformat()
            
            # Simulate realistic completion patterns (70-90% completion)
            if random.random() < 0.80:  # 80% completion rate
                status = 'completed'
            else:
                status = 'skipped'
            
            log_data = {
                'habit_id': habit['id'],
                'user_id': user_id,
                'date': log_date,
                'status': status
            }
            
            try:
                supabase.table('habit_logs').insert(log_data).execute()
                log_count += 1
            except:
                pass  # Skip if already exists
    
    print(f"   ✅ Created {log_count} habit logs")
    
    # 5. Create reminder settings
    print("\n⏰ Creating reminder settings...")
    reminder_data = {
        'user_id': user_id,
        'preferred_time': 'morning',
        'timezone': 'America/New_York'
    }
    
    try:
        supabase.table('reminder_settings').insert(reminder_data).execute()
        print("   ✅ Created reminder settings")
    except:
        print("   ℹ️  Reminder settings already exist")
    
    # 6. Create a sample AI suggestion
    print("\n🤖 Creating sample AI suggestion...")
    ai_suggestion_data = {
        'user_id': user_id,
        'date': today.isoformat(),
        'summary_of_progress': 'Completion rate: 80.0% over the last 7 days',
        'suggestions': str({
            'summary': 'Completion rate: 80.0% over the last 7 days',
            'suggestions': [
                'Focus on consistency with your morning workouts - small daily efforts compound over time',
                'Consider pairing your coding study with a specific time block to build stronger habit cues',
                'Celebrate your 80% completion rate - you\'re making excellent progress!'
            ],
            'motivation': 'You\'re doing great! Your dedication to showing up every day is building the foundation for long-term success. Keep up the momentum!'
        })
    }
    
    try:
        supabase.table('ai_suggestions').insert(ai_suggestion_data).execute()
        print("   ✅ Created AI suggestion")
    except:
        print("   ℹ️  AI suggestion already exists for today")
    
    # Summary
    print("\n" + "="*50)
    print("🎉 Sample data seeding complete!")
    print("="*50)
    print(f"\n📧 Demo Account:")
    print(f"   Email: {demo_user_email}")
    print(f"   Password: {demo_password}")
    print(f"\n📊 Created:")
    print(f"   • {len(goals)} goals")
    print(f"   • {len(habits)} habits")
    print(f"   • {log_count} habit logs (30 days)")
    print(f"   • 1 reminder setting")
    print(f"   • 1 AI suggestion")
    print(f"\n🚀 You can now login and explore the app with sample data!")
    print("="*50 + "\n")


if __name__ == '__main__':
    try:
        seed_sample_data()
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        import traceback
        print(traceback.format_exc())
