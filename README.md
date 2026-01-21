# Cyclon

Cyclon is a generic script to automate tasks using opencode in a loop. It reads a plan (checklist) and prompt from 
markdown files, combines them into a full prompt, and executes opencode commands in a loop with error handling
and retries.

## Usage

1. Create a plan file (default: `.cyclon.plan.md`) with a checklist of steps to perform.
2. Create a prompt file (default: `.cyclon.prompt.md`) with the initial prompt for opencode.
3. Run the script in the desired directory: `python3 /path/to/cyclon`
4. To run in a specific directory: `cd /target/directory && python3 /path/to/cyclon`

### Adding to PATH or Alias

To run `cyclon` from anywhere:

#### Option 1: Add directory to PATH
1. Add the cyclon directory to your PATH: `export PATH=$PATH:/path/to/cyclon/directory`
2. For permanent addition, add the export line to your shell's rc file (e.g., `~/.zshrc`).
3. Restart your shell or run `source ~/.zshrc`.

#### Option 2: Add alias to .zshrc
Add this line to `~/.zshrc`:
```
alias cyclon='python3 /path/to/cyclon/directory/cyclon'
```
Then run `source ~/.zshrc`.

Now you can run `cyclon` from any directory.

The script will:
- Create a lock file (`.cyclon.lock`) to prevent multiple instances.
- Read and combine the plan and prompt files.
- Append instructions for context and lock removal.
- Run opencode in a loop, retrying on specific exceptions.
- Stop if the lock file is removed or an unhandled error occurs.

## Configuration

Edit `config.json` or create a local `.cyclon.config.json` to customize:
- Model: opencode model to use
- Exception strings to retry on
- Sleep duration between retries
- Timeout for opencode commands

Plan and prompt files are fixed as `.cyclon.plan.md` and `.cyclon.prompt.md`.

## Files

- `.cyclon.plan.md`: Checklist of steps (e.g., numbered list)
- `.cyclon.prompt.md`: Initial prompt for opencode
- `.cyclon.lock`: Lock file created at startup, should be removed by AI agent to stop the loop
- `.cyclon.context.md`: Optional context file with compressed error info and project structure, read by opencode if existst