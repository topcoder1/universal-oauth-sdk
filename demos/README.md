# 🎯 Universal OAuth SDK - Demos

Interactive demonstrations showcasing the capabilities of the Universal OAuth SDK.

## 📚 Available Demos

### [Demo 1: Basic OAuth Usage](./01-basic-usage)
**Difficulty:** Beginner  
**Time:** 5 minutes

Learn the fundamentals of OAuth authentication with a simple Google login example.

**Features:**
- ✅ Basic OAuth flow
- ✅ Token storage
- ✅ API requests
- ✅ User information retrieval

```bash
cd 01-basic-usage
npm install
npm start
```

---

### [Demo 2: Device Code Flow](./02-device-flow)
**Difficulty:** Intermediate  
**Time:** 10 minutes

Implement OAuth for CLI applications and devices without browsers using GitHub's device flow.

**Features:**
- ✅ Device authorization
- ✅ User code display
- ✅ Automatic polling
- ✅ Perfect for CLI tools

```bash
cd 02-device-flow
npm install
npm start
```

---

### [Demo 3: Encrypted Token Storage](./03-encrypted-storage)
**Difficulty:** Intermediate  
**Time:** 10 minutes

Secure your OAuth tokens with AES-256-CBC encryption for enterprise-grade security.

**Features:**
- ✅ AES-256-CBC encryption
- ✅ Random IV per token
- ✅ Secure key management
- ✅ Compliance-ready

```bash
cd 03-encrypted-storage
npm install
npm start
```

---

### [Demo 4: Multi-Provider Support](./04-multi-provider)
**Difficulty:** Advanced  
**Time:** 15 minutes

Authenticate with multiple OAuth providers simultaneously and manage multiple accounts.

**Features:**
- ✅ Multiple providers
- ✅ Unified token storage
- ✅ Account aggregation
- ✅ Consistent API

```bash
cd 04-multi-provider
npm install
npm start
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or 20+
- npm or pnpm
- OAuth credentials from providers

### Installation

Each demo is self-contained. Navigate to a demo directory and run:

```bash
npm install
```

### Configuration

Most demos require OAuth credentials. Create a `.env` file in each demo directory:

```env
# Example for Google
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
```

See each demo's README for specific configuration instructions.

## 📖 Learning Path

**New to OAuth?** Follow this recommended order:

1. **Start with Demo 1** - Learn basic OAuth concepts
2. **Try Demo 4** - Understand multi-provider support
3. **Explore Demo 3** - Add security with encryption
4. **Advanced: Demo 2** - Master device flow for CLI apps

## 🎓 What You'll Learn

### OAuth Fundamentals
- Authorization code flow
- PKCE (Proof Key for Code Exchange)
- Token management
- Refresh tokens

### Advanced Concepts
- Device authorization flow
- Token encryption
- Multi-provider authentication
- Secure storage patterns

### Best Practices
- Environment variable management
- Error handling
- Token refresh strategies
- Security considerations

## 🛠️ Getting OAuth Credentials

### Google
1. Visit https://console.cloud.google.com/
2. Create project → Enable APIs → Create credentials
3. OAuth 2.0 Client ID
4. Add redirect: `http://localhost:8787/callback`

### GitHub
1. Visit https://github.com/settings/developers
2. New OAuth App
3. Add redirect: `http://localhost:8787/callback`

### Microsoft
1. Visit https://portal.azure.com/
2. App registrations → New registration
3. Add redirect: `http://localhost:8787/callback`
4. API permissions → Add User.Read

## 💡 Tips

### Running Multiple Demos
Each demo uses its own database file, so you can run them independently without conflicts.

### Environment Variables
Use a `.env` file or export variables:
```bash
export GOOGLE_CLIENT_ID="your-id"
export GOOGLE_CLIENT_SECRET="your-secret"
```

### Troubleshooting
- **Port 8787 in use?** Change `redirectUri` in the code
- **Browser doesn't open?** Check firewall settings
- **Token errors?** Delete the `.db` file and try again

## 📦 Demo Structure

Each demo includes:
- `index.js` - Main demo code
- `package.json` - Dependencies
- `README.md` - Detailed instructions
- `.env.example` - Configuration template (where applicable)

## 🔗 Resources

- **Main Documentation:** [../docs/API.md](../docs/API.md)
- **Usage Guide:** [../docs/USAGE_GUIDE.md](../docs/USAGE_GUIDE.md)
- **GitHub:** https://github.com/topcoder1/universal-oauth-sdk
- **npm:** https://www.npmjs.com/package/@topcoder1/oauth-sdk

## 🤝 Contributing

Found a bug or have an idea for a new demo? 

1. Open an issue on GitHub
2. Submit a pull request
3. Share your use case

## 📄 License

These demos are part of the Universal OAuth SDK and are licensed under Apache-2.0.

---

**Happy coding!** 🎉

If you build something cool with these demos, we'd love to hear about it!
