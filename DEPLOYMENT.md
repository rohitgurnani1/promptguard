# 🚀 Deployment Guide for PromptGuard

This guide covers multiple ways to host and demo your PromptGuard Streamlit app.

## 🎯 Quick Demo Options

### Option 1: Streamlit Cloud (Recommended for Presentations) ⭐

**Best for**: Live demos, presentations, sharing with others

**Steps**:

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set:
     - **Main file path**: `app.py`
     - **Python version**: 3.8+
   - Click "Deploy"

3. **Add your API key**:
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add:
     ```toml
     OPENAI_API_KEY = "your-api-key-here"
     ```

4. **Access your app**: `https://your-app-name.streamlit.app`

**Pros**:
- ✅ Free
- ✅ Automatic HTTPS
- ✅ Easy to share URL
- ✅ Auto-updates on git push
- ✅ No server management

**Cons**:
- ⚠️ Public by default (can be made private)
- ⚠️ Limited to Streamlit apps

---

### Option 2: ngrok (Quick Local Demo)

**Best for**: Quick demos, testing, local presentations

**Steps**:

1. **Install ngrok**:
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com
   ```

2. **Run your Streamlit app locally**:
   ```bash
   streamlit run app.py
   ```

3. **Create public tunnel**:
   ```bash
   ngrok http 8501
   ```

4. **Share the ngrok URL** (e.g., `https://abc123.ngrok.io`)

**Pros**:
- ✅ Quick setup (5 minutes)
- ✅ Free tier available
- ✅ Works with local app

**Cons**:
- ⚠️ URL changes each time (unless paid)
- ⚠️ Requires your computer to be on
- ⚠️ Free tier has session limits

---

### Option 3: Heroku

**Best for**: More permanent hosting, production use

**Steps**:

1. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `setup.sh`**:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. **Update `Procfile`**:
   ```
   web: sh setup.sh && streamlit run app.py
   ```

4. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-key
   git push heroku main
   ```

---

### Option 4: AWS / Google Cloud / Azure

**Best for**: Enterprise, production, custom requirements

**Steps** (AWS EC2 example):

1. **Launch EC2 instance** (Ubuntu)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install streamlit openai pandas
   ```
3. **Run with nohup**:
   ```bash
   nohup streamlit run app.py --server.port=80 --server.address=0.0.0.0 &
   ```
4. **Configure security group** to allow port 80/443

---

## 🎤 Presentation Tips

### Before the Demo

1. **Test everything beforehand**:
   - Run a quick evaluation to ensure it works
   - Have your API key ready
   - Test on the network you'll use

2. **Prepare example scenarios**:
   - Pick 2-3 interesting attacks to showcase
   - Know which models work best
   - Have expected results in mind

3. **Create a backup plan**:
   - Screenshots/video of the app working
   - Pre-recorded demo video
   - Static slides showing results

### During the Demo

1. **Start with the problem**:
   - "Prompt injection is a real security threat..."
   - Show why defenses matter

2. **Walk through the UI**:
   - Show model selection
   - Explain the 8 attack types
   - Show the 3 defense strategies

3. **Run a live evaluation**:
   - Pick 2-3 attacks
   - Use 2 defenses
   - Show results in real-time

4. **Explain the metrics**:
   - Attack Success Rate (ASR)
   - Robustness Score
   - What they mean

### Demo Script Example

```
1. Introduction (30 sec)
   - "PromptGuard evaluates LLM defenses against prompt injection"

2. Show the UI (1 min)
   - Sidebar: models, attacks, defenses
   - Explain what each does

3. Run evaluation (2 min)
   - Select: gpt-4o-mini, 3 attacks, 2 defenses
   - Click "Run Evaluation"
   - Show progress

4. Explain results (2 min)
   - Show summary table
   - Explain ASR and robustness
   - Show detailed outputs

5. Compare defenses (1 min)
   - Which defense works best?
   - Why?

6. Q&A (remaining time)
```

---

## 🔒 Security Considerations

### For Public Hosting

1. **Don't expose API keys**:
   - Use environment variables
   - Use Streamlit secrets
   - Never commit keys to git

2. **Rate limiting**:
   - Consider adding rate limits
   - Monitor API usage
   - Set spending limits on OpenAI

3. **Access control**:
   - Streamlit Cloud: Can be made private
   - Add authentication if needed
   - Consider IP whitelisting

---

## 📊 Recommended Setup for Presentations

**Best option**: **Streamlit Cloud** + **Backup video**

1. Deploy to Streamlit Cloud (free, reliable)
2. Record a backup demo video
3. Have screenshots ready
4. Test on presentation day

**Quick setup time**: ~15 minutes

---

## 🛠️ Troubleshooting

### App won't start
- Check API key is set
- Verify all dependencies installed
- Check port isn't in use

### Slow evaluations
- Reduce number of attacks/defenses
- Use faster models (gpt-4o-mini)
- Pre-run some evaluations

### API errors
- Check API key is valid
- Verify account has credits
- Check rate limits

---

## 📝 Checklist Before Presentation

- [ ] App deployed and accessible
- [ ] API key configured
- [ ] Tested evaluation runs successfully
- [ ] Backup video/screenshots ready
- [ ] Know which attacks/defenses to demo
- [ ] Understand the metrics
- [ ] Have answers to common questions ready

---

## 🎯 Quick Start Commands

### Local Demo
```bash
streamlit run app.py
# Open http://localhost:8501
```

### ngrok Demo
```bash
streamlit run app.py &
ngrok http 8501
# Share the ngrok URL
```

### Streamlit Cloud
1. Push to GitHub
2. Deploy at share.streamlit.io
3. Add API key in secrets
4. Share the URL

---

**Good luck with your presentation! 🎉**

