# Wiki Sync Notes

`docs/wiki/` is an in-repo mirror of GitHub wiki content.

GitHub wiki pages are stored in a separate repository:

- `https://github.com/shahpoll/qe_apple_silicon_build.wiki.git`

Update flow:

```sh
git clone https://github.com/shahpoll/qe_apple_silicon_build.wiki.git /tmp/qe_wiki
cp docs/wiki/*.md /tmp/qe_wiki/
cd /tmp/qe_wiki
git add .
git commit -m "Update wiki pages"
git push
```
