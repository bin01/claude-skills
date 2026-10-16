# claude-skills

Personal Claude skills, packaged as a plugin marketplace (`bin01-skills`). Each plugin lives under `plugins/<name>/`, with skills in `skills/<skill>/SKILL.md` and subagents in `agents/`.

| Plugin | What it does |
|---|---|
| [raise-the-bar](plugins/raise-the-bar/skills/raise-the-bar/SKILL.md) | Rewrites a task prompt to be more ambitious along altitude, depth, or range before running it. Based on Felix Rieseberg's [How to be more ambitious](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/). |
| [haiku-crew](plugins/haiku-crew/README.md) | Haiku executor subagents plus an `orchestrate` skill for cheaper Opus-plans/Haiku-executes delegation, with an eval suite. |

## Install in the Claude app

In plugin settings, add a marketplace from a repository, paste `https://github.com/bin01/claude-skills`, then install the plugins you want.

## Install in Claude Code

```sh
/plugin marketplace add bin01/claude-skills
/plugin install raise-the-bar@bin01-skills
/plugin install haiku-crew@bin01-skills
```

## Adding a skill

1. Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/skills/<name>/SKILL.md`.
2. Add an entry for it to `.claude-plugin/marketplace.json`.
