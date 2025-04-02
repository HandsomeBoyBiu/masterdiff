# masterdiff

## What is masterdiff?

`masterdiff` is a tool that can help you analyze and export the files changed in each commit in the git repository

## How to build masterdiff?
`pip install GitPython`

## How to use masterdiff?
usage: `python masterdiff.py [-h] --repo REPO [--output OUTPUT] [--last LAST]`

```
options:
  -h, --help       show this help message and exit
  --repo REPO      Your repoitory path
  --output OUTPUT  Output directory path, default: ./
  --last LAST      Number of recent changes to extract, default: 5
```
