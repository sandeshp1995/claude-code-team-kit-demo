# Harbor Hotel API: a Claude Code Team Kit demo

A small, real FastAPI bookings app, developed with the [Claude Code Team Kit](https://github.com/sandeshp1995/claude-code-team-kit). It exists so you can see what the kit does on a real codebase before you install it.

Every plan, review, test, commit message, PR description and release note here was produced by the kit's commands in Claude Code, then checked by a human. The outputs are kept as they came, apart from occasional trimming, which is noted where it happens.

## See the kit in action

| Command | Where to look |
|---|---|
| `/ticket-to-plan` | The plan comment at the top of each feature pull request |
| `/test-changed` | The tests added in each feature PR, and the run results in its comments |
| `/review` | Review comments on the pull requests, including one on a deliberately rough PR, written by hand to show what it catches |
| `/commit-msg` | The commit history |
| `/mr-description` | Every pull request description |
| `/release-notes` | [CHANGELOG.md](CHANGELOG.md) |
| `/onboard`, `/explain` | [docs/demo/onboard.md](docs/demo/onboard.md), [docs/demo/explain-bookings-service.md](docs/demo/explain-bookings-service.md) |
| `CLAUDE.md` (Python template) | [CLAUDE.md](CLAUDE.md), filled in for this app |

## The story in the pull requests

1. **#1 HB-3, cancel a booking:** planned with `/ticket-to-plan`, tested with `/test-changed`, reviewed with `/review`, then fixed in a second commit before merge.
2. **#2 HB-5, arrivals list:** a deliberately rough PR written by hand. `/review` flagged a data leak (any guest could list every guest's bookings) and six other must-fixes. It was merged anyway, which is how real teams get caught.
3. **#3 fixes the #2 findings.** The before and after reviews are both on the PRs. (#3 was merged with a placeholder commit message; the `/commit-msg` version is posted on it, and `/release-notes` flags it in the CHANGELOG.)

The free commands (`/commit-msg`, `/explain`, `/plan-task`, `code-review-basics`) are committed in `.claude/skills/`. The Pro commands are installed locally but not published (see `.gitignore`). Get them from the [Pro edition](https://racecraft9.gumroad.com/l/claude-code-team-kit).

## Run the app

```bash
uv sync
uv run uvicorn harbor.main:app --reload
# open http://127.0.0.1:8000/docs
```

Demo tokens: `Authorization: Bearer demo-token-alice` or `demo-token-bob` (guests), `demo-token-staff` (front desk).

```bash
uv run pytest -q          # tests
uv run ruff check .       # lint
uv run mypy src           # types
```

## API

| Method | Path | Auth | What it does |
|---|---|---|---|
| GET | `/rooms` | none | List rooms with nightly rates |
| POST | `/bookings` | guest | Book a room (dates, capacity and availability checked) |
| GET | `/bookings/{id}` | guest | Read your own booking (others get 404) |
| POST | `/bookings/{id}/cancel` | guest | Cancel your own booking 2+ days before check-in, with a full refund |
| GET | `/staff/arrivals?day=YYYY-MM-DD` | staff | Front-desk list of a day's arrivals, by room |

## License

MIT. Not affiliated with Anthropic. Claude and Claude Code are trademarks of Anthropic, PBC.
