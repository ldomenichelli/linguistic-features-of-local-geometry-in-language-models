# Publishing the repository and GitHub Pages site

The prepared repository name is:

```text
linguistic-features-of-local-geometry-in-language-models
```

The intended owner is `ldomenichelli`. No code license has been selected. Do not add a blanket license to the third-party excerpts.

## Repository

The public repository has been created at:

<https://github.com/ldomenichelli/linguistic-features-of-local-geometry-in-language-models>

The local `main` branch is published through the owner’s SSH connection. Existing release commits use Lucia Domenichelli’s verified GitHub noreply identity as both author and committer. Do not rewrite published history when updating ordinary project files.

After making and checking changes:

```bash
git push origin main
```

## Activate the site

For the one-time GitHub Pages activation, open **Settings → Pages → Build and deployment → Source → GitHub Actions**. The workflow is already in [`.github/workflows/pages.yml`](.github/workflows/pages.yml). Before activation, the workflow builds and checks the site but skips deployment with a setup note in its run summary. Selecting the source does not rerun an already completed workflow. After enabling Pages, run **Actions → Deploy project explorer → Run workflow**, or push the next checked update to `main`, to build and deploy the site.

Once the deployment succeeds, the expected project URL is:

<https://ldomenichelli.github.io/linguistic-features-of-local-geometry-in-language-models/>

The static site uses relative paths and needs no API keys, server, or model inference. The deployment uploads only `docs/`. It validates the released data and downloadable results before publication. [GitHub’s Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) describes the required Pages environment and permissions.

## Verify before sharing

```bash
make check
make serve
```

Check an excerpt permalink, a filtered CSV download, two-excerpt comparison, a figure PDF, and a current table CSV. Optional real-browser automation is available in `scripts/check_browser.py`; its help explains the local Chrome endpoint. Record the successful Pages workflow URL before describing the site as published. The manuscript’s repository link is intentionally left unchanged.

## Optional browser verification

With a local Chrome DevTools endpoint on port 9222, install `websocket-client` in your analysis environment and run:

```bash
.venv/bin/pip install websocket-client
.venv/bin/python scripts/check_browser.py --screenshots /tmp/local-geometry-preview
```

The script is local developer tooling, separate from the static site and its deployment. It verifies actual interactions and downloads, including missing FCI values and the lexical-density display convention.
