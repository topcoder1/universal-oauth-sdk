# Publishing Guide - Universal OAuth SDK v1.0.0

## ✅ Pre-Publish Checklist

All items below are **COMPLETE** and ready for publishing:

- [x] All tests passing (45/45)
- [x] All packages build successfully
- [x] TypeScript errors: 0
- [x] Lint errors: 0
- [x] Package versions updated to 1.0.0
- [x] Package metadata added (repository, keywords, author)
- [x] .npmignore files created
- [x] CHANGELOG.md created
- [x] Documentation complete
- [x] Examples working

## 🚀 Publishing Steps

### Step 1: Final Build & Test

```bash
# Clean install
pnpm install

# Build all packages
pnpm -r build

# Run all tests
pnpm test

# Validate manifests
pnpm lint:manifests
```

**Expected Output:**
- ✅ All packages build successfully
- ✅ 45/45 tests passing
- ✅ 11/11 manifests validated

### Step 2: Update Package Metadata

**IMPORTANT**: Before publishing, update these fields in all package.json files:

1. Replace `yourusername` with your GitHub username
2. Replace `Your Name <your.email@example.com>` with your info

**Files to update:**
- `packages/sdk-node/package.json`
- `packages/cli/package.json`
- `packages/provider-catalog/package.json`
- `packages/manifest-tools/package.json`

### Step 3: Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "chore: prepare for v1.0.0 release"

# Create GitHub repo (via GitHub website or gh CLI)
gh repo create universal-oauth-sdk --public --source=. --remote=origin

# Push
git push -u origin main
```

### Step 4: Login to npm

```bash
npm login
```

Enter your npm credentials when prompted.

Verify you're logged in:
```bash
npm whoami
```

### Step 5: Test Local Package

Before publishing, test that packages work locally:

```bash
# In sdk-node directory
cd packages/sdk-node
npm pack

# This creates oauth-kit-sdk-1.0.0.tgz
# Test installing it
cd /tmp
npm install /path/to/oauth-kit-sdk-1.0.0.tgz
```

### Step 6: Publish to npm

**Option A: Publish All Packages at Once**
```bash
# From root directory
pnpm publish -r --access public
```

**Option B: Publish Individually**
```bash
# Publish in dependency order

# 1. Provider catalog (no dependencies)
cd packages/provider-catalog
npm publish --access public

# 2. Manifest tools (no dependencies)
cd ../manifest-tools
npm publish --access public

# 3. SDK (no dependencies on other packages)
cd ../sdk-node
npm publish --access public

# 4. CLI (depends on SDK)
cd ../cli
npm publish --access public
```

### Step 7: Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial production release"

# Push tag
git push origin v1.0.0
```

### Step 8: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose tag: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### Step 9: Verify Publication

Check that packages are live on npm:

```bash
# View package info
npm view @oauth-kit/sdk
npm view @oauth-kit/cli
npm view @oauth-kit/provider-catalog
npm view @oauth-kit/manifest-tools

# Test installation
mkdir test-install
cd test-install
npm install @oauth-kit/sdk
npm install -g @oauth-kit/cli
```

## 📢 Step 10: Announce!

### Social Media

**Twitter/X:**
```
🎉 Just published Universal OAuth SDK v1.0.0!

✨ Features:
• OAuth 2.0 + Device Flow
• 11 providers (Google, GitHub, Microsoft, etc.)
• Token encryption
• TypeScript support
• 45 passing tests

npm install @oauth-kit/sdk

#OAuth #TypeScript #NodeJS
https://github.com/yourusername/universal-oauth-sdk
```

**Reddit:**
- r/node
- r/javascript
- r/typescript
- r/webdev

**Dev.to:**
Write a blog post about:
- Why you built it
- Key features
- How to use it
- Comparison with other libraries

**Hacker News:**
Submit to Show HN:
```
Show HN: Universal OAuth SDK – OAuth 2.0 library with device flow and encryption
```

### Communities
- Discord servers (Node.js, TypeScript)
- Slack communities
- LinkedIn
- Product Hunt

## 📊 Post-Publication Checklist

- [ ] Packages visible on npm
- [ ] Can install with `npm install @oauth-kit/sdk`
- [ ] GitHub release created
- [ ] README updated with npm install instructions
- [ ] Announced on Twitter/X
- [ ] Posted on Reddit
- [ ] Shared on LinkedIn
- [ ] Submitted to Hacker News
- [ ] Updated project status

## 🎯 Success Metrics

Track these after publishing:
- npm downloads
- GitHub stars
- Issues/PRs
- Community feedback
- Documentation views

## 🐛 If Something Goes Wrong

### Wrong Version Published
```bash
npm unpublish @oauth-kit/sdk@1.0.0
# Fix the issue
npm publish --access public
```

**Note**: You can only unpublish within 72 hours, and only if no one has downloaded it.

### Need to Deprecate
```bash
npm deprecate @oauth-kit/sdk@1.0.0 "Use version 1.0.1 instead"
```

### Forgot to Add Files
1. Update package.json `files` field
2. Bump version to 1.0.1
3. Publish again

## 📝 After Publishing

1. **Monitor Issues**: Respond to GitHub issues promptly
2. **Update Docs**: Fix any documentation errors
3. **Plan v1.1.0**: Start planning next features
4. **Engage Community**: Answer questions, accept PRs

## 🎊 Congratulations!

You've successfully published the Universal OAuth SDK to npm!

**Package URLs:**
- https://www.npmjs.com/package/@oauth-kit/sdk
- https://www.npmjs.com/package/@oauth-kit/cli
- https://www.npmjs.com/package/@oauth-kit/provider-catalog
- https://www.npmjs.com/package/@oauth-kit/manifest-tools

**Next Steps:**
- Build community
- Add more providers
- Create more examples
- Write tutorials

---

**Questions?** Check the [npm publish documentation](https://docs.npmjs.com/cli/v9/commands/npm-publish)
