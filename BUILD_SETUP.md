# Build Setup Guide

## Prerequisites Completed ✅

1. ✅ PowerShell execution policy enabled
2. ✅ Corepack enabled for pnpm
3. ✅ Dependencies installed (without optional better-sqlite3)
4. ✅ Workspace configuration fixed
5. ✅ All critical syntax bugs fixed

## Current Status

### What's Working
- All TypeScript syntax errors fixed
- Package structure properly configured
- Workspace dependencies using `workspace:*` protocol
- @types/node added to all packages

### What's Pending
- **Visual Studio Build Tools installation** (in progress)
- better-sqlite3 compilation
- openid-client v6 API compatibility
- Full project build

## After Visual Studio Build Tools Installation

Run these commands in order:

```bash
# 1. Clean everything
pnpm store prune
rm -r node_modules
rm -r packages/*/node_modules
rm -r packages/*/dist

# 2. Reinstall with better-sqlite3
pnpm install

# 3. Fix openid-client version (if needed)
pnpm add openid-client@^5.6.5 --filter @oauth-kit/sdk

# 4. Build all packages
pnpm -r build

# 5. Verify build
pnpm -r build
```

## Known Issues & Solutions

### Issue 1: openid-client v6 API Changes
**Problem**: v6.8.1 has breaking API changes
**Solution**: Downgrade to v5.6.5 or update code to v6 API

### Issue 2: better-sqlite3 Build Failure
**Problem**: Requires C++ compiler
**Solution**: Install Visual Studio Build Tools with "Desktop development with C++"

### Issue 3: TypeScript Module Resolution
**Problem**: Was using "Bundler" resolution
**Solution**: Changed to "NodeNext" for proper Node.js support

## Testing After Build

### Test 1: Verify Compilation
```bash
# Should complete without errors
pnpm -r build
```

### Test 2: Check Exports
```bash
node -e "console.log(require('./packages/sdk-node/dist/index.js'))"
```

### Test 3: Run Example (requires OAuth credentials)
```bash
# Set environment variables
$env:GOOGLE_CLIENT_ID="your-client-id"
$env:GOOGLE_CLIENT_SECRET="your-client-secret"

# Build and run
pnpm --filter @oauth-kit/examples-node run build
pnpm --filter @oauth-kit/examples-node run start
```

## Next Development Steps (After Build Works)

1. **Add Tests**
   - Unit tests for token storage
   - Integration tests for OAuth flow
   - Mock provider for testing

2. **Improve Error Handling**
   - Add timeouts to callback server
   - Better error messages
   - Input validation

3. **Documentation**
   - API documentation
   - Usage examples
   - Provider setup guides

4. **Add More Providers**
   - Microsoft/Azure AD
   - Salesforce
   - Slack
   - GitHub Enterprise

5. **CI/CD**
   - Automated testing
   - Build verification
   - Manifest validation
