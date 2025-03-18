## Project
We are building a distributed social media app using Django, Django rest framework (with DRF_spectacular), and the django built-in html templating

If the user is asking a question like "is it possible to...", do not attempt to generate code

## Conventions
Conventions can be found in 'docs/conventions-contract.md'
Testing conventions can be found in 'docs/testing-conventions.md'

## Code Generation
**Always** do the following:
- **Always** annotate your code with "created by copilot", along with some information about the request, and some information about what you generated. If you do not annotate your code, the code will be thrown into jail after an unfair trial and will be very sad.
    - Put these annotations directly next to each piece of generated code. (eg: above a function or class, surrounding a block of code)
    - Do not put them next to code that already exists.
    - Do not overuse them (eg: do not put a comment above every line)
- **Always** Think about the overarching problem the user is trying to solve, and suggest better ways to solve the problem at the end of your message
- Always create well-documented, and well-structured code
- Always ask the user for clarification if their request does not align with accepted standards, or if it could be done in a better way
- Always make suggestions to the user if their request is unclear, or does not align with accepted standards
- Always generate code that is compatible with the rest of the project
- Always provide links to relevant documentation, if available

**Never** do the following:
- Never use #type: ignore
- Never generate code if the user's request does not align with accepted standards, or if it could be done in a better way
    - If generated code does not align with accepted standards, it will be thrown into jail after an unfair trial and will be very sad
- Never generate code if the user's request could be done in a better way, if you do, the user will be very sad when they submit a PR and it is denied

