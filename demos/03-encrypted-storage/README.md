# Demo 3: Encrypted Token Storage

Demonstration of secure token storage using AES-256-CBC encryption.

## Why Encrypt Tokens?

OAuth tokens are sensitive credentials that grant access to user data. Encrypting them at rest provides:
- ✅ Protection against database theft
- ✅ Compliance with security standards
- ✅ Defense in depth security
- ✅ Safe storage on shared systems

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Generate encryption key:**
   ```bash
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

3. **Configure OAuth credentials:**
   
   Create `.env` file:
   ```env
   ENCRYPTION_KEY=your-64-character-hex-key
   MICROSOFT_CLIENT_ID=your-client-id
   MICROSOFT_CLIENT_SECRET=your-secret
   ```

4. **Get Microsoft OAuth credentials:**
   - Go to https://portal.azure.com/
   - Register new application
   - Add redirect URI: `http://localhost:8787/callback`
   - Add API permissions: User.Read

## Run

```bash
npm start
```

## Security Features

### AES-256-CBC Encryption
- Industry-standard encryption algorithm
- 256-bit key length
- CBC mode for additional security

### Random IV
- Unique initialization vector for each token
- Prevents pattern analysis
- Stored alongside encrypted data

### Secure Key Management
- Key stored in environment variable
- Never committed to version control
- Rotatable for enhanced security

## Expected Output

```
🔐 Universal OAuth SDK - Encrypted Storage Demo

✅ Encrypted store initialized

✅ Client initialized

🌐 Starting OAuth flow...
👉 A browser window will open for authentication

✅ Authentication successful!

🔒 Token Security:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Tokens encrypted with AES-256-CBC
✅ Random IV for each token
✅ Secure storage in SQLite database
✅ Protected against unauthorized access
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 Fetching user information...

👤 Microsoft User Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: John Doe
Email: john@company.com
Job Title: Software Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Demo complete!

💡 Tip: Your tokens are safely encrypted in encrypted-tokens.db
```

## Best Practices

1. **Never hardcode encryption keys**
2. **Use environment variables or key management services**
3. **Rotate keys periodically**
4. **Restrict database file permissions**
5. **Use different keys for dev/staging/production**

## Use Cases

- **Enterprise Applications:** Meet security compliance
- **Multi-tenant Systems:** Isolate tenant data
- **Shared Environments:** Protect against unauthorized access
- **Regulated Industries:** HIPAA, PCI-DSS, GDPR compliance
