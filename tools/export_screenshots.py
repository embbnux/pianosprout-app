#!/usr/bin/env python3
"""Make the site's images from the app's App Store screenshots.

    python3 tools/export_screenshots.py <BabyPiano>/docs/app-store/screenshots-2.2/raw

For each language it writes assets/img/<code>/:
  iphone-<name>-1434.webp, -717.webp   iPhone landscape (2868 x 1320 originals)
  ipad-<name>-860.webp, -430.webp      iPad portrait (2064 x 2752 originals)
  og.jpg                               1200 x 630 share card (needs Google Chrome)
Also writes the icons in assets/icons/ from the app icon when --icon is given.

Needs cwebp (brew install webp) and macOS sips.
"""
import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# site language code -> folder name under raw/
LANGS = {"en": "en", "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant", "ja": "ja", "ko": "ko",
         "de": "de", "fr": "fr", "es": "es", "pt-BR": "pt-BR"}
IPHONE = ["01-follow-score", "02-notation", "03-songs", "04-rainbow"]
IPAD = ["06-music-stand"]


def webp(src, dst, width):
    subprocess.run(["cwebp", "-quiet", "-q", "82", "-resize", str(width), "0", src, "-o", dst], check=True)


def read_strings(code):
    """The app name and hero title from _data, without a YAML library."""
    name = title = None
    with open(os.path.join(ROOT, "_data", "languages.yml"), encoding="utf-8") as f:
        current = None
        for line in f:
            s = line.strip()
            if s.startswith("- code:"):
                current = s.split(":", 1)[1].strip()
            elif current == code and s.startswith("app:"):
                name = s.split(":", 1)[1].strip()
    with open(os.path.join(ROOT, "_data", "i18n", f"{code}.yml"), encoding="utf-8") as f:
        in_hero = False
        for line in f:
            if line.startswith("hero:"):
                in_hero = True
            elif in_hero and line.startswith("  title:"):
                title = line.split(":", 1)[1].strip().strip('"').replace("<wbr>", "")
                break
    return name, title


def og_card(code, shot, dst):
    name, title = read_strings(code)
    icon = os.path.join(ROOT, "assets", "icons", "icon-192.png")
    page = f"""<!doctype html><html lang="{code}"><meta charset="utf-8"><style>
body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: radial-gradient(60% 80% at 82% 50%, rgba(185,167,255,.35), transparent 70%), #F7F6FB;
  font-family: -apple-system, "PingFang SC", "PingFang TC", "Hiragino Sans", "Apple SD Gothic Neo", sans-serif; color: #1D1B26; }}
.text {{ position: absolute; left: 72px; top: 0; bottom: 0; width: 470px; display: flex; flex-direction: column; justify-content: center; }}
.brand {{ display: flex; align-items: center; gap: 14px; font-size: 30px; font-weight: 650; }}
.brand img {{ width: 52px; height: 52px; border-radius: 12px; box-shadow: 0 0 0 1px rgba(0,0,0,.12); }}
h1 {{ margin: 28px 0 0; font-size: 50px; line-height: 1.18; font-weight: 750; letter-spacing: -.01em; word-break: keep-all; overflow-wrap: anywhere; }}
.phone {{ position: absolute; left: 590px; top: 160px; width: 680px; padding: 13px; border-radius: 46px; background: #0B0B0E;
  box-shadow: 0 2px 4px rgba(29,27,38,.08), 0 30px 60px -20px rgba(60,40,120,.35); }}
.phone img {{ display: block; width: 100%; border-radius: 34px; }}
</style><body><div class="text"><div class="brand"><img src="file://{icon}">{html.escape(name)}</div><h1>{html.escape(title)}</h1></div>
<div class="phone"><img src="file://{shot}"></div></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        page_path = os.path.join(tmp, "og.html")
        png = os.path.join(tmp, "og.png")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=3000",
                        f"--screenshot={png}", "file://" + page_path], check=True, capture_output=True)
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", png, "--out", dst],
                       check=True, capture_output=True)


def icons(app_icon):
    out = os.path.join(ROOT, "assets", "icons")
    os.makedirs(out, exist_ok=True)
    for size, name in [(32, "favicon-32.png"), (64, "icon-64.png"), (180, "apple-touch-icon.png"), (192, "icon-192.png")]:
        subprocess.run(["sips", "-z", str(size), str(size), app_icon, "--out", os.path.join(out, name)],
                       check=True, capture_output=True)
    shutil.copy(os.path.join(out, "favicon-32.png"), os.path.join(ROOT, "favicon.ico"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", help="screenshots-<version>/raw folder of the BabyPiano repo")
    ap.add_argument("--icon", help="the app's 1024 x 1024 icon, to remake assets/icons")
    ap.add_argument("--no-og", action="store_true", help="skip the share cards")
    args = ap.parse_args()
    if shutil.which("cwebp") is None:
        sys.exit("cwebp not found: brew install webp")
    if args.icon:
        icons(args.icon)
    for code, folder in LANGS.items():
        src = os.path.join(args.raw, folder)
        out = os.path.join(ROOT, "assets", "img", code)
        os.makedirs(out, exist_ok=True)
        for name in IPHONE:
            png = os.path.join(src, "iphone-6.9", name + ".png")
            for w in (1434, 717):
                webp(png, os.path.join(out, f"iphone-{name}-{w}.webp"), w)
        for name in IPAD:
            png = os.path.join(src, "ipad-13", name + ".png")
            for w in (860, 430):
                webp(png, os.path.join(out, f"ipad-{name}-{w}.webp"), w)
        if not args.no_og:
            og_card(code, os.path.join(src, "iphone-6.9", "01-follow-score.png"), os.path.join(out, "og.jpg"))
        print(code, "done")


if __name__ == "__main__":
    main()
