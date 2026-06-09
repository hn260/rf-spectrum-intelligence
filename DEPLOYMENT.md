# 🚀 Deployment Guide

This guide details how to push your local repository to GitHub and deploy the application to **Streamlit Community Cloud** for free public access.

---

## Step 1: Push to GitHub

1. Go to [github.com/new](https://github.com/new) and create a new repository:
   * **Repository name**: `rf-spectrum-intelligence`
   * **Visibility**: Public (recommended to connect with Streamlit Cloud)
   * **Initialize repository**: Do **NOT** add a README, `.gitignore`, or license (as we already have them in our local repository).

2. Open your shell (Powershell/CMD/Terminal) in this directory and execute the following commands to link the local repository and push:
   ```bash
   # Rename default branch to main
   git branch -M main

   # Add your remote URL (replace <username> with your GitHub username)
   git remote add origin https://github.com/<username>/rf-spectrum-intelligence.git

   # Push to remote main
   git push -u origin main
   ```

---

## Step 2: Deploy to Streamlit Community Cloud

Streamlit Community Cloud is a free hosting service provided by Streamlit that spins up persistent Python environments directly connected to your GitHub repositories.

1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in using your GitHub account.
2. Click the **"Create app"** (or **"New app"**) button.
3. Configure the deployment fields:
   * **Repository**: Select `<username>/rf-spectrum-intelligence` from the dropdown list.
   * **Branch**: Set to `main`.
   * **Main file path**: Enter `dashboard/app.py`.
4. Click **"Deploy!"**

Your application will build (installing dependencies from `requirements.txt`) and launch in about 1-2 minutes. You will receive a permanent, shareable URL (e.g. `https://rf-spectrum-intelligence.streamlit.app/`).
