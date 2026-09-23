# Public catalog name snapshot

Source: TCGdex cards database, https://github.com/tcgdex/cards-database
API: https://api.tcgdex.net/v2/en/cards
Database license: MIT; copyright and permission notice in TCGDEX-LICENSE.txt.
TCGdex is not affiliated with Nintendo or The Pokémon Company.
Images are URLs only; no image binaries, prices or full card details are bundled.

Regenerate explicitly from the repository root:

```sh
python scripts/update_catalog_name_index.py --language en
```

The updater downloads brief paginated records and writes a normalized, deduplicated
snapshot atomically only after the download succeeds. Review the data diff before
committing. Names retain meaningful symbols and distinct accented spellings;
matching folds Latin accents. A representative edition with an image is preferred.

The app reads this public file, cached for 24 hours and invalidated by file changes.
It never invokes the updater. Refresh manually when catalog additions warrant it;
there is no scheduled job or runtime refresh. Older snapshots still allow manual
searches for new names. Missing/invalid snapshots disable suggestions only.
Representative images may require the browser to reach the image host; text
suggestions work offline. Full catalog results always require explicit Search catalog.
