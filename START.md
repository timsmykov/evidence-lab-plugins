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
   > `START.md` and `BOOTSTRAP.md` from that same release. Speak in plain
   > language, ask the four setup questions one at a time, show the complete
   > recommendation, and install nothing until I confirm it.

3. Answer four short questions. A number, several numbers, or a personal answer
   are all valid.
4. Review the universal research foundation and any profile-specific additions,
   then answer yes only if the complete recommendation looks right.
5. When setup is complete, open a new task and begin with the actual research
   goal.

For Russian-language setup, use [START.ru.md](START.ru.md).

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

Start with a short expectation, then ask question 1 immediately:

> I will ask four short questions, show the complete recommendation, and wait
> for your approval before adding anything. You can choose one or several
> numbers, or write your own answer.

For each question:

- show `Question N of 4`;
- render every option as a numbered plain-language choice;
- end with `Choose one or several numbers, or write your own answer.`;
- ask only one question in a message;
- do not repeat an answer that is already clear from the conversation.

After normalization, build the locked installation plan and render it through
`scripts/render_plan.py`. Show that rendered recommendation instead of raw JSON,
pack manifests, commands, or internal rule IDs. Installation begins only after
an explicit affirmative answer to the rendered confirmation question.

## Completion contract

Say setup is complete only after host readback confirms every selected pack and
version. Then tell the researcher:

> Evidence Lab is ready. Open a new task so the application can load the new
> research capabilities. Start that task with what you actually want to work
> on; you will not need to repeat setup.

Follow the recovery behavior in [BOOTSTRAP.md](BOOTSTRAP.md) for every partial,
failed, or interrupted installation.
