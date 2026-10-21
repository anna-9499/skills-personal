# Part B — CCR template (fill in directly or copy into a separate file)

> If the target knowledge base already has its own CCR template, use theirs instead of this one. Replace every `<<< PRODUCT >>>` with the real product name, and delete this instruction line from the final file.

Use when the canonical QA context (Product KB / Feature Profile / Checklist) of `<<< PRODUCT >>>` is **missing, wrong, stale or contradicting** a change that has shipped / is about to ship.

**How to submit:** fill in this file (keep the `# Part N` section structure), attach it to the related task in the team's context management system, then press Submit. Submitting is a manual, human action.

The system receiving CCRs usually does not read the content — it only does a rough check that no `<<< ... >>>` placeholder is left.

## Field labels

| Label | Meaning |
|---|---|
| `[AGENT]` | The person/agent writing the CCR can fill it from Jira + the canon they looked up. The submitter only needs to review. |
| `[YOU]` | Needs human judgement — do not decide on your own, ask the submitter. |

Things you **do not need to ask the submitter**: what the context builder may mutate on the real environment, which account to explore with, whether to capture network/DB — that is the policy of whoever owns the target environment.

**No information → write "unknown".** A declared gap can be handled; a gap filled with a guess spreads into the KB and into every test case generated after it.

---

## Part 0 — How many CCRs? `[YOU confirm, AGENT proposes]`

The unit of a CCR is **one thing that can be resolved independently**, not a single Jira ticket. Several tickets can be merged into 1 CCR if all 4 points below are the same; split if **at least one** point differs:

| | Question |
|---|---|
| Who unblocks | Can the context builder explore it alone, or does it need a dev answer / PO decision / taxonomy owner decision? |
| Unlock condition | Exactly **one** piece of information or **one** action finishes it? |
| Lifecycle | If this request is cancelled, do the remaining tickets still have value on their own? |
| Target artifact | Same KB of one specific object, or does it touch the shared registry/taxonomy? |

Do not over-merge: putting "needs a dev answer" together with "just needs re-exploring" makes the part that could be explored right away wait for dev for no reason.

---

## Part 1 — What was seen

**Request type** `[AGENT proposes, YOU approve]`

`NEW_FEATURE` · `BEHAVIOR_CHANGE` · `PROFILE_GAP` · `CHECKLIST_GAP` · `STALE_CONTEXT` · `CONFLICT` · `CANON_HYGIENE`

**Type:** `<<< FILL IN >>>`

**Object** `[AGENT]` — taken from the target knowledge base's registry, if you have access

- Object: `<<< object_key >>>` · Feature: `<<< feature_key or leave empty >>>`
- Matches no object, or the registry could not be looked up? Describe it in words. **Do not invent an object_key that does not exist.**

**Observed** `[AGENT]` — summarised from the Jira ticket(s), NOT speculation

```
<<< For each ticket: key, title, resolve date, summary of the behaviour change taken from description + comments
    (especially dev-written comments like "Context"/"Behaviour changes"/"Test cases") >>>
```

- Source: `<<< e.g. summarised from N Done Jira tickets, NOT observed directly on the real environment >>>`
- Times seen / times confirmed directly: `<<< the real number — a Jira summary not yet verified yourself means 0 >>>`

**What was tried and NOT reproduced / what was not tried** `[AGENT + YOU]`

```
<<< say plainly what has NOT been verified directly on the real environment — an honest "not tried" is better
    than letting the person/agent handling the CCR assume it was tried >>>
```

**Scope to re-explore & estimated impact** `[AGENT]` — REQUIRED, this is the most important part

> Different from "Observed" above: it does not describe WHAT happened, but **WHAT TO DO NEXT**. After reading this, the person/agent handling the CCR must know right away which surface to re-verify, and the knock-on impact in advance.

For EACH separate ticket/claim in "Observed":

| Ticket / claim | Surface to re-verify | Why it cannot be trusted yet | Object/feature/checklist likely affected | Trust level |
|---|---|---|---|---|
| `<<< e.g. PROJ-123 — add field X to form Y >>>` | `<<< portal · api · storefront · db — be SPECIFIC, do not write "all" without a reason >>>` | `<<< e.g. only a dev description in a comment, not observed on the real environment >>>` | `<<< object_key/feature_key/checklist_id if known, or "unclear, needs own assessment" >>>` | `<<< TRUSTED (test case PASS #id) / TRUSTED (PO/Dev confirm: "quote" — link) / NOT ENOUGH — needs re-explore >>>` |

- A claim that may make a published checklist/automation WRONG (not just MISSING coverage) → name the suspected checklist_id/check code; this is a higher-priority signal than an ordinary "gap".
- Suspect the current object boundary no longer makes sense → state the IDEA, **do not decide a new object_key name yourself**.
- Not sure which surface is affected → write "unclear, needs own assessment", **do not leave it empty**.
- The "Trust level" column decides whether the person/agent handling the CCR may skip re-exploring this claim — only write "TRUSTED" when you have 1 of these 2, with a concrete citation:
  - **Test case run and PASSED**: id + run date + build, checking exactly the claimed behaviour.
  - **Clear PO/Dev confirmation**: verbatim quote + link, confirming exactly the claimed behaviour.
  - Only self-taken screenshots/API captures → must write "NOT ENOUGH — needs re-explore", however sure you are.

---

## Part 2 — Where it was seen `[AGENT]`

- **Specific URL / ID known:** `<<< storefront URL, campaign/instance id, endpoint, Jira link — anything available >>>`
- **State of the object when observed / when the ticket describes it:** `<<< FILL IN >>>`
- **Environment described in the original ticket (not necessarily the one used to re-explore):** `<<< staging | production | unknown >>>`
- **Role involved:** `<<< e.g. guest buyer | owner | staff — if the ticket says >>>`
- **Surface:** `portal` · `storefront` · `api` · `db`

---

## Part 3 — Avoiding false conflicts `[AGENT]`

> Most "conflicts" are not real contradictions, but two observations that are both correct where nobody wrote down which build each ran on.

For EACH ticket:

- **Build / version / deploy date:** `<<< or "unknown" — do not leave empty >>>`
- **Last resolve/update date:** `<<< YYYY-MM-DD >>>`
- **Shipped yet:** `<<< Resolution: Done/merged/deployed, or not >>>`

**What the context currently says** `[AGENT]` — look up the canon BEFORE submitting

- Context version in use: `<<< if it can be looked up >>>`
- Canon currently says: `<<< verbatim quote of the related KB-id/check-id, or "not found" >>>`
- Keywords searched: `<<< list them >>>`
- Canon could not be looked up → state clearly "could not be looked up — the person/agent handling the CCR must look it up again".

---

## Part 4 — Two questions only a human can answer `[YOU]`

### 4.1 Has anyone confirmed this is the CORRECT behaviour?

- Who confirmed: `<<< PO | Dev | spec | PASSED test case | NOBODY — only a dev description/comment >>>`
- Where, when: `<<< e.g. comment #xxx on yyyy-mm-dd, or test case TC-xxx PASS on yyyy-mm-dd on build yyy >>>`
- What exactly they confirmed: `<<< verbatim quote, do not paraphrase >>>`

> A dev's own technical comment (including "Ready to test", "Resolution: Done") is **NOT** a PO/business sign-off. Nobody really confirmed → the knowledge goes into the context labelled "current observation" (unconfirmed), and is not used as an expected result.

### 4.2 What is NOT being proposed?

**Required.** List clearly what must NOT be treated as confirmed/approved even though it is in the ticket:

```
<<< e.g. specific figures the dev wrote at ship time, proposed object_key name, proposed feature boundary, etc. >>>
```

### 4.3 What the context should say `[AGENT writes, YOU approve]`

```
<<< write it as a sentence that will sit in the KB — describe the current state that needs re-verifying, do not assert it as certain >>>
```

### 4.4 Urgency `[YOU]`

`HIGH` (blocking P0/P1 tests) · `MEDIUM` (affects coverage) · `LOW` (gradual improvement)

---

## Part 5 — Evidence `[AGENT]`

Jira ticket link / screenshots / response / HAR: `<<< FILL IN >>>`

> **Before attaching: remove emails, phone numbers, addresses, real customer names, tokens, cookies, credentials.** Internal dev/support names in Jira comments are usually acceptable, but still check carefully.

---

## Self-check before submitting

`[YOU]`:
- [ ] This really is **one** independently resolvable thing (Part 0)
- [ ] Answered 4.1 honestly — even when the answer is "nobody, just a dev comment"
- [ ] Filled in 4.2
- [ ] Evidence has PII/token/credential removed

`[AGENT]`:
- [ ] The number of direct confirmations is the real number, not rounded up
- [ ] Wrote the build/resolve date or admitted "unknown" for each ticket
- [ ] Wrote the keywords used to look up the canon (or why it could not be looked up)
- [ ] Every ticket/claim in "Observed" has 1 matching row in "Scope to re-explore & estimated impact"
- [ ] Each row's "Trust level" column has exactly 1 of the 3 states, with a concrete citation when writing "TRUSTED"
- [ ] No `<<< ... >>>` placeholder is left in the file
