# Start Evidence Lab

This is the app-first entrypoint for a researcher who has not installed
Evidence Lab yet. The researcher should not need to run or understand terminal
commands, plugin manifests, marketplaces, schemas, or Git.

## What the researcher does

1. Open a new local task in Codex or Claude Code from the folder where the
   research will live.
2. Paste this message:

   > Set up Evidence Lab for my research from
   > `https://github.com/timsmykov/evidence-lab-plugins`. Use only the latest
   > published `release-*` GitHub Release and its `release-lock.json`. Follow
   > `START.md` and `BOOTSTRAP.md` from that same release. After verification,
   > run `python3 scripts/render_onboarding.py language` from the pinned release
   > and show its output verbatim. Then continue entirely in my chosen language, ask
   > the four setup questions one at a time, show the complete
   > recommendation, and install nothing until I confirm it.

3. Choose English or Russian, then answer four short research questions. A
   number, several numbers, or a personal answer are all valid.
4. Review the universal research foundation and any profile-specific additions,
   then answer yes only if the complete recommendation looks right.
5. When setup is complete, open a new task and begin with the actual research
   goal.

## What the agent does before the first question

Keep these steps in the background unless the researcher asks for technical
details:

1. Detect the active host from the running application. Do not ask the
   researcher whether they use Codex or Claude Code.
2. Resolve the latest published, non-draft, non-prerelease GitHub Release. Do
   not treat a tag without a published Release as installable.
3. Obtain the repository at that exact tag and download its
   `release-lock.json` asset. Read `START.md` and `BOOTSTRAP.md` from the pinned
   checkout, never from a floating branch.
4. Verify the tag, source commit, catalog, and pack hashes with the pinned
   release tools before collecting profile data.
5. Keep the checkout separate from the researcher's project state. Store the
   validated profile, plan, and installation state under the research project
   at `.evidence-lab/`.

If the stable release cannot be verified, stop before onboarding and explain in
one sentence that setup could not be safely checked. Do not fall back to
`main`, another tag, or an unverified archive.

## Conversation contract

Before the expectation or any research question, run
`python3 scripts/render_onboarding.py language` and show its stdout verbatim.
Do not compose, shorten, translate, or paraphrase that message.

Resolve the choice through the deterministic language selector. If it is not
recognized, repeat only this choice. After a valid answer, continue entirely in
English or Russian and show the matching expectation:

> I will ask four short questions, show the complete recommendation, and wait
> for your approval before adding anything. You can choose one or several
> numbers, or write your own answer.

For each question, run `python3 scripts/render_onboarding.py question --locale
<en|ru> --number <1|2|3|4>`. Add `--include-expectation` only for question 1.
Show stdout verbatim. Do not invent a profile quiz or substitute another
question. In particular:

- show `Question N of 4`;
- render every option as a numbered plain-language choice;
- end with `Choose one or several numbers, or write your own answer.`;
- ask only one question in a message;
- do not repeat an answer that is already clear from the conversation.

After normalization, build the locked installation plan with `bootstrap.py
plan --locale <en|ru> --recommendation .evidence-lab/recommendation.md`; this
fused command prints the canonical recommendation. Show its stdout verbatim instead of raw
JSON, pack manifests, commands, or internal rule IDs. If the output does not
start with the locale's canonical recommendation heading, stop and rerun the
renderer; never replace it with a technical summary. Installation
begins only after an explicit affirmative answer to that rendered confirmation
question.

## Completion contract

Say setup is complete only after host readback confirms every selected pack and
version. The confirmed apply command must use `--locale <en|ru>` and its
canonical completion stdout must be shown verbatim:

> Evidence Lab is ready. Open a new task so the application can load the new
> research capabilities. Start that task with what you actually want to work
> on; you will not need to repeat setup.

Follow the recovery behavior in [BOOTSTRAP.md](BOOTSTRAP.md) for every partial,
failed, or interrupted installation.
