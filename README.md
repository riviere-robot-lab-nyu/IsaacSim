# A simple guide to push your changes to another branch 

This guide walks you through pushing local changes to a new branch in your forked repository, especially when your local directory doesn't have a `.git` folder yet.

If you want to check the original READMD.md, check [here](isaacsim_ori.md).

## Step-by-Step Workflow

### 1. Initialize Git in your local directory
```bash
cd /path/to/your/local/repo
git init
```

### 2. Add your fork as the remote
```bash
git remote add origin https://github.com/riviere-robot-lab-nyu/IsaacSim.git
```

### 3. Fetch the repository history
```bash
git fetch origin
```

This downloads the repository metadata without modifying your local files.

### 4. Create a new branch based on the main branch
```bash
# First, check what the default branch is called
git branch -r

# Create and switch to a new branch (replace 'main' if the default branch has a different name)
git checkout -b my-feature-branch origin/main
```

### 5. Stage your changes
```bash
# Stage all changes
git add .

# Or stage specific files
git add file1.py file2.py
```

### 6. Commit your changes
```bash
git commit -m "Description of your changes"
```

### 7. Push to your fork
```bash
# Push to a new branch with the same name
git push origin my-feature-branch

# Or push to a branch with a different name
git push origin my-feature-branch:different-branch-name
```

## Useful Commands
```bash
# Check the status of your changes
git status

# Verify your remote is configured correctly
git remote -v

# View your commit history
git log --oneline -5

# See what files have changed
git diff --stat
```

