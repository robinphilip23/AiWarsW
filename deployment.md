# Hosting Guide for AgriShield

This guide covers how to deploy your Flask AI application to a server. Since you are in a hackathon, **Option 1 (Render)** is recommended for speed and ease. **Option 2 (AWS EC2)** is better if you want full control or have a very large model file (>500MB).

## Prerequisites (Do this first)

1.  **Code Preparation**:
    I have already created `requirements.txt` in your app folder. This tells the server what libraries to install.

2.  **Folder Structure**:
    Ensure your GitHub repository root is `agrisheild-final`.
    The server needs to see `plant_disease_model.h5` and `Hackathon\Image_chatbot_website`.

---

## Step 0: Push Code to GitHub (Required for Option 1)
Before deploying, your code needs to be on GitHub.

1.  **Initialize Git** (if not done):
    ```bash
    git init
    ```

2.  **Add Files**:
    ```bash
    git add .
    ```

3.  **Commit**:
    ```bash
    git commit -m "Initial commit for hackathon"
    ```

4.  **Create Repo**:
    *   Go to [github.com/new](https://github.com/new).
    *   Name it `agrisheild-final`.
    *   **Do NOT** check "Add a README" or ".gitignore".
    *   Click **Create repository**.

5.  **Connect & Push**:
    *   Copy the commands under "**…or push an existing repository from the command line**".
    *   They look like this (replace `YOUR-USERNAME`):
    ```bash
    git remote add origin https://github.com/YOUR-USERNAME/agrisheild-final.git
    git branch -M main
    git push -u origin main
    ```

---

## Option 1: Render (Easiest & Free Tier)
*Best for Hackathons. Automatic HTTPS.*

1.  **Push your code to GitHub**.
2.  Go to [dashboard.render.com](https://dashboard.render.com/).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Settings**:
    *   **Name**: `agrisheild`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r Hackathon/Image_chatbot_website/requirements.txt`
    *   **Start Command**: `cd Hackathon/Image_chatbot_website && gunicorn app:app`
6.  **Environment Variables** (Advanced):
    *   Key: `OPENROUTER_API_KEY`
    *   Value: `sk-or-v1-...` (Your actual key)
    *   Key: `PYTHON_VERSION`
    *   Value: `3.10.12` (Optional, but good for stability)
7.  Click **Create Web Service**.

> **Note on Model Size**: If your `.h5` model is >100MB, ensure you have Git LFS enabled or it might fail to push to GitHub. If it's too big for GitHub, you might need Option 2.

---

## Option 2: AWS EC2 (Ubuntu VM)
*The "Server Instance" approach. Robust but requires manual setup.*

### 1. Launch Instance
1.  Log in to AWS Console -> **EC2**.
2.  **Launch Instance**:
    *   **OS**: Ubuntu 22.04 LTS.
    *   **Instance Type**: `t2.medium` or `t3.medium` (Need at least 4GB RAM for TensorFlow). **t2.micro (free tier) might crash** loading the model.
    *   **Key Pair**: Create one and download the `.pem` file.
    *   **Security Group**: Allow HTTP (80), HTTPS (443), and SSH (22).

### 2. Connect & Setup
Open your terminal (where the `.pem` file is):
```bash
ssh -i "your-key.pem" ubuntu@<your-instance-public-ip>
```

Run these commands inside the server:
```bash
# Update system
sudo apt update && sudo apt install python3-pip python3-venv nginx git -y

# Clone your repo
git clone https://github.com/your-username/agrisheild-final.git
cd agrisheild-final

# Setup Virtual Env
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r Hackathon/Image_chatbot_website/requirements.txt
```

### 3. Test Run
```bash
cd Hackathon/Image_chatbot_website
# Export your key temporarily
export OPENROUTER_API_KEY="sk-or-v1-..."
# Run with Gunicorn to test
gunicorn --bind 0.0.0.0:5000 app:app
```
Visit `http://<your-instance-ip>:5000` to verify.

### 4. Keep it Running (Systemd)
Create a service file so it runs in the background.
```bash
sudo nano /etc/systemd/system/agrisheild.service
```
Paste this (adjust paths if needed):
```ini
[Unit]
Description=Gunicorn instance to serve AgriShield
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/agrisheild-final/Hackathon/Image_chatbot_website
Environment="PATH=/home/ubuntu/agrisheild-final/venv/bin"
Environment="OPENROUTER_API_KEY=sk-or-v1-..."
ExecStart=/home/ubuntu/agrisheild-final/venv/bin/gunicorn --workers 3 --bind unix:agrisheild.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```
Save (`Ctrl+O`, `Enter`) and Exit (`Ctrl+X`).

Start it:
```bash
sudo systemctl start agrisheild
sudo systemctl enable agrisheild
```

### 5. Configure Nginx (Public Access)
```bash
sudo nano /etc/nginx/sites-available/agrisheild
```
Paste:
```nginx
server {
    listen 80;
    server_name <your-public-ip>;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/agrisheild-final/Hackathon/Image_chatbot_website/agrisheild.sock;
    }
}
```
Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/agrisheild /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

Now your app allows traffic on port 80!
