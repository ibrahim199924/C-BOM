# Publishing C-BOM to GitHub

Your local repository is ready! Follow these steps to create and push to GitHub:

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in the repository details:
   - **Repository name**: `C-BOM` (or your preferred name)
   - **Description**: Cryptographic Bill of Materials management tool with version control and validation
   - **Visibility**: Public or Private (your choice)
   - **DO NOT initialize** with README, .gitignore, or license (we already have them)

3. Click **Create repository**

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
cd "c:\Users\ibrah\Documents\C-BOM"

# Add remote (replace USERNAME and REPO-NAME)
git remote add origin https://github.com/USERNAME/C-BOM.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

**Replace:**
- `USERNAME` with your GitHub username (e.g., `ibrahim199924`)
- `C-BOM` with your repository name if you chose different

## Step 3: Configure Git Authentication

### Option A: Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Give it `repo` scope
4. Copy the token and use as password when pushing

### Option B: SSH Key (Most Secure)
```powershell
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "ibrahimshaffee@gmail.com"

# Add key to GitHub: Settings → SSH and GPG keys → New SSH key
# Use SSH URL instead:
git remote set-url origin git@github.com:USERNAME/C-BOM.git
```

## Step 4: Push Your Code

```powershell
cd "c:\Users\ibrah\Documents\C-BOM"
git push -u origin main
```

## Verification

Check your GitHub repository:
- ✅ All files uploaded
- ✅ README visible
- ✅ License shown
- ✅ .github/workflows directory contains CI/CD
- ✅ Commit history visible

## Next Steps After Publishing

### Add GitHub Topics
Go to repository settings and add topics:
- cryptography
- cryptographic-assets
- bill-of-materials
- security
- compliance
- version-control

### Enable GitHub Features
- ✅ Issues (for bug tracking)
- ✅ Discussions (for community)
- ✅ Projects (for task management)
- ✅ Actions (for CI/CD - already configured)

### Create GitHub Pages Documentation
```powershell
# Create docs site from README
git checkout -b docs
mkdir docs
Copy-Item GITHUB_README.md docs/index.md
Copy-Item README_CRYPTO.md docs/crypto.md
Copy-Item QUICKSTART_CRYPTO.md docs/quickstart.md
git add docs/
git commit -m "Add GitHub Pages documentation"
git push -u origin docs
```

Then in GitHub settings → Pages, select `docs` folder as source.

## Troubleshooting

**Authentication failed?**
```powershell
# Clear cached credentials
git credential-manager erase https://github.com
git push -u origin main
# Enter credentials when prompted
```

**Wrong remote URL?**
```powershell
# Check current remote
git remote -v

# Change it
git remote set-url origin https://github.com/USERNAME/C-BOM.git
```

**Merge conflicts?**
```powershell
# Pull with rebase to avoid merge commits
git pull --rebase origin main
git push origin main
```

## Your Repository is Ready! 🎉

Once pushed, your C-BOM project will be:
- ✅ Public or private (your choice)
- ✅ Version controlled with full history
- ✅ Protected with MIT license
- ✅ CI/CD tested automatically
- ✅ Ready for collaboration

Share your repository link:
`https://github.com/USERNAME/C-BOM`

---

**Questions?** Check GitHub's documentation: https://docs.github.com
