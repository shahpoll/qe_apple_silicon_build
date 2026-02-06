# Wiki Sync Notes

`docs/wiki/` is an in-repo mirror of GitHub wiki content.

GitHub wiki pages are stored in a separate repository:

- `https://github.com/shahpoll/qe_apple_silicon_build.wiki.git`

Recommended update command:

```sh
bash scripts/publish_wiki.sh
```

Manual update flow:

```sh
git clone https://github.com/shahpoll/qe_apple_silicon_build.wiki.git /tmp/qe_wiki
cp docs/wiki/Home.md docs/wiki/Environment.md docs/wiki/Workflow.md docs/wiki/Troubleshooting.md docs/wiki/Results.md /tmp/qe_wiki/
cd /tmp/qe_wiki
git add .
git commit -m "Update wiki pages"
git push
```
