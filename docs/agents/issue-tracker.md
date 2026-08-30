# Issue tracker: Jira (project KAN)

Issues and specs for this repo live in Jira project **KAN** on `arkhaya.atlassian.net`
(cloudId `arkhaya.atlassian.net`). Use the Atlassian MCP tools (`mcp__claude_ai_Atlassian__*`)
for all operations; there is no CLI. The README roadmap is synced from the KAN board by
`.github/workflows/sync-roadmap.yml`, so anything created here shows up there within 6 hours.

## Project vocabulary

- **Issue types**: `Task` (default for tickets), `Story`, `Bug`, `Epic` (container), `Subtask` (needs a parent).
- **Statuses**: `To Do` → `In Progress` → `Done`; also `On Hold` and `Cancelled`.
- **Labels**: free-form Jira labels, created on first use. None are in use today.
- **Link types**: `Blocks` (inward "is blocked by" / outward "blocks"), `Relates`, `Duplicate`, `Cloners`.

## Conventions

- **Create an issue**: `createJiraIssue` with `projectKey: KAN`, `issueTypeName: Task` (or `Bug`/`Story`), `summary`, `description` (markdown), optional `labels`.
- **Read an issue**: `getJiraIssue` with the key (e.g. `KAN-42`); pass `fields: ["*all", "comment"]` when you need comments and links.
- **List issues**: `searchJiraIssuesUsingJql`, e.g. `project = KAN AND statusCategory != Done ORDER BY created DESC`, adding `AND labels = "<label>"` filters as needed.
- **Comment on an issue**: `addCommentToJiraIssue`.
- **Apply / remove labels**: `editJiraIssue` with `fields: { labels: [...] }` (send the full desired list — read current labels first).
- **Close**: `transitionJiraIssue` to `Done`. For `wontfix`, apply the label and transition to `Cancelled` instead.
- **Claim**: `editJiraIssue` with `fields: { assignee: { accountId } }`; get your own id from `atlassianUserInfo`.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature
requests; `/triage` reads this flag. PRs live on GitHub — `gh pr view/list/comment` — not in Jira.)_

## When a skill says "publish to the issue tracker"

Create a KAN issue with `createJiraIssue`.

## When a skill says "fetch the relevant ticket"

`getJiraIssue` with `fields: ["*all", "comment"]`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is an Epic; tickets are its child issues.

- **Map**: an `Epic` labelled `wayfinder-map`, holding the Notes / Decisions-so-far / Fog body in its description.
- **Child ticket**: a `Task` created with `parent: { key: KAN-<map> }`. Labels: `wayfinder-<type>` (`research` / `prototype` / `grilling` / `task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: a `Blocks` issue link via `createIssueLink` — `inwardIssue` = the blocker, `outwardIssue` = the blocked ticket. A ticket is unblocked when every blocker is `Done`/`Cancelled`.
- **Frontier query**: `parent = KAN-<map> AND statusCategory != Done AND assignee IS EMPTY ORDER BY created ASC`, then drop any ticket whose `issuelinks` contain an "is blocked by" link to an unresolved issue; first remaining wins.
- **Claim**: assign the ticket to yourself (see Conventions) — the session's first write.
- **Resolve**: `addCommentToJiraIssue` with the answer, `transitionJiraIssue` to `Done`, then append a context pointer (gist + link) to the map Epic's Decisions-so-far via `editJiraIssue`.
