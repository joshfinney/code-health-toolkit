# Work Laptop Handoff

## Principle

Do not make the project stealthy. Make it boring, accurate, and easy to explain.

This repository should be presented as a deterministic engineering quality
toolkit. It should not contain company code, work outputs, credentials, or audit
reports from proprietary repositories.

## Recommended path

1. Create an approved internal private repository.
2. Use a clear name such as `engineering/code-health-toolkit`.
3. Commit with your approved work Git identity.
4. Push to the internal host.
5. Clone from the internal host onto the work laptop.

## Before the first commit

Check your Git identity:

```bash
git config user.name
git config user.email
```

If the repository is going to an internal work host, set the local repo identity
to your approved work identity before committing:

```bash
git config user.name "Your Name"
git config user.email "your.name@company.com"
```

Then commit:

```bash
git add .
git commit -m "Initial code-health toolkit"
```

## Publish to the approved internal host

```bash
git remote add origin git@approved-host:engineering/code-health-toolkit.git
git push -u origin main
```

Then clone on the work laptop:

```bash
git clone git@approved-host:engineering/code-health-toolkit.git
```

## What not to do

- Do not push this to a personal public repository for work use.
- Do not include proprietary source code or audit output.
- Do not rename the project to hide its purpose.
- Do not use this to bypass policy, monitoring, review, or approval.
- Do not mix generic tooling with confidential work artefacts.

## Safe explanation

Use this description if asked what the repo is:

```text
This is a local code-health toolkit for Python repositories. It provides
deterministic audit scripts, hotspot ranking, and repository guidance for small,
reviewable maintainability improvements. It does not contain proprietary source
code or committed audit output.
```

