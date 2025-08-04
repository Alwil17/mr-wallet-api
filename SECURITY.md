# Security Policy

## Supported Versions

We currently support the latest stable release of Mr Wallet API.  
Please update to the latest version before reporting vulnerabilities.

| Version | Supported          |
| ------- | ------------------ |
| latest  | ✅                 |

---

## Reporting a Vulnerability

If you discover a security vulnerability in Mr Wallet API:

1. **Do not open a public issue.**
2. Please email us at [willialfred24@gmail.com] with details of the vulnerability.
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact (especially on financial data)
   - Suggested fix (if you have one)
4. We will respond within 48 hours and work with you to resolve the issue quickly.

---

## Security Considerations for Financial Data

Mr Wallet API handles sensitive financial information. We take the following security measures:

### 🔐 Authentication & Authorization
- JWT-based authentication with secure token generation
- Password hashing using industry-standard algorithms
- Role-based access control for user data isolation

### 💾 Data Protection
- All financial data is encrypted at rest
- Secure database connections with SSL/TLS
- Input validation and sanitization to prevent injection attacks
- GDPR-compliant data handling and deletion capabilities

### 🛡️ API Security
- Rate limiting to prevent abuse
- CORS configuration for web client security
- Request validation using Pydantic models
- Secure file upload handling with type validation

### 🔍 Monitoring & Logging
- Security event logging (without sensitive data)
- Failed authentication attempt tracking
- Regular security audits and dependency updates

---

## Responsible Disclosure

We appreciate responsible disclosure and will:
- Acknowledge your contribution in our security advisories
- Provide updates on the fix progress
- Give credit to security researchers who help keep our users' financial data safe

---

## Security Best Practices for Contributors

When contributing to Mr Wallet API:
- Never commit API keys, passwords, or sensitive configuration
- Use environment variables for all sensitive settings
- Validate all user inputs, especially financial amounts
- Handle decimal precision carefully for monetary calculations
- Follow secure coding practices for financial applications

---

Thank you for helping to secure Mr Wallet and protect our users' financial data! 🔒💰