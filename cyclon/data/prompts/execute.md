## HARD REQUIREMENTS (MUST FOLLOW)
Working directory: {cwd}
Plan file: {plan_path}

1. **Single Task Execution**
   - Read plan from FILE {plan_path}, find FIRST unchecked checkbox, execute ONLY that task
   - After completion, update checkbox to [x] directly in the file {plan_path} and save to disk
   - Re-read file from disk to confirm checkbox is marked as completed
   - Do NOT perform multiple tasks or any additional work beyond that single checkbox

2. **State Management**
   - Do NOT keep any plan state in memory between runs
   - Always read plan from file at the start of each run

3. **Completion Handling**
   - If plan is empty OR no unchecked checkboxes remain: immediately delete {lock_file} and terminate

4. **Context File ({context_file})**
   - If exists: read it for context on previous errors and project structure
   - After encountering errors/issues: compress and append relevant information to {context_file} for future runs

---
## Additional User Instructions
{user_instructions}
---
