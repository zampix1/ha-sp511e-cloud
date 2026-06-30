# Publishing Checklist

Before pushing this repository publicly:

1. Replace every `CHANGE_ME` placeholder:
   - `custom_components/fairynest_sp511e/manifest.json`
   - GitHub repository URL
   - issue tracker URL
   - code owner handle
2. Set the copyright owner in `LICENSE`.
3. Create the GitHub repository, then upload this folder as the repository root.
4. Confirm GitHub Actions pass:
   - HACS validation
   - Hassfest validation
   - Python tests
5. Create release `v0.1.0`.
6. Test in Home Assistant through HACS as a custom repository.

For HACS default inclusion later, open a PR against the HACS default repository only after the custom repository has a public release, working issues, passing validations, and stable user-facing documentation.
