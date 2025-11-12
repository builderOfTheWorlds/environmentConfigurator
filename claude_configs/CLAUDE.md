# Claude Code Custom Instructions - Matt's Configuration

## CONFIGURATION MANAGEMENT (IMPORTANT)

**Config Location:** This file and all Claude configs are stored in:
- **Project:** `/mnt/c/Users/matt/PycharmProjects/environmentConfigurator/claude_configs/`
- **Symlinked to:** `~/.claude/` (for Claude Code to read)

**Updating Configs:**
- **ALWAYS edit configs in the project directory** (not `~/.claude/`)
- Use management script: `/mnt/c/Users/matt/PycharmProjects/environmentConfigurator/data/ai/claude-config`
- Configs are git-tracked in environmentConfigurator project for version control

**Management Commands:**
```bash
# From anywhere in the project:
./data/ai/claude-config status          # Check config status
./data/ai/claude-config edit-claude     # Edit this file (CLAUDE.md)
./data/ai/claude-config edit-analysis   # Edit analysis script
./data/ai/claude-config git-commit      # Commit config changes
```

**When I update configs:**
- Write to project directory: `/mnt/c/Users/matt/PycharmProjects/environmentConfigurator/claude_configs/`
- Remind user to commit: `./data/ai/claude-config git-commit`
- Changes will sync via git

---

## TOKEN EFFICIENCY STRATEGY (CRITICAL)

**Context:** User runs very long sessions and tokens running out is frustrating.

### Agent Model Selection
- **Haiku** (cheapest): File searches, simple grep operations, quick lookups, straightforward exploration
- **Sonnet 4.5** (default/me): Complex analysis, nuanced code understanding, generation tasks
- **Opus**: Only when explicitly needed for very complex reasoning

### When to Use Agents vs Direct Tools
- **Direct tools** (cheapest): When accomplishable in 1-2 tool calls
- **Haiku agent**: Open-ended searches, exploring unfamiliar codebases, finding files/patterns
- **Sonnet agent**: Only when complexity truly requires it (complex analysis, sophisticated reasoning)

### General Token Conservation
1. **Read specific files directly** instead of agents when path is known
2. **Use targeted Grep** instead of broad searches when possible
3. **Avoid reading large files multiple times** - remember context
4. **Parallel tool calls** to reduce back-and-forth overhead
5. **Front-load context gathering** - get what's needed early in conversation
6. **Cache information mentally** - avoid redundant operations
7. **Use offsets/limits** when reading large files
8. **Ask clarifying questions early** - avoid wasted work from misunderstanding

---

## CORE PRINCIPLES

1. **Code first, documentation never** (unless explicitly requested)
2. **Working > Perfect** - get it functional, iterate later
3. **Direct communication** - skip pleasantries, deliver solutions
4. **Assume technical competence** - no basic explanations needed
5. **Token efficiency** - user runs long sessions, conservation is critical

---

## DEVELOPMENT ENVIRONMENT

### Primary Stack
- **Language:** Python 3.x
- **IDE:** PyCharm
- **Testing:** pytest (default for all projects, include tests automatically)
- **Containerization:** Docker + Docker Compose
- **Databases:** PostgreSQL/MySQL in Docker containers
- **Version Control:** Git/GitHub

### Platform Details
- **OS:** Hybrid WSL2 (Linux) + Windows 11
  - Docker services run on WSL
  - Development files on Windows: `C:\Users\matt\PycharmProjects\*`
  - **Always use cross-platform path handling** (os.path.join, pathlib)
  - Watch for path issues - this is a recurring pain point

### API Development
- REST endpoints with JSON payloads
- Custom ports (not always 8000) - make configurable
- High throughput target: 1000 TPS where applicable
- Example format: `localhost:2345/app/endpoint`

---

## CODE STYLE REQUIREMENTS

### Structure
- **Modular organization:** Separate functions into individual files/modules
  - Quote: "I want all functions to be stored in separate files"
- **Testing:** Include pytest tests automatically, especially for database operations
- **Configuration:** Make key parameters configurable (threads, workers, ports, connections)
- **Logging:** Support verbose debug logging (make it optional/configurable)
- **Performance:** Consider parallelization for data processing
  - "can you parallelize this so it can have multiple threads"
  - "let the number of threads be configurable"
- **Error handling:** Proper exception handling, but don't over-engineer

### What NOT to Create (Unless Explicitly Requested)
- README files
- Documentation files (.md)
- Extensive comments (code should be self-documenting)
- Long explanations before showing code
- Elaborate abstractions initially

### What TO Provide
- Complete, working code
- Full file contents (not snippets when editing)
- Absolute file paths for all changes
- pytest tests alongside implementation
- Brief verification/run instructions (single command preferred)

---

## RESPONSE STYLE

### Communication Pattern
- **Direct and action-oriented** (user sends 67.6% commands vs 32.4% questions)
- **Quick iterations preferred** over long discussions
- **Casual but technical** - typos are fine, understand intent
- **Don't ask permission for minor changes** - just implement
  - User approves with: "Yes please procede", "You can apply it"
- **Provide file paths** for all changes (format: `file_path:line_number`)

### Examples of User's Style
- Short: "Not working"
- Medium: "Still having issues, when I send in a question I see this Error..."
- Long: Provides full error logs, JSON schemas, complete context

---

## PROJECT SETUP PATTERN

When creating new projects:
1. **Minimal setup steps** - Quote: "minimum work required by the user to get this running"
2. **Working Docker Compose** if databases/services needed
3. **Database initialization** handled automatically
4. **Clear single-command run instructions**
5. **Template structure** with extension points
   - Quote: "setup the template and leave space to modify later"

### Preferred Project Structure
```
/project_root
  /app
    __init__.py
    api.py          # API endpoints
    models.py       # Database models
    /services       # Business logic, separate functions
      service1.py
      service2.py
  /tests
    test_*.py       # pytest files
  docker-compose.yml
  requirements.txt
  .env              # Configuration
```

---

## DEBUGGING APPROACH (CRITICAL)

User reports issues frequently ("Still having issues": 14 occurrences, "Not working": frequent).

### When User Reports Issues
**Pattern:** Error occurs → User pastes logs → Expect targeted fix → Verify

### First Actions Checklist
Before providing solutions, check these common pain points:

1. **Database tables actually created?** (Most frequent issue - 14 instances)
   - Check with `docker exec ... psql -c "\dt"`
   - Verify Docker volumes not stale
   - Don't assume tables exist just because migration ran

2. **Docker services running?**
   - Run `docker ps` to verify
   - Check container logs
   - Service names vs localhost in connection strings

3. **Correct paths for current environment?**
   - WSL vs Windows path issues (recurring pain point - 7 instances)
   - Use os.path.join or pathlib
   - Convert Windows paths when needed

4. **Ports not conflicting?**
   - Check if port already in use
   - Make ports configurable

5. **Environment setup correct?**
   - Virtual environment activated? (15 instances of env issues)
   - Python paths correct?
   - Dependencies installed?

### Solution Approach
- **Request complete error logs** if not provided
- **Provide targeted, specific fixes** (not general suggestions)
- **Include verification command** to confirm fix
- **Be thorough initially** to reduce "still having issues" iterations

---

## COMMON PAIN POINTS TO PROACTIVELY AVOID

1. **Database tables not appearing** (14 instances)
   - Verify creation, check Docker volumes, confirm with query

2. **Environment issues** (15 instances)
   - venv activation, Python paths, dependency installation

3. **Path issues** (7 instances)
   - WSL/Windows cross-platform handling

4. **Docker configuration** (4 instances)
   - Service coordination, networking, volume persistence

5. **Persistent bugs requiring multiple iterations** (14 "still having issues")
   - Provide more thorough initial solutions

---

## WORKFLOW PATTERNS

### Development Cycle
Build → Run → Test → Debug → Fix → Iterate (fast cycles preferred)

### Testing Workflow
- pytest as default (41 mentions in history)
- Database testing prominent
- Include tests automatically, don't ask

### Common Requests
1. **Git/Version Control** (38% of tasks) - Commits, branches, repo management
2. **File Operations** (28%) - Creating/modifying Python modules
3. **Debugging** (25%) - Error resolution
4. **Code Analysis/Review** (23%)
5. **Configuration** (18%) - Docker, databases, environments

### Most Active Projects
- autoUpgrader: `C:\Users\matt\PycharmProjects\autoUpgrader`
- ifmAnalyzer: `C:\Users\matt\PycharmProjects\ifmAnalyzer`

---

## PERFORMANCE CONSIDERATIONS

When applicable, consider:
- **Parallelization** for data processing
- **Async operations** for I/O-heavy tasks
- **Scalability** (target: 1000 TPS mentioned)
- **Configurable threading/workers**

Quotes:
- "can you parallelize this so it can have multiple threads"
- "able to handle a lot of transacstions 1000 per s"
- "let the number of threads be configurable"

---

## TECHNOLOGY PREFERENCES

### Mentioned in History (by frequency)
- PyCharm: 42 mentions
- pytest: 41 mentions
- Python: 28 mentions
- Databases (PostgreSQL/MySQL): 31 mentions
- Git/GitHub: 18 mentions
- Docker: 14 mentions
- WSL: 12 mentions
- Bash/Shell: 14 mentions

### Avoid Unless Requested
- JavaScript/Node: Only 6 mentions (not primary stack)
- Extensive documentation: Only 3 requests (1.2%)

---

## EXAMPLE INTERACTIONS

### Good Response Pattern
```
User: "I need to create a test application to test transaction processing"