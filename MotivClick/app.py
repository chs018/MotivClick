"""
MotivaTrack - Main Flask Application
Goal Tracker with AI Motivation
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
import traceback

from config import Config
from supabase_client import init_supabase, get_supabase
from services import goal_service, habit_service, stats_service, ai_service

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Supabase connection
try:
    init_supabase()
except Exception as e:
    print(f"Warning: Supabase initialization failed: {e}")
    print("Make sure environment variables are set correctly.")


# ============================================================================
# Authentication Helpers
# ============================================================================

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user from session."""
    if 'user_id' not in session:
        return None
    
    try:
        supabase = get_supabase()
        response = supabase.table('users')\
            .select('id, email, display_name')\
            .eq('id', session['user_id'])\
            .execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None


# ============================================================================
# Routes - Authentication
# ============================================================================

@app.route('/')
def index():
    """Home route - redirect based on auth status."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth_register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth_register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth_register.html')
        
        try:
            supabase = get_supabase()
            
            # Check if user already exists
            existing = supabase.table('users')\
                .select('id')\
                .eq('email', email)\
                .execute()
            
            if existing.data:
                flash('An account with this email already exists.', 'error')
                return render_template('auth_register.html')
            
            # Create new user
            password_hash = generate_password_hash(password)
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'display_name': display_name or email.split('@')[0]
            }
            
            response = supabase.table('users').insert(user_data).execute()
            
            if response.data:
                user = response.data[0]
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session.permanent = True
                
                flash('Registration successful! Welcome to MotivaTrack.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            print(f"Registration error: {e}")
            print(traceback.format_exc())
            flash('An error occurred during registration.', 'error')
    
    return render_template('auth_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth_login.html')
        
        try:
            supabase = get_supabase()
            
            # Find user by email
            response = supabase.table('users')\
                .select('*')\
                .eq('email', email)\
                .execute()
            
            if not response.data:
                flash('Invalid email or password.', 'error')
                return render_template('auth_login.html')
            
            user = response.data[0]
            
            # Verify password
            if not check_password_hash(user['password_hash'], password):
                flash('Invalid email or password.', 'error')
                return render_template('auth_login.html')
            
            # Set session
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session.permanent = True
            
            flash(f'Welcome back, {user.get("display_name", "User")}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Login error: {e}")
            print(traceback.format_exc())
            flash('An error occurred during login.', 'error')
    
    return render_template('auth_login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# Routes - Dashboard
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        # Get overview stats
        stats = stats_service.get_user_overview_stats(user_id)
        
        # Get habits with streaks and today's status
        habits = habit_service.get_habits_with_streaks(user_id)
        
        # Get today's AI suggestion if available
        today = date.today().isoformat()
        supabase = get_supabase()
        ai_response = supabase.table('ai_suggestions')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('date', today)\
            .execute()
        
        ai_suggestion = ai_response.data[0] if ai_response.data else None
        
        # Get recent activity (last 7 days)
        recent_activity = stats_service.get_recent_activity(user_id, days=7)
        
        return render_template(
            'dashboard.html',
            user=user,
            stats=stats,
            habits=habits,
            ai_suggestion=ai_suggestion,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        print(traceback.format_exc())
        flash('Error loading dashboard.', 'error')
        return render_template('dashboard.html', user=user, stats={}, habits=[])


# ============================================================================
# Routes - Goals
# ============================================================================

@app.route('/goals')
@login_required
def goals():
    """List all goals."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        goals_list = goal_service.get_goals_with_habits(user_id)
        return render_template('goals.html', user=user, goals=goals_list)
    except Exception as e:
        print(f"Goals error: {e}")
        print(traceback.format_exc())
        flash('Error loading goals.', 'error')
        return render_template('goals.html', user=user, goals=[])


@app.route('/goals/new', methods=['GET', 'POST'])
@login_required
def new_goal():
    """Create a new goal."""
    user_id = session['user_id']
    user = get_current_user()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        target_type = request.form.get('target_type', 'daily')
        start_date = request.form.get('start_date', date.today().isoformat())
        target_date = request.form.get('target_date', '').strip()
        
        if not title:
            flash('Goal title is required.', 'error')
            return render_template('goal_form.html', user=user, goal=None)
        
        try:
            goal_service.create_goal(
                user_id=user_id,
                title=title,
                description=description,
                target_type=target_type,
                start_date=start_date,
                target_date=target_date if target_date else None
            )
            
            flash('Goal created successfully!', 'success')
            return redirect(url_for('goals'))
            
        except Exception as e:
            print(f"Create goal error: {e}")
            print(traceback.format_exc())
            flash('Error creating goal.', 'error')
    
    return render_template('goal_form.html', user=user, goal=None)


@app.route('/goals/<goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    """Edit a goal."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        goal = goal_service.get_goal_by_id(goal_id, user_id)
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('goals'))
        
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            target_type = request.form.get('target_type', 'daily')
            start_date = request.form.get('start_date')
            target_date = request.form.get('target_date', '').strip()
            
            if not title:
                flash('Goal title is required.', 'error')
                return render_template('goal_form.html', user=user, goal=goal)
            
            goal_service.update_goal(
                goal_id=goal_id,
                user_id=user_id,
                title=title,
                description=description,
                target_type=target_type,
                start_date=start_date,
                target_date=target_date if target_date else None
            )
            
            flash('Goal updated successfully!', 'success')
            return redirect(url_for('goals'))
        
        return render_template('goal_form.html', user=user, goal=goal)
        
    except Exception as e:
        print(f"Edit goal error: {e}")
        print(traceback.format_exc())
        flash('Error editing goal.', 'error')
        return redirect(url_for('goals'))


@app.route('/goals/<goal_id>/archive', methods=['POST'])
@login_required
def archive_goal(goal_id):
    """Archive a goal."""
    user_id = session['user_id']
    
    try:
        goal_service.archive_goal(goal_id, user_id)
        flash('Goal archived.', 'success')
    except Exception as e:
        print(f"Archive goal error: {e}")
        flash('Error archiving goal.', 'error')
    
    return redirect(url_for('goals'))


@app.route('/goals/<goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """Delete a goal."""
    user_id = session['user_id']
    
    try:
        goal_service.delete_goal(goal_id, user_id)
        flash('Goal deleted.', 'success')
    except Exception as e:
        print(f"Delete goal error: {e}")
        flash('Error deleting goal.', 'error')
    
    return redirect(url_for('goals'))


# ============================================================================
# Routes - Habits
# ============================================================================

@app.route('/goals/<goal_id>/habits', methods=['GET', 'POST'])
@login_required
def manage_habits(goal_id):
    """Manage habits for a goal."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        goal = goal_service.get_goal_by_id(goal_id, user_id)
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('goals'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            frequency = request.form.get('frequency', 'daily')
            
            if not name:
                flash('Habit name is required.', 'error')
            else:
                habit_service.create_habit(
                    user_id=user_id,
                    goal_id=goal_id,
                    name=name,
                    frequency=frequency
                )
                flash('Habit added!', 'success')
            
            return redirect(url_for('manage_habits', goal_id=goal_id))
        
        habits_list = habit_service.get_habits_for_goal(goal_id, user_id)
        
        return render_template(
            'habits.html',
            user=user,
            goal=goal,
            habits=habits_list
        )
        
    except Exception as e:
        print(f"Manage habits error: {e}")
        print(traceback.format_exc())
        flash('Error managing habits.', 'error')
        return redirect(url_for('goals'))


@app.route('/habits/<habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    """Delete a habit."""
    user_id = session['user_id']
    
    try:
        habit = habit_service.get_habit_by_id(habit_id, user_id)
        goal_id = habit['goal_id'] if habit else None
        
        habit_service.delete_habit(habit_id, user_id)
        flash('Habit deleted.', 'success')
        
        if goal_id:
            return redirect(url_for('manage_habits', goal_id=goal_id))
    except Exception as e:
        print(f"Delete habit error: {e}")
        flash('Error deleting habit.', 'error')
    
    return redirect(url_for('goals'))


@app.route('/habits/log', methods=['POST'])
@login_required
def log_habit():
    """Log habit completion (AJAX endpoint)."""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        habit_id = data.get('habit_id')
        log_date = data.get('date', date.today().isoformat())
        status = data.get('status', 'completed')
        
        if not habit_id:
            return jsonify({'error': 'Habit ID required'}), 400
        
        # Log the habit
        habit_service.log_habit_completion(habit_id, user_id, log_date, status)
        
        # Calculate new streak
        streak = habit_service.calculate_habit_streak(habit_id, user_id)
        
        return jsonify({
            'success': True,
            'streak': streak,
            'status': status
        })
        
    except Exception as e:
        print(f"Log habit error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Routes - Statistics
# ============================================================================

@app.route('/stats')
@login_required
def stats():
    """Statistics page."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        # Get overview stats
        overview = stats_service.get_user_overview_stats(user_id)
        
        # Get weekly stats
        weekly_stats = stats_service.get_weekly_completion_stats(user_id, weeks=4)
        
        # Get monthly stats
        monthly_stats = stats_service.get_monthly_completion_stats(user_id, months=3)
        
        # Get all habits with statistics
        habits_stats = stats_service.get_all_habits_statistics(user_id)
        
        return render_template(
            'stats.html',
            user=user,
            overview=overview,
            weekly_stats=weekly_stats,
            monthly_stats=monthly_stats,
            habits_stats=habits_stats
        )
        
    except Exception as e:
        print(f"Stats error: {e}")
        print(traceback.format_exc())
        flash('Error loading statistics.', 'error')
        return render_template('stats.html', user=user)


# ============================================================================
# Routes - Settings
# ============================================================================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        supabase = get_supabase()
        
        if request.method == 'POST':
            preferred_time = request.form.get('preferred_time', 'morning')
            timezone = request.form.get('timezone', 'UTC')
            
            # Upsert reminder settings
            settings_data = {
                'user_id': user_id,
                'preferred_time': preferred_time,
                'timezone': timezone
            }
            
            supabase.table('reminder_settings')\
                .upsert(settings_data, on_conflict='user_id')\
                .execute()
            
            flash('Settings saved!', 'success')
            return redirect(url_for('settings'))
        
        # Get current settings
        response = supabase.table('reminder_settings')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        current_settings = response.data[0] if response.data else {
            'preferred_time': 'morning',
            'timezone': 'UTC'
        }
        
        return render_template(
            'settings.html',
            user=user,
            settings=current_settings
        )
        
    except Exception as e:
        print(f"Settings error: {e}")
        print(traceback.format_exc())
        flash('Error loading settings.', 'error')
        return render_template('settings.html', user=user)


# ============================================================================
# Routes - AI Motivation
# ============================================================================

@app.route('/ai/motivation/today', methods=['POST'])
@login_required
def ai_motivation_today():
    """Generate today's AI motivation (AJAX endpoint)."""
    user_id = session['user_id']
    user = get_current_user()
    
    try:
        # Get user's active goals
        goals = goal_service.get_user_goals(user_id, include_archived=False)
        
        # Get recent habit logs (last 7 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        recent_logs = habit_service.get_user_logs_by_date_range(
            user_id,
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        # Generate motivation
        user_name = user.get('display_name', 'there')
        motivation_data = ai_service.generate_daily_motivation(
            user_name=user_name,
            goals=goals,
            recent_logs=recent_logs
        )
        
        # Save to database
        today = date.today().isoformat()
        supabase = get_supabase()
        
        ai_data = {
            'user_id': user_id,
            'date': today,
            'summary_of_progress': motivation_data['summary'],
            'suggestions': str(motivation_data)  # Store as JSON string
        }
        
        supabase.table('ai_suggestions')\
            .upsert(ai_data, on_conflict='user_id,date')\
            .execute()
        
        return jsonify({
            'success': True,
            'data': motivation_data
        })
        
    except Exception as e:
        print(f"AI motivation error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """404 error handler."""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler."""
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500


# ============================================================================
# Template Filters
# ============================================================================

@app.template_filter('format_date')
def format_date(value):
    """Format date for display."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        except:
            return value
    
    if isinstance(value, date):
        return value.strftime('%b %d, %Y')
    
    return value


@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime for display."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%b %d, %Y at %I:%M %p')
    
    return value


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
