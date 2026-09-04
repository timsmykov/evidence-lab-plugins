# Evidence Lab Research Skills

This is the onboarding-free, one-install distribution of the Evidence Lab skill
library. Installing this plugin makes every published research skill and the
personal skill-authoring procedure available immediately. It does not ask
profile questions, select companion plugins, or change the host beyond this
single plugin installation.

The skill implementations remain canonical in their focused packs. The
`skills/` entries in this bundle are generated, byte-checked mirrors created by
`scripts/build_research_bundle.py`. Keeping physical copies inside the plugin
makes local and remote marketplace installation behave the same way.

Install only this plugin when the user wants the complete library without
onboarding:

```text
evidence-lab-research@evidence-lab-plugins
```

See the repository [getting-started guide](../../../docs/getting-started.md) for
Codex and Claude Code commands, verification, first-task examples, and
troubleshooting. The [skill catalogue](../../../docs/skills.md) lists every
included procedure with its use case, expected output, canonical source, and
readiness status.

The separate `evidence-lab-core` plugin retains the optional onboarding and
profile-based installer for users who want a smaller tailored setup.
