# MotivaTrack Production Deployment Guide

## 🚀 Deploying to Production

This guide covers deploying MotivaTrack to production environments.

---

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database schema deployed to production Supabase
- [ ] Strong `SECRET_KEY` generated
- [ ] `FLASK_ENV=production` set
- [ ] Dependencies installed
- [ ] HTTPS configured (required for secure cookies)
- [ ] Backup strategy in place

---

## Environment Configuration

### Production Environment Variables

Create a production `.env` file with these settings:

```env
# Flask Configuration
SECRET_KEY=<generate-strong-random-key-here>
FLASK_ENV=production

# Supabase Configuration
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_KEY=your-production-supabase-key

# Google Gemini API
GEMINI_API_KEY=your-production-gemini-key
```

### Generate Strong SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

---

## Deployment Options

### Option 1: Deploy to Heroku

1. **Install Heroku CLI**

2. **Create a Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set SUPABASE_URL=your-url
   heroku config:set SUPABASE_KEY=your-key
   heroku config:set GEMINI_API_KEY=your-key
   heroku config:set FLASK_ENV=production
   ```

4. **Create a `Procfile`**:
   ```
   web: gunicorn app:app
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 2: Deploy to Railway

1. **Install Railway CLI** or use the web dashboard

2. **Create new project**:
   ```bash
   railway init
   ```

3. **Add environment variables** in Railway dashboard

4. **Deploy**:
   ```bash
   railway up
   ```

### Option 3: Deploy to Render

1. **Create account** at [render.com](https://render.com)

2. **Create new Web Service**

3. **Connect your Git repository**

4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

5. **Add environment variables** in Render dashboard

### Option 4: Deploy to DigitalOcean App Platform

1. **Create account** at [digitalocean.com](https://digitalocean.com)

2. **Create new App**

3. **Connect repository**

4. **Configure**:
   - Run Command: `gunicorn --worker-tmp-dir /dev/shm app:app`

5. **Add environment variables**

### Option 5: Deploy to VPS (Ubuntu)

1. **SSH into your server**

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

3. **Clone repository**:
   ```bash
   git clone <your-repo>
   cd motivatrack
   ```

4. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create systemd service** (`/etc/systemd/system/motivatrack.service`):
   ```ini
   [Unit]
   Description=MotivaTrack Flask App
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/motivatrack
   Environment="PATH=/path/to/motivatrack/venv/bin"
   ExecStart=/path/to/motivatrack/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

6. **Configure Nginx** (`/etc/nginx/sites-available/motivatrack`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /path/to/motivatrack/static;
       }
   }
   ```

7. **Enable and start service**:
   ```bash
   sudo systemctl enable motivatrack
   sudo systemctl start motivatrack
   sudo systemctl enable nginx
   sudo systemctl restart nginx
   ```

8. **Set up SSL with Let's Encrypt**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

---

## Database Setup

### Supabase Production Configuration

1. **Create production Supabase project**

2. **Run schema.sql** in SQL Editor

3. **Enable Row Level Security (RLS)** for enhanced security:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE habit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminder_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_suggestions ENABLE ROW LEVEL SECURITY;

-- Note: Since we're using custom auth, you'll need to manage
-- RLS policies based on your session user_id
```

4. **Set up backups** in Supabase dashboard

5. **Monitor database usage** and scale as needed

---

## Security Best Practices

### Application Security

1. **Use HTTPS only**
   - Set `SESSION_COOKIE_SECURE = True` in production
   - Configure SSL certificates

2. **Secure cookies**
   - `SESSION_COOKIE_HTTPONLY = True` (already set)
   - `SESSION_COOKIE_SAMESITE = 'Lax'` (already set)

3. **Environment variables**
   - Never commit `.env` to version control
   - Use platform secret management

4. **Rate limiting**
   - Consider adding Flask-Limiter for API endpoints

5. **Input validation**
   - Already implemented in forms
   - Consider adding more validation for API endpoints

### Supabase Security

1. **Use RLS policies** to restrict data access

2. **Rotate API keys** regularly

3. **Monitor API usage** in Supabase dashboard

4. **Set up database backups**

### API Keys

1. **Protect Gemini API key**
   - Store securely in environment variables
   - Monitor usage and set quotas

2. **Implement rate limiting** for AI generation

---

## Performance Optimization

### Application Level

1. **Enable caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

2. **Use connection pooling** with Supabase

3. **Optimize database queries**
   - Add indexes where needed
   - Use select specific fields

4. **Enable compression**:
   ```python
   from flask_compress import Compress
   Compress(app)
   ```

### Server Level

1. **Use Gunicorn with multiple workers**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Configure Nginx caching** for static files

3. **Use CDN** for static assets (optional)

---

## Monitoring and Logging

### Application Logging

1. **Configure logging** in production:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **Use a logging service**:
   - Papertrail
   - Loggly
   - Sentry for error tracking

### Monitoring

1. **Set up uptime monitoring**:
   - UptimeRobot
   - Pingdom
   - StatusCake

2. **Monitor Supabase metrics**:
   - Database size
   - API usage
   - Query performance

3. **Monitor API usage**:
   - Gemini API quota
   - Request rates

---

## Backup Strategy

### Database Backups

1. **Enable Supabase automatic backups**

2. **Create manual backups** regularly:
   - Use Supabase backup feature
   - Export data periodically

3. **Test restore procedures**

### Application Backups

1. **Version control** with Git

2. **Document configuration**

3. **Store environment variable templates**

---

## Scaling Considerations

### Vertical Scaling

- Upgrade server resources as needed
- Increase Gunicorn workers

### Horizontal Scaling

- Use load balancer
- Deploy multiple app instances
- Ensure session management works across instances

### Database Scaling

- Supabase handles most scaling automatically
- Monitor and upgrade plan as needed
- Consider read replicas for heavy read workloads

---

## Troubleshooting Production Issues

### Common Issues

1. **502 Bad Gateway**
   - Check if Gunicorn is running
   - Verify Nginx configuration

2. **Database connection errors**
   - Check Supabase status
   - Verify credentials
   - Check firewall rules

3. **AI generation failures**
   - Verify Gemini API key
   - Check API quotas
   - Implement fallback messages

### Debug Mode

**Never enable debug mode in production!**

Instead:
- Use logging
- Monitor error tracking service
- Check application logs

---

## Maintenance

### Regular Tasks

- [ ] Monitor error logs weekly
- [ ] Check API usage monthly
- [ ] Review database performance
- [ ] Update dependencies quarterly
- [ ] Review and rotate secrets annually

### Updates

1. **Test updates in staging first**

2. **Create backup before updates**

3. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Run database migrations** if needed

5. **Restart application**:
   ```bash
   sudo systemctl restart motivatrack
   ```

---

## Cost Optimization

### Supabase

- Start with free tier
- Monitor usage
- Upgrade only when needed

### Gemini API

- Monitor API calls
- Implement caching for AI responses
- Set daily limits if needed

### Hosting

- Start small and scale
- Use spot instances for dev/staging
- Monitor actual usage

---

## Support and Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Supabase Documentation**: https://supabase.com/docs
- **Gemini API Documentation**: https://ai.google.dev/docs
- **Gunicorn Documentation**: https://docs.gunicorn.org/

---

**Good luck with your deployment! 🚀**
