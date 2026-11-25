# Public release and hosting

The owner requested public release on 25 November 2026 after removing manuscript TeX sources, including from Git history. The released website and repository contain the PDF, CSV tables, figures, code, and numeric data. Manuscript sources are maintained separately.

## Project website

Intended GitHub Pages address:

<https://ldomenichelli.github.io/linguistic-features-of-local-geometry-in-language-models/>

GitHub Pages is the public hosting destination. The separate Sites preview is private and is not the public project website. The address above is ready for use after repository visibility and Pages activation are completed and deployment succeeds.

## GitHub repository

<https://github.com/ldomenichelli/linguistic-features-of-local-geometry-in-language-models>

After pushing the sanitized history, use **Settings → General → Danger Zone → Change visibility → Make public**. The connected GitHub tools do not expose repository visibility changes or Pages administration. Verify the resulting visibility in GitHub and with an unauthenticated repository request.

The original history is backed up locally outside this repository. Rewritten commit IDs replace the old history; collaborators should clone the sanitized repository afresh. Do not merge or push a checkout containing the original history back into the public branch.

## GitHub Pages

1. Make the repository public after the sanitized history is pushed.
2. In **Settings → Pages**, choose **GitHub Actions** as the source.
3. The change to public visibility starts the deployment workflow automatically. If Pages was enabled afterward, run **Actions → Deploy project explorer → Run workflow** with `publish_publicly` enabled, or push a new commit to `main`.
4. Confirm the deployment succeeds and check the returned Pages URL.

Pushes to `main` and the change to public visibility start the Pages workflow. Manual runs require a public opt-in. Deployment requires a public repository and Pages configured with GitHub Actions as its source. If activation is missing, the workflow builds and uploads the checked artifact and provides activation instructions without claiming a deployment. The historical Pages deployment from 21 November 2026 is not evidence of the current publication state.

## Validate and update

```bash
make site
make check
python3 scripts/check_browser.py
git push origin main
```

Check a text search, missing-profile record, model/layer comparison, filtered CSV, figure PDF, and table CSV. Website downloads use PDF, CSV, and JSON. Manuscript TeX is not required by the build, copied into the repository, or served by the website.

Existing commits use Lucia Domenichelli’s verified GitHub noreply identity as author and committer. No code license has been selected.
