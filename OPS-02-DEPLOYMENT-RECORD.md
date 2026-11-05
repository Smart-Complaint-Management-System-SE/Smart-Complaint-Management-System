# OPS-02: HTTPS Test Deployment

## Deployment platform
Render

## Application URL
https://smart-complaint-management-system-yj4e.onrender.com

## Deployment configuration
- Runtime: Python 3
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app
- Database: PostgreSQL
- HTTPS: Enabled through Render

## Verification
- Render deployment completed successfully.
- Application home page loads over HTTPS.
- Test registration and login were attempted.

## Notes
The Render free web service may sleep after inactivity.
The free PostgreSQL database has an expiration limit.
