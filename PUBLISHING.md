# Private review and publication

Public publication is paused. The project should remain in a private GitHub repository, with GitHub Pages unpublished, during this review period.

## Private preview

The owner-only site is:

<https://local-geometry-paper-preview.reflectiveshore16.chatgpt.site>

Sites enforces access for the project owner. Static HTML, excerpts, and result files must remain behind that access control; a client-side password is not a privacy boundary.

## Repository access

Repository: <https://github.com/ldomenichelli/linguistic-features-of-local-geometry-in-language-models>

In **Settings → General → Danger Zone → Change visibility**, choose **Make private** and complete GitHub’s confirmation. Independently, open **Settings → Pages**, use the menu beside the site address, and choose **Unpublish site** if a deployment remains. A private repository alone does not guarantee private Pages access on every GitHub plan.

The connected GitHub tools do not expose these administrative settings. Verify the repository visibility in the owner’s settings and check that its anonymous API URL and the former public Pages URL return 404.

## Updates during private review

```bash
make site
make check
python3 scripts/check_browser.py

git push origin main
```

Pushes run validation but never publish GitHub Pages. The Pages workflow only supports manual dispatch; `publish_publicly` defaults to false, and publication also requires a public repository. Keep that option off during private review.

Update the existing private Sites project from the checked `docs/` snapshot, preserving its project ID and owner-only audience. Do not create a second site or change access to publish an update.

Existing commits use Lucia Domenichelli’s verified GitHub noreply identity as both author and committer. Preserve this identity and ordinary published history. No code license has been selected.

## Future public release

Only after a new request to publish publicly, change repository visibility as appropriate, configure Pages with **GitHub Actions** as its source, and run **Actions → Deploy project explorer → Run workflow** with `publish_publicly` explicitly enabled.

Check a text search, missing-profile record, model/layer comparison, filtered CSV, figure PDF, and table CSV. Website downloads use PDF, CSV, and JSON; ZIP and TeX files remain outside the site output.

The first public deployment was verified on 21 November 2026 ([workflow run](https://github.com/ldomenichelli/linguistic-features-of-local-geometry-in-language-models/actions/runs/44924561912)). This historical deployment is not evidence that the site is currently public.
