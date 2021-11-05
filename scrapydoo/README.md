# scrapydoo - index a directory in elasticsearch

> Warning: this does not really work

This project is a proof of concept to show how Rust can be used to
index logfiles in elasticsearch.

## Follow-ups

- Add build uuid to the clap arg so that the tool can index logs from a log server or a zuul executor
- Investigate why jwalk does not run in parallel
- Add zuul build api support to:
  - get recent builds
  - fetch zuul-manifest
  - stream build logs fetch to elastic index
