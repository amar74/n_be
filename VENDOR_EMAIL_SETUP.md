# Vendor Email Configuration Guide

## Overview
When a vendor is created through the Super Admin dashboard, an automated email is sent to the vendor with their login credentials and vendor information.

## Email Format
**Subject:** Vendor Creation Confirmation

**Content Includes:**
- Vendor ID
- Company Name
- User ID (Email)
- Password
- Login URL

## Required Environment Variables

Add these to your `.env` file in the `megapolis-api` directory:

```bash
# SMTP Configuration (Required for sending emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Nyftaa Team
SMTP_FROM_EMAIL=your-email@gmail.com

# Vendor Portal URL (Required)
VENDOR_LOGIN_URL=http://localhost:3000/vendor/login
# Update this to your production vendor login URL when deployed
```

## Gmail Configuration (Recommended)

If using Gmail:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Megapolis API"
   - Copy the generated 16-character password
   - Use this as your `SMTP_PASSWORD`

3. **Update your .env file:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Your app password
SMTP_FROM_EMAIL=your-email@gmail.com
```

## Alternative SMTP Providers

### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

### AWS SES
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

## Testing

To test the email functionality:

1. Create a vendor through the Super Admin dashboard
2. Check the backend logs for email sending status
3. If SMTP is not configured, the email content will be logged to console (development mode)

## Email Preview

The email sent to vendors looks like this:

```
Subject: Vendor Creation Confirmation

Dear [Vendor Name],

We're pleased to inform you that your vendor profile has been successfully created in our system.

Vendor ID: [Vendor UUID]
Company: [Company Name]
User ID (Email): [vendor@email.com]
Password: [Generated Password]
Login URL: [Your Vendor Portal URL]

You will shortly receive further details regarding documentation, onboarding, and payment processes.

Thank you for partnering with us.

Warm regards,
Nyftaa Team
```

## Troubleshooting

### Email not sending
1. Check your `.env` file has all required SMTP variables
2. Verify SMTP credentials are correct
3. Check backend logs: `tail -f logs/megapolis.log`
4. Ensure port 587 is not blocked by firewall

### Gmail "Less secure app" error
- Use an App Password instead of your regular password
- Enable 2FA first before generating App Password

### Development Mode
If SMTP is not configured, the system will log the email content to console instead of failing. This allows development without email setup.

## Production Checklist

Before deploying to production:

- [ ] Set up a proper email service (SendGrid, Mailgun, etc.)
- [ ] Update `VENDOR_LOGIN_URL` to production URL
- [ ] Update `SMTP_FROM_EMAIL` to your domain email
- [ ] Update `SMTP_FROM_NAME` to "Nyftaa Team" or your company name
- [ ] Test email delivery
- [ ] Set up email monitoring/logging
- [ ] Configure SPF/DKIM records for better deliverability

## Files Modified

- `app/services/email.py` - Email template and sending logic
- `app/routes/vendor.py` - Vendor creation endpoint with email trigger
- `app/environment.py` - Environment configuration (already had SMTP settings)

## Need Help?

If you encounter issues:
1. Check the logs: `tail -f logs/megapolis.log`
2. Verify environment variables are loaded: Add debug logging in `environment.py`
3. Test SMTP connection separately before integrating
