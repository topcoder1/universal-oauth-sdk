# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-28

### 🎉 Initial Release

The Universal OAuth SDK is production-ready!

### Added

#### Core SDK (`@oauth-kit/sdk`)
- OAuth 2.0 Authorization Code Flow with PKCE
- Device Code Flow (RFC 8628) for CLI/TV/IoT devices
- Automatic token refresh
- Three storage options:
  - `MemoryStore` - In-memory storage
  - `SQLiteStore` - Persistent SQLite storage
  - `EncryptedSQLiteStore` - AES-256-CBC encrypted storage
- Type-safe TypeScript API
- Comprehensive error handling with timeouts
- Input validation for all parameters
- 45 unit and integration tests (100% passing)

#### CLI Tool (`@oauth-kit/cli`)
- `oauth connect <provider>` - Authorize with OAuth provider
- `oauth token <provider>` - View token (redacted)
- `oauth list` - List all stored tokens
- `oauth info <key>` - Show detailed token information
- `oauth refresh <key>` - Manually refresh tokens
- `oauth revoke <key>` - Delete tokens

#### Provider Catalog (`@oauth-kit/provider-catalog`)
- 11 pre-configured OAuth providers:
  - Google
  - GitHub
  - Microsoft (Azure AD)
  - Salesforce
  - Slack
  - LinkedIn
  - Dropbox
  - Shopify
  - Twitter/X
  - Discord
  - Spotify
- JSON Schema validation
- MIT licensed for easy contribution

#### Manifest Tools (`@oauth-kit/manifest-tools`)
- Provider manifest validation
- JSON Schema linter
- Ajv-based validation with format support

#### Examples
- Express.js web application with multi-provider support
- Complete setup guides
- Environment configuration templates

#### Documentation
- Complete API documentation
- Comprehensive usage guide
- Security best practices
- Troubleshooting guides
- npm publish checklist

#### Infrastructure
- GitHub Actions CI/CD
  - Multi-OS testing (Ubuntu, Windows, macOS)
  - Node.js version matrix (18.x, 20.x)
  - Automated testing, linting, and validation
- ESLint configuration
- Prettier formatting
- TypeScript strict mode

### Security
- PKCE (Proof Key for Code Exchange) implementation
- State parameter validation for CSRF protection
- AES-256-CBC token encryption at rest
- Secure error messages (no sensitive data exposure)
- Input validation and sanitization
- Timeout protection (5-minute default)

### Performance
- Fast builds (~1.5s per package)
- Quick tests (~970ms for 45 tests)
- Efficient token storage
- Minimal dependencies

### Developer Experience
- Full TypeScript support with type definitions
- Comprehensive error messages with context
- Working examples and templates
- Detailed documentation
- Easy setup and configuration

---

## Future Releases

See [GitHub Issues](https://github.com/yourusername/universal-oauth-sdk/issues) for planned features.

### Planned Features
- More OAuth providers (Twitch, Zoom, GitLab, etc.)
- Client Credentials Flow
- Implicit Flow (legacy support)
- Token revocation endpoint support
- JWT validation helpers
- Token introspection
- More example applications (Next.js, Electron, React SPA)
- Documentation website
- VS Code extension

---

[1.0.0]: https://github.com/yourusername/universal-oauth-sdk/releases/tag/v1.0.0
