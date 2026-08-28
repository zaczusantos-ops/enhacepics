"""
ChurchPhoto Pro - Git Initializer and Remote Sync using Dulwich
"""

import os
from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo

REPO_PATH = Path(r"c:\Users\Claudio\Downloads\enhancepics")
REMOTE_URL = "git@github.com:zaczusantos-ops/enhacepics.git"

def main():
    print(f"Initializing Git repository at: {REPO_PATH}")
    
    # 1. Initialize or open repo
    git_dir = REPO_PATH / ".git"
    if not git_dir.exists():
        repo = porcelain.init(str(REPO_PATH))
        print("Git repo initialized.")
    else:
        repo = Repo(str(REPO_PATH))
        print("Existing Git repo opened.")

    # 2. Configure author/committer
    config = repo.get_config()
    config.set(("user",), "name", "ChurchPhoto Pro Bot")
    config.set(("user",), "email", "bot@churchphoto.pro")
    config.write_to_path()

    # 3. Add all files
    porcelain.add(str(REPO_PATH))
    print("Files staged.")

    # 4. Commit
    try:
        commit_sha = porcelain.commit(
            str(REPO_PATH),
            message=b"feat: Big Update - Remocao Equipes, IA Rigorosa e Presets Lightroom",
            author=b"ChurchPhoto Pro Bot <bot@churchphoto.pro>",
            committer=b"ChurchPhoto Pro Bot <bot@churchphoto.pro>"
        )
        print(f"Commit created: {commit_sha.decode('ascii') if isinstance(commit_sha, bytes) else commit_sha}")
    except Exception as e:
        print(f"Commit note: {e}")

    # 5. Add remote
    try:
        porcelain.remote_add(str(REPO_PATH), "origin", REMOTE_URL)
        print(f"Remote origin added: {REMOTE_URL}")
    except Exception as e:
        print(f"Remote note: {e}")

    # 6. Push to remote
    print("Pushing to remote repository...")
    try:
        porcelain.push(str(REPO_PATH), REMOTE_URL, refspecs=[b"HEAD:refs/heads/main"])
        print("Successfully pushed to origin main!")
    except Exception as e:
        print(f"Push with default refspec failed: {e}. Trying master refspec...")
        try:
            porcelain.push(str(REPO_PATH), REMOTE_URL, refspecs=[b"HEAD:refs/heads/master"])
            print("Successfully pushed to origin master!")
        except Exception as e2:
            print(f"Push error: {e2}")

if __name__ == "__main__":
    main()
