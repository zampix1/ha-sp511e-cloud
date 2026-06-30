# Publishing Checklist

Before pushing this repository publicly:

1. Confirm repository metadata points to `https://github.com/zampix1/ha-sp511e-cloud`.
2. Create or update the GitHub repository, then push this folder as the repository root.
3. Confirm GitHub Actions pass:
   - HACS validation
   - Hassfest validation
   - Python tests
4. Create release `v0.1.0`.
5. Test in Home Assistant through HACS as a custom repository.

For HACS default inclusion later, open a PR against the HACS default repository only after the custom repository has a public release, working issues, passing validations, and stable user-facing documentation.
