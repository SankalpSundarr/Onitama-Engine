# From the downloaded ZIP to GitHub

These steps use Windows PowerShell. Run each block in order, and stop if a
command reports an error. Skip installations you already have.

## 1. Install the tools

1. Create or sign in to your account at <https://github.com>.
2. Install Git for Windows: <https://git-scm.com/download/win>.
   Keep Git Credential Manager enabled and allow Git on the command line.
3. Install 64-bit Python 3.12 if needed. Its Windows installer is available at
   <https://www.python.org/downloads/release/python-31210/>.
   Keep the Python launcher enabled. Other Numba-compatible Python versions
   can also work, but change the `py -3.12` command accordingly.
4. Reopen PowerShell after installation, then check:

```powershell
git --version
py -3.12 --version
```

## 2. Extract the project

Right-click `onitama-engine.zip` in Explorer and choose **Extract All**.
Open the extracted folder containing `README.md`, `requirements.txt`, and
`onitama_optimized.py`. If there are two nested `onitama-engine` folders, use
the inner one containing those files.

Click Explorer's address bar, type `powershell`, and press Enter. Check:

```powershell
Get-ChildItem
```

## 3. Install dependencies and run one move

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_demo.py --depth 4 --plies 1
```

Wait for the Numba warm-up. You should then see a board, one move, a score,
node count, elapsed seconds, and nodes per second.

To run 20 moves at depth 6:

```powershell
.\.venv\Scripts\python.exe run_demo.py --depth 6 --plies 20
```

## 4. Optional: start the local API

```powershell
.\.venv\Scripts\python.exe backend.py
```

Open <http://127.0.0.1:5000/health>. A JSON response with `status: ok` confirms
the server is running. No graphical frontend is included. Press Ctrl+C in
PowerShell before continuing with Git commands.

## 5. Make the first local commit

Replace `YOUR_GITHUB_EMAIL` with an email verified on your GitHub account,
or copy your GitHub-provided private commit email from
<https://github.com/settings/emails>.

```powershell
git init -b main
git config user.name "Sankalp Sundar"
git config user.email "YOUR_GITHUB_EMAIL"
git add .
git status
git commit -m "Add Onitama bitboard engine, demo and local API"
```

The configuration is local to this repository. `.gitignore` excludes the
virtual environment, caches, local environment files, and tablebase files.
Check `git status` before committing: it should list source and documentation,
not `.venv` or large generated data.

## 6. Create an empty GitHub repository

Visit <https://github.com/new>:

- Name: `onitama-engine`.
- Description: `Onitama engine using bitboards, Numba JIT and alpha-beta search`.
- Choose **Public** if you want to share it as a portfolio project.
- Do not initialize a README, `.gitignore`, or license: the local repository
  already contains its first commit.
- Click **Create repository**.

## 7. Push the code

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/onitama-engine.git
git push -u origin main
```

Complete the GitHub browser sign-in when prompted by Git Credential Manager.
Refresh the repository page. You should see the source files and rendered README.

## 8. Publish later updates

Run these inside the same project folder after editing and checking the code:

```powershell
git add .
git status
git commit -m "Describe the change you made"
git push
```

An editor such as VS Code is optional. Git records versions locally; `git push`
uploads your commits. Do not rerun `git init` or `git remote add origin` for each
update. A public repository does not automatically run the Python API online.

## Common first-run issues

- **`git` is not recognized:** reopen PowerShell after installing Git.
- **Python 3.12 is not found:** install it, or use the launcher for your installed
  Numba-compatible version when creating `.venv`.
- **`requirements.txt` is not found:** open PowerShell in the folder that
  actually contains the extracted files.
- **`No module named ...`:** run pip through the same `.venv` Python shown above.
- **`origin already exists`:** inspect `git remote -v`. If it points to the
  correct repository, continue with `git push`; do not add it again.
- **GitHub rejects the first push because it has existing commits:** the remote
  was initialized with files. Do not force-push; reconcile the histories or use
  a new, empty repository.

## References

- [GitHub: adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub: credential manager](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git)
- [Numba: installation and Python support](https://numba.readthedocs.io/en/stable/user/installing.html)
