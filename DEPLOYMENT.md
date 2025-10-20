# Deployment Guide

Your Fact-Check News app is now ready to deploy! Follow these steps to get it running on Autonomy.

## Prerequisites Checklist

Before deploying, you need:

- [ ] **Autonomy Account**: Sign up at https://my.autonomy.computer
- [ ] **Docker**: Installed and running from https://www.docker.com/get-started/
- [ ] **Brave Search API Key**: Get from https://brave.com/search/api/
- [ ] **Autonomy CLI**: Will be installed in Step 1

## Step-by-Step Deployment

### Step 1: Install Autonomy CLI

```bash
curl -sSfL autonomy.computer/install | bash && . "$HOME/.autonomy/env"
```

Verify installation:
```bash
autonomy --version
```

If the command is not found, run:
```bash
source "$HOME/.autonomy/env"
```

### Step 2: Start Docker

Make sure Docker Desktop is running. Verify with:

```bash
docker ps
```

You should see a table of running containers (may be empty).

### Step 3: Configure Secrets

Create `secrets.yaml` in the project root:

```bash
cd /path/to/autonomy-demo
cp secrets.yaml.template secrets.yaml
```

Edit `secrets.yaml` and replace `your_brave_api_key_here` with your actual Brave Search API key.

**Get your Brave Search API key:**
1. Go to https://brave.com/search/api/
2. Sign up for a free account
3. Create an API key
4. Copy the key into `secrets.yaml`

### Step 4: Enroll with Autonomy

This connects your local machine to your Autonomy cluster:

```bash
cd /path/to/autonomy-demo
autonomy cluster enroll --no-input
```

**Important**: This will print a code and open your browser. Follow the prompts to authenticate.

### Step 5: Deploy Your App

```bash
autonomy zone deploy
```

This will:
- Build Docker images
- Push them to your Autonomy cluster
- Start the fact-checking service
- Configure the Brave Search MCP server
- Deploy the web UI

**Note the output!** It will show your cluster and zone names, for example:
```
Cluster: a9eb812238f753132652ae09963a05e9
Zone: factcheck
```

### Step 6: Access Your App

Once deployed (takes about 1-2 minutes), access your app at:

```
https://${CLUSTER}-${ZONE}.cluster.autonomy.computer/
```

Replace `${CLUSTER}` and `${ZONE}` with the actual values from Step 5.

For example:
```
https://a9eb812238f753132652ae09963a05e9-factcheck.cluster.autonomy.computer/
```

## Testing Your Deployment

### 1. Check Health

```bash
timeout 15s curl --silent --request GET \
"https://${CLUSTER}-${ZONE}.cluster.autonomy.computer/api/health"
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test Fact-Check API

Create a test file `test-article.json`:

```json
{
  "article": "According to a recent study, global temperatures have increased by 1.1°C since pre-industrial times. The Arctic ice has decreased by 13% per decade since 1979. Scientists predict that sea levels could rise by 1-2 meters by 2100 if current trends continue."
}
```

Test the fact-check endpoint:

```bash
timeout 120s curl --silent --request POST \
--header "Content-Type: application/json" \
--data @test-article.json \
"https://${CLUSTER}-${ZONE}.cluster.autonomy.computer/api/fact-check"
```

This should return a comprehensive fact-check report.

### 3. Test the Web UI

Open your browser and go to:
```
https://${CLUSTER}-${ZONE}.cluster.autonomy.computer/
```

1. Paste an article into the text box
2. Click "Fact-Check Article"
3. Wait 30-60 seconds for processing
4. View the comprehensive report

## Monitoring and Debugging

### View Logs

Start the logs server:

```bash
cd /path/to/autonomy-demo
autonomy zone inlet --to logs > logs_server.log 2>&1 &
LOGS_PID=$!
sleep 3
LOGS_PORT=$(grep -o "localhost:[0-9]*" logs_server.log | cut -d: -f2 | head -1)
echo "Logs available at: http://127.0.0.1:$LOGS_PORT"
```

Open the logs in your browser:
```bash
open "http://127.0.0.1:$LOGS_PORT"
```

Stream logs in terminal:
```bash
POD_NAME=main-pod
CONTAINER_NAME=main
FULL_POD_NAME=$(timeout 10s curl -s "127.0.0.1:$LOGS_PORT/" | grep -o 'main-pod-[a-z0-9]*-[a-z0-9]*' | head -1)
timeout 30s curl -N "127.0.0.1:$LOGS_PORT/pods/$FULL_POD_NAME/containers/$CONTAINER_NAME" | head -50
```

Stop the logs server when done:
```bash
kill $LOGS_PID
```

### List All Zones

```bash
autonomy zone list
```

### Check Deployment Status

```bash
autonomy cluster show
```

## Redeploying After Changes

If you make changes to the code:

### Update Backend (Python)

```bash
cd /path/to/autonomy-demo
autonomy zone deploy
```

### Update Frontend (UI)

```bash
cd /path/to/autonomy-demo/ui
npm run build-autonomy
cd ..
autonomy zone deploy
```

## Troubleshooting

### "AlreadyExists" error for agents

This is normal for the orchestrator agents but shouldn't affect functionality. The agents will reuse existing instances.

### Build fails

Make sure Docker is running:
```bash
docker ps
```

### Can't access the app

1. Wait 2-3 minutes after deployment for everything to start
2. Check logs for errors
3. Verify zone is running: `autonomy zone list`

### Fact-check takes too long

First-time deployments may take longer as agents initialize. Subsequent requests should be faster.

### "Connection refused" errors

The zone might still be starting. Wait a minute and try again.

## Deleting Your App

To remove the deployment:

```bash
cd /path/to/autonomy-demo
autonomy zone delete --yes
```

**Warning**: This will permanently delete your deployment.

## Example Fact-Check Articles

Try these sample articles to test your app:

### Climate Change Article
```
According to NASA, global temperatures have increased by 1.1°C since pre-industrial times. The Arctic sea ice is declining at a rate of 13% per decade. Scientists warn that if greenhouse gas emissions continue at current rates, sea levels could rise by 1-2 meters by 2100, affecting millions of coastal residents.
```

### Technology News Article
```
Apple announced its latest iPhone with a revolutionary new chip that delivers 40% faster performance. The device features a 6.7-inch display and a 48-megapixel camera. Industry analysts predict the phone will sell 100 million units in the first quarter alone.
```

### Health Article
```
A groundbreaking study published in the New England Journal of Medicine found that regular exercise reduces the risk of heart disease by 30%. The research followed 50,000 participants over 10 years and found that those who exercised at least 150 minutes per week had significantly better cardiovascular health.
```

## Support

For issues:
- **Autonomy Platform**: Join Discord at https://autonomy.computer/docs/start/discord.md  
- **This App**: Check the main README.md or create an issue

## What's Next?

After deployment, you can:
- Customize the UI styling in `ui/app/page.tsx`
- Adjust agent instructions in `images/main/main.py`
- Add more MCP tools for additional capabilities
- Integrate with your own data sources
- Scale to handle more concurrent requests

Enjoy your AI-powered fact-checking system! 🎉


