# pianosprout.xyz

Website of PianoSprout (宝宝钢琴师), a piano app for children and beginners on iPhone and iPad: <https://pianosprout.xyz/>

Built by GitHub Pages with Jekyll from the `main` branch.

| Where | What |
| --- | --- |
| `_data/languages.yml` | The 9 languages: addresses, the app's name, App Store badge |
| `_data/i18n/<code>.yml` | Every word on the home page, one file per language |
| `_layouts/` | `base` (head, top bar, footer), `home`, `privacy` |
| `privacy.*.md` | Privacy policies. The old addresses (`/privacy.en`, `/privacy.zh-Han`, `/privacy.jp`, `/privacy.es`, `/privacy.pt`) are linked from App Store Connect: keep them |
| `assets/img/<code>/` | Screenshots for the site, made by `tools/export_screenshots.py` |
| `assets/badges/` | Apple's localized "Download on the App Store" badges |

Preview locally with the same versions as GitHub Pages:

```bash
bundle exec jekyll serve   # with a Gemfile that has `gem "github-pages", group: :jekyll_plugins`
```

Questions and feedback: [support@pianosprout.xyz](mailto:support@pianosprout.xyz). We use your emails only to reply to you.

You can also use <https://github.com/embbnux/pianosprout-app/issues>. Issues are public, so please leave out personal details.
