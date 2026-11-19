# FaultyData Registry

The public specimen catalog behind [faultydata.com](https://faultydata.com) —
a failure-signature registry of **cited real-world outages** and classic
HTTP/client failure modes, each replayable live against any HTTP client.

Think Have-I-Been-Pwned, but for your HTTP stack: instead of asking "was my
password leaked?", ask "does my client survive the CrowdStrike channel file,
a Slowloris drip, or a 429 that actually means it?"

## The catalog

`specimens/` holds one YAML file per exhibit — **107 and counting**. Every
specimen has:

| field | meaning |
|---|---|
| `id` | stable `FD-YYYY-NNN` identifier — cite this in bug reports |
| `slug` | human-readable URL (`/specimen/<slug>`) |
| `title`, `category`, `severity` | what it is and how bad it is |
| `tests` | capability tags: `parsing`, `timeouts`, `retry-logic`, `headers`, `semantics`, `loops`, `monitoring`, `auth` |
| `citation` | the real postmortem/doc this is based on — nothing here is invented |
| `anatomy` | the story: what happened in production and why your client should care |
| `signature` | the machine-readable fault: status, headers, body, corruption mode, delays, sequences, raw wire bytes |
| `expect` | (optional) which client outcomes count as surviving |

Real incidents in the catalog include CrowdStrike 2024, AWS S3 us-east-1,
Meta's BGP withdrawal, Cloudbleed, the XZ backdoor, Dyn, Rogers, Southwest,
CodeSpaces, SolarWinds, polyfill.io, left-pad and more — plus classic
pathologies like truncated JSON, redirect loops, duplicate Content-Length
and HTTP/0.9 responses.

## Replay them

No signup needed for the free tier (60 req/min per IP):

```sh
curl https://faultydata.com/r/crowdstrike-channel-file   # one exhibit, live
curl https://faultydata.com/api/specimens               # the whole catalog as JSON
curl -X POST https://faultydata.com/battery \
  -H 'content-type: application/json' -d '{"suite":"starter"}'
```

Exhibits that break the connection itself (resets, raw wire responses) are
served unedited on the direct line `https://faultydata.com:8443`.

## Grade a client in CI — the Action

[`action.yml`](action.yml) downloads the `fd` runner, points your client at
each exhibit in a suite, and the **server** computes the grade — your client
can't grade its own homework.

```yaml
- uses: Q-Nimbus/faultydata-registry@v1
  with:
    suite: starter          # starter | transport | retry-logic | timeouts | ...
    name: my-http-client
    min-score: "80"         # fail CI below this
    client: python3 tests/http_check.py   # optional; empty = Go net/http
```

The client command runs once per exhibit with `$FD_URL` set (`{url}` also
works). Report what happened with `FD_OUTCOME=timeout|parse_error|...` —
see [`examples/http_check.py`](examples/http_check.py) and the
[runner docs](https://faultydata.com/docs#runner). The step summary gets a
link to the public report card and badge.

Current [leaderboard](https://faultydata.com/leaderboard): OkHttp A+, node
fetch A, httpx A — and curl-with-no-flags dead last at F.

## Contributing specimens

Open an issue or PR with the YAML for a real, documented incident — a
postmortem link is required. The bar: it must be *cited*, *reproducible*,
and *named* (`FD-YYYY-NNN`). Chaos is only funny when it's attributable.

## License

MIT — the catalog facts and this repo are free; the server source is not
part of this repository.
