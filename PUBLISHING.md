# Public release and hosting

The owner requested public release on 25 November 2026 after removing manuscript TeX sources, including from Git history. The released website and repository contain the PDF, CSV tables, figures, code, and numeric data. Manuscript sources are maintained separately.

## Project website

<https://local-geometry-paper-preview.reflectiveshore16.chatgpt.site>

The existing Sites project is reused for the public release. Deploy the checked `docs/` snapshot to that same project and set its audience to public. Preserve its project ID and URL.

## GitHub repository

<https://github.com/ldomenichelli/linguistic-features-of-local-geometry-in-language-models>

After pushing the sanitized history, use **Settings → General → Danger Zone → Change visibility → Make public**. The connected GitHub tools do not expose repository visibility changes or Pages administration. Verify the resulting visibility in GitHub and with an unauthenticated repository request.

The original history is backed up locally outside this repository. Rewritten commit IDs replace the old history; collaborators should clone the sanitized repository afresh. Do not merge or push a checkout containing the original history back into the public branch.

## GitHub Pages

1. Make the repository public after the sanitized history is pushed.
2. In **Settings → Pages**, choose **GitHub Actions** as the source.
3. Run **Actions → Deploy project explorer → Run workflow** with `publish_publicly` enabled.
4. Confirm the deployment succeeds and check the returned Pages URL.

Pushes run validation. The Pages workflow requires manual public opt-in and a public repository. The historical Pages deployment from 21 November 2026 is not evidence of the current publication state.

## Validate and update

```bash
make site
make check
python3 scripts/check_browser.py
git push origin main
```

Check a text search, missing-profile record, model/layer comparison, filtered CSV, figure PDF, and table CSV. Website downloads use PDF, CSV, and JSON. Manuscript TeX is not required by the build, copied into the repository, or served by the website.

Existing commits use Lucia Domenichelli’s verified GitHub noreply identity as author and committer. No code license has been selected.
