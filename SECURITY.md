# 🔒 Security Best Practices

This document explains how API keys and sensitive data are handled in this project.

## ✅ Secure Setup

### API Keys Storage

1. **`.env` file** - Contains your actual API keys
   - ✅ **NOT committed to git** (in `.gitignore`)
   - ✅ **Local only** - stays on your machine
   - ✅ **Auto-loaded** - code automatically reads from it

2. **`.env.example`** - Template file (safe to commit)
   - ✅ **No real keys** - just placeholders
   - ✅ **Shows structure** - helps others set up
   - ✅ **Safe to share** - can be committed to git

### Files with API Keys

**❌ NEVER commit these files:**
- `.env` - Contains real API keys
- `setup_env.ps1` - Now loads from .env (but still ignored)
- `credentials.json` - Google service account credentials
- `config.json` - May contain sensitive data

**✅ Safe to commit:**
- `.env.example` - Template only
- All Python code files - No hardcoded keys
- Documentation files - No real keys

## 🔐 How It Works

### Automatic Key Loading

The code automatically loads API keys from:
1. Environment variables (if set)
2. `.env` file (if exists and `python-dotenv` is installed)

**Example:**
```python
# This code automatically loads from .env
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

api_key = os.getenv('PINECONE_API_KEY')  # Gets from .env or env var
```

### Setting Up

1. **Copy the template:**
   ```powershell
   copy .env.example .env
   ```

2. **Edit `.env` with your keys:**
   ```
   PINECONE_API_KEY=your-actual-key-here
   OPENAI_API_KEY=your-actual-key-here
   ```

3. **Verify it's ignored:**
   ```powershell
   git check-ignore .env  # Should output: .env
   ```

## 🚨 Security Checklist

Before committing to git:

- [ ] `.env` is in `.gitignore` ✅
- [ ] `.env` is NOT in git (check with `git status`)
- [ ] No API keys in code files ✅
- [ ] No API keys in documentation ✅
- [ ] `setup_env.ps1` doesn't contain keys ✅
- [ ] Only `.env.example` is committed (template only) ✅

## 🔄 If You Accidentally Committed Keys

**If you accidentally committed `.env` or keys:**

1. **Remove from git history:**
   ```powershell
   git rm --cached .env
   git commit -m "Remove .env from git"
   ```

2. **Rotate your API keys immediately:**
   - Pinecone: Generate new key in dashboard
   - OpenAI: Generate new key in dashboard
   - Perplexity: Generate new key in dashboard

3. **Update `.env` with new keys**

4. **Force push (if already pushed):**
   ```powershell
   git push --force
   ```
   ⚠️ **Warning:** Only do this if you're the only one using the repo!

## 📝 Current Status

✅ **All API keys are secure:**
- `.env` file created locally (not in git)
- `.env.example` template created (safe to commit)
- All code files updated to load from `.env`
- `.gitignore` updated to exclude sensitive files
- No hardcoded keys in any code

## 🎯 Best Practices

1. **Never commit `.env`** - Always check `git status` before committing
2. **Use `.env.example`** - Share structure, not keys
3. **Rotate keys regularly** - Especially if exposed
4. **Use different keys** - Dev/staging/production should have separate keys
5. **Review commits** - Check `git diff` before pushing

## 🔍 Verify Security

Run these commands to verify:

```powershell
# Check .env is ignored
git check-ignore .env

# Check no keys in code
git grep -i "pcsk_" -- "*.py" "*.md" "*.ps1"

# Check what will be committed
git status
git diff --cached
```

---

**Your API keys are now secure!** 🎉


