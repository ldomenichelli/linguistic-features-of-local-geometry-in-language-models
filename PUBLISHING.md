# GitHub Pages

Project address: <https://ldomenichelli.github.io/linguistic-features-of-local-geometry-in-language-models/>

## Setup

1. In the repository’s **Settings → General**, set its visibility to **Public**.
2. In **Settings → Pages**, choose **GitHub Actions** as the source.
3. Run **Actions → Deploy project explorer → Run workflow** with `publish_publicly` enabled.
4. Check that deployment succeeds before sharing the site address.

The workflow also runs when the repository becomes public and on pushes to `main`. Deployment requires Pages to be configured with GitHub Actions as its source.

## Update the site

```bash
make site
make check
git push origin main
```

The workflow builds and publishes `docs/`. If Pages is not configured, it uploads the site artifact and shows setup instructions in the workflow summary.

For a local preview, run `make serve` and open <http://localhost:8765>. See [SITE.md](SITE.md) for data and website updates.
