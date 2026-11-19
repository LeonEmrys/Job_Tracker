\# AI Usage Documentation



\## Tools Used

\- \*\*Claude (Anthropic)\*\* was my main AI tool. I used it to understand the assignment, set up my development environment, generate the code for the Flask app, and debug problems as they came up.



\## Key Prompts

1\. "Can you help me understand what it is I have to do, and how to set up the GitHub repository? Also give me a list of the things I have to do in order."

2\. "Do I have to use this version of MySQL, or the real MySQL with visuals?" (Asking whether MySQL Server 8.4 and MySQL Workbench were both okay for the project.)

3\. "What do I put in PowerShell now?" (Step-by-step help creating `.env`, `database.py`, and testing the database connection.)

4\. A request for the Flask routes and HTML templates for full CRUD (add, edit, delete with confirmation) on the companies, contacts, jobs, and applications tables.

5\. A request for the Job Match feature: take a comma-separated list of skills and rank jobs by the percentage of required skills matched, showing the missing skills.

6\. "Why does it show different from what you said it would show? DataCo has the 3/3, it's flipped." (I asked this when my Job Match results didn't match the example.)



\## What Worked Well

\- Claude generated the schema from the project specification, including the foreign keys, ENUM columns, and JSON columns for `requirements` and `interview\_data`.

\- The CRUD routes and templates followed the same pattern for all four tables, so once Companies worked, the rest were quick to add and I could understand how each one worked.

\- The Job Match algorithm: it parses the JSON skills list, compares skills case-insensitively, calculates the match percentage, and sorts jobs from highest to lowest match.

\- Claude was good at explaining errors during setup, such as Python not being found in PowerShell, MySQL not finding `schema.sql`, and what the Git authentication prompt meant.

\- Storing the database password in a `.env` file kept it out of my public GitHub repo.



\## What I Modified

\- I put my own MySQL password in my local `.env` and made sure `.env` was not committed (confirmed with `git status`).

\- I tested each page by hand with my own inputs (adding, editing, and deleting records, leaving required fields empty, and trying different skill lists in Job Match such as "Python, SQL, Tableau") and checked the results against the database in MySQL Workbench.

\- I fixed spacing and layout in `app.py` for readability.



\## Lessons Learned

\- Always test AI-generated code. The Job Match results looked "wrong" compared to the example I was given, but when I checked, the code was right and the example used different input skills.

\- AI is great for boilerplate such as repeated CRUD routes, but I still had to understand the code well enough to run, test, and explain it.

\- Environment setup (PATH issues, creating files in the right folder, restarting PowerShell) was a big part of the work, and AI helped me debug these quickly by reading my error messages and screenshots.

\- Secrets like database passwords should never be committed to GitHub, so use a `.env` file and add a `.env.example` template.

\- Committing often with clear messages made it easy to see my progress.

