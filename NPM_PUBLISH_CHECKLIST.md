# npm Publish Checklist

## Pre-Publish Checklist

### 1. Package Metadata ✅
- [ ] Update package.json files with repository URLs
- [ ] Add keywords for discoverability
- [ ] Set correct license
- [ ] Add author information
- [ ] Add homepage and bugs URLs

### 2. Documentation ✅
- [ ] README.md is complete and accurate
- [ ] API documentation is up to date
- [ ] Usage examples are tested
- [ ] CHANGELOG.md exists
- [ ] LICENSE file exists

### 3. Code Quality ✅
- [ ] All tests passing (45/45)
- [ ] No TypeScript errors
- [ ] Code is linted
- [ ] Code is formatted
- [ ] No security vulnerabilities

### 4. Build & Test ✅
- [ ] Clean install works: `pnpm install`
- [ ] All packages build: `pnpm -r build`
- [ ] All tests pass: `pnpm test`
- [ ] Manifests validate: `pnpm lint:manifests`

### 5. Files Configuration
- [ ] Create .npmignore files
- [ ] Verify `files` field in package.json
- [ ] Test local installation
- [ ] Check bundle size

### 6. Versioning
- [ ] Choose initial version (recommend 1.0.0)
- [ ] Update all package.json versions
- [ ] Create git tag
- [ ] Update CHANGELOG.md

## Step-by-Step Publishing Guide

### Step 1: Update Package Metadata

Edit each package.json:

```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/universal-oauth-sdk.git",
    "directory": "packages/sdk-node"
  },
  "homepage": "https://github.com/yourusername/universal-oauth-sdk#readme",
  "bugs": {
    "url": "https://github.com/yourusername/universal-oauth-sdk/issues"
  },
  "keywords": [
    "oauth",
    "oauth2",
    "oidc",
    "authentication",
    "google",
    "github",
    "microsoft"
  ],
  "author": "Your Name <your.email@example.com>"
}
```

### Step 2: Create .npmignore Files

**packages/sdk-node/.npmignore:**
```
src/
*.test.ts
__tests__/
*.tsbuildinfo
tsconfig.json
vitest.config.ts
.DS_Store
*.log
```

**packages/cli/.npmignore:**
```
src/
*.tsbuildinfo
tsconfig.json
.DS_Store
*.log
```

**packages/manifest-tools/.npmignore:**
```
src/
*.tsbuildinfo
tsconfig.json
.DS_Store
*.log
```

### Step 3: Test Local Installation

```bash
# In each package directory
pnpm pack

# This creates a .tgz file
# Test installing it locally
cd /tmp
npm install /path/to/oauth-kit-sdk-1.0.0.tgz
```

### Step 4: Verify Package Contents

```bash
# Check what will be published
npm pack --dry-run

# Or use
npx publint
```

### Step 5: Login to npm

```bash
npm login
# Enter your npm credentials
```

### Step 6: Publish Packages

```bash
# Publish all packages (from root)
pnpm publish -r --access public

# Or publish individually
cd packages/sdk-node
npm publish --access public

cd ../cli
npm publish --access public

cd ../manifest-tools
npm publish --access public

cd ../provider-catalog
npm publish --access public
```

### Step 7: Create Git Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Step 8: Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose tag v1.0.0
4. Add release notes
5. Publish release

## Post-Publish Checklist

- [ ] Verify packages on npm
- [ ] Test installation: `npm install @oauth-kit/sdk`
- [ ] Update documentation with npm install instructions
- [ ] Announce on social media
- [ ] Post on Reddit (r/node, r/javascript)
- [ ] Share on Twitter/X
- [ ] Post on Hacker News
- [ ] Update project status to "Published"

## Package URLs (After Publishing)

- **@oauth-kit/sdk**: https://www.npmjs.com/package/@oauth-kit/sdk
- **@oauth-kit/cli**: https://www.npmjs.com/package/@oauth-kit/cli
- **@oauth-kit/manifest-tools**: https://www.npmjs.com/package/@oauth-kit/manifest-tools
- **@oauth-kit/provider-catalog**: https://www.npmjs.com/package/@oauth-kit/provider-catalog

## Troubleshooting

### "You do not have permission to publish"
- Make sure you're logged in: `npm whoami`
- Check package name isn't taken
- Use scoped package: `@yourscope/package-name`

### "Package name too similar to existing package"
- Choose a different name
- Use a scope: `@oauth-kit/sdk`

### "Missing required field"
- Check package.json has all required fields
- Ensure `main`, `types`, and `files` are correct

## Version Management

### Semantic Versioning
- **Major (1.0.0)**: Breaking changes
- **Minor (0.1.0)**: New features, backward compatible
- **Patch (0.0.1)**: Bug fixes

### Updating Versions
```bash
# Update all packages
pnpm -r exec npm version patch
pnpm -r exec npm version minor
pnpm -r exec npm version major
```

## Recommended First Version

**1.0.0** - The SDK is production-ready with:
- ✅ 45 passing tests
- ✅ 11 provider integrations
- ✅ Complete documentation
- ✅ Token encryption
- ✅ CLI tool
- ✅ Example applications
- ✅ CI/CD configured

## Quick Publish Commands

```bash
# 1. Final checks
pnpm install
pnpm -r build
pnpm test
pnpm lint:manifests

# 2. Update versions
# Edit package.json files to version 1.0.0

# 3. Commit changes
git add .
git commit -m "chore: prepare for v1.0.0 release"
git push

# 4. Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Publish
npm login
pnpm publish -r --access public

# 6. Verify
npm view @oauth-kit/sdk
```

## Success Criteria

✅ All packages published successfully  
✅ Can install with `npm install @oauth-kit/sdk`  
✅ Documentation is accessible  
✅ Examples work with published packages  
✅ GitHub release created  
✅ Community announcements made  

---

**Ready to publish?** Follow the steps above carefully and you'll have your SDK on npm! 🚀
