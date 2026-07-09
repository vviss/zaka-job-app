# Changes

The given code ran but had a number of issues across security, accuracy, and
performance.
Below is a list of the issues I found and what I changed to fix them, along with my reasoning for the fix.

## Security

**The filesystem MCP server exposed the whole repo, with no path checks.**
`config.json` set the server root to `..` (the entire project), and `read_file` / `list_dir` did a plain `os.path.join(ROOT, path)` with no validation.
So a path like `.env`, `../../personal/my_passwords`, or an absolute path could read any file on disk (including `.env`), which holds the API keys.
I scoped the server to the `data/` folder and resolved the path with `realpath` and rejected anything that lands outside `data/`.

**`write_file` and `delete_file` were exposed as tools.**
A read-only research assistant has no reason to write or delete files, and a prompt injection
could convince the model to use them. Removed both tools (server + schema +
dispatch) and set the config `permissions` to read-only.

**Access control was an LLM decision.**
`can_access` asked the model to answer ALLOW/DENY - non-deterministic, prompt-injectable, and `"ALLOW" in verdict` even matches something like "I will not ALLOW this".
(The prompt itself didn't even have an explicit instruction for the model to use the word "ALLOW" to grant access).
Replaced it with a deterministic code check: resolve the path and confirm it's inside `data/<team>/`.

**`list_dir` wasn't access-checked.**
The gating only covered `read_file`, so directory listing could enumerate another team's folder.
Added `list_dir` to the same check - it's also a read of the file system.

**The API key was being written to the logs.**
`llm.py` injected an `Authorization: Bearer <key>` header into the request payload purely for logging (not actually used by the API call)
Removed it, and changed the default `LOG_LEVEL` from `DEBUG` to `INFO` so full request payloads (documents, prompts) aren't dumped by default either.

**The team name was unvalidated.**
`--team` was joined straight into a path, so `--team ../../something` could cross out of `data/`, and an unknown team crashed with an unhandled error.
The team is now validated against the real subfolders of `data/`, with a message listing the valid teams (assuming team names themselves are not sensitive data).

**The answer cache ignored the team.**
The cache key was the question only, so asking the same question for two teams returned the first team's answer.
This caused cross-team intereference, so basically wrong answers (for example, the planning deadline differs per team).
Changed the cache key to `(team: question)`.

## Accuracy

**Conflicting handbooks in the acme data.**
`acme` had two handbooks with different planning deadlines, both ingested, so the deadline answer was either one of the two.
Removed the old one and renamed the one with `current` in its name to just `handbook`.
Ideally here I would implement data versioning instead of removing old files manually.

**Retrieval ignored non-English text.**
The tokenizer was `[a-z0-9]+`, which drops everything non-English/Latin, so Arabic queries were ignored (not tokenized) and matched nothing (couldn't get any Arabic answers from the bilingual doc).
Switched to a more general `\w+`.

**Chunking cut through sentences and tables.**
Documents were sliced into fixed 500-character pieces, which split sentences and also tables like the Q3 headcount into different chunks.
Now it splits on paragraphs (blank lines) and includes whole paragraphs up to the size limit, with a one-paragraph overlap so that paragraphs related in meaning stay somehow connected (ie. not discarded as being irrelevant).

**Retrieval scoring was biased toward long chunks.**
The score was just the count of matching words, so a longer chunk could rank higher simply because it has more words (more chances to match), not because it's actually more relevant.
Now the score is normalized by the chunk's term count (a density of matches instead of a raw count).

Note: Before I'd changed the chunking from fixed-size pieces to splitting by paragraphs, this wasn't an issue since all chuncks were equal. But with my current approach, I think it's a better practice (even though for our specific dataset I didn't feel much improvements).

**The researcher only saw a 120-char preview of each chunk.**
The preview shown to the researcher was truncated to 120 chars, so the answer was often not in the context it saw (it could still open the file, but most of the times chose not to).
Dropped the truncation: it costs a few more tokens but the results are clearly better.

**Writer hallucinations and wrong citations.**
The prompt said "answer using your knowledge and the following context", which caused made-up answers AND wrong citations
(it once cited "job_description.md" when asked about the tasks of a new engineer, this file doesn't exist in the data).
We now give it deterministic sources from previous steps, and we ask it explicitly in the prompt to not rely on its own knowledge as fallback.

**Off-topic questions were answered from the model's own general knowledge.**
Only the writer was grounded to the context, not the researcher, so for a question that isn't in the docs, the researcher would answer from its own knowledge and the writer would just pass it through.
I grounded the researcher's prompt the same way (only use the documents, or a web search it actually ran), but it was still stubborn for very well known facts (ex: "what is the capital of France?").
So when nothing matches in the docs, instead of letting the model fill the void from its own knowledge, I fallback to a web search.

**Citation sources could include files that were never actually read.**
The researcher added a file to the sources as soon as the model asked to read it, _before_ the read actually ran.
So if the model guessed a filename that doesn't exist (but is inside the team folder, so it passes the access check), it still ended up cited even though the read failed.
Now a file is only added to the sources if it actually exists on disk, so a missing/hallucinated file never gets cited.

**Only the first plan step was used, and it hid the real user's question.**
The orchestrator ran the planner, then passed only `steps[0]` to the researcher as the search query.
So the researcher _and retrieval_ worked off just the first step of the plan instead of the full plan.
The 'first step' of the plan most of the time doesn't even contain the context of the user's actual question, and results were random (a question would answer correctly one run and "I don't know" the next). Now the real question is passed through (retrieval uses it) and the full plan
is passed to the researcher as a scratchpad for its chain-of-thought process.

**The researcher did a single tool round.**
It made one round of tool calls then a forced summary, so it couldn't analyze an action and decide the next step (ex: read a document and then
follow up on it).
So basically the researcher can now read a doc, analyze the info, decide the next step, and maybe read again if it needs before answering.
Made it a bounded loop (with max steps to avoid excessive thinking, latency, token usage, and a possible infinite loop if the LLM is stubborn and can't accept a failure to answer a question).

**Infinite loops.**
Both the model-call retry and the JSON-parse retry were `while True`. A bad API key or a recurring non-JSON reply would loop forever.
Set a max retries variable for both.

**Web search was a dummy endpoint (always crashed).**
It pointed at a placeholder URL with no error handling, so it never worked and any call crashed the researcher.
Wired it to DuckDuckGo (free, no api key) and wrapped it in a 'try/except' block.
It returns an empty string when nothing comes back, so I use it as the fallback when the docs have nothing
When the web search doesn't return anything, I don't go through the LLM at all and instead I return a hard-coded 'not-found' note to avoid having to convince the model not to use its own knowledge to answer the question (plus save an LLM call).

## Performance

**Redundant API call**
The writer made a second LLM call just to format text to markdown.
Just added an instruction to answer with markdown to the original prompt and answer directly with markdown (to reduce latency and token usage).
