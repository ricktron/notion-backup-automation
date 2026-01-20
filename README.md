# Notion Backup Automation

Automated backup solution for Notion databases with weekly scheduled runs via GitHub Actions. This tool backs up your **Captain's Log** and **Master Projects Tracker** databases to GitHub artifacts.

## Features

- 🔄 Automated weekly backups via GitHub Actions
- 📊 Exports Notion databases to CSV format
- 📦 Stores backups as GitHub artifacts (90-day retention)
- 🔔 Notifications on success/failure
- 📝 Detailed logging for troubleshooting
- 🛡️ Error handling and retry logic

## Prerequisites

- Python 3.8 or higher
- Notion account with admin access
- GitHub account (for Actions workflow)

## Setup Instructions

### 1. Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it (e.g., "Backup Integration")
4. Select the workspace containing your databases
5. Set capabilities: **Read content** (minimum required)
6. Click **Submit** and copy the **Internal Integration Token**

### 2. Share Databases with Integration

1. Open your **Captain's Log** database in Notion
2. Click the **"..."** menu (top right)
3. Select **"Add connections"**
4. Find and select your integration
5. Repeat for **Master Projects Tracker** database

### 3. Get Database IDs

Database IDs are found in the URL when you open a database:
```
https://www.notion.so/{workspace}/{database_id}?v={view_id}
```

For example:
- URL: `https://www.notion.so/myworkspace/a1b2c3d4e5f6?v=123456`
- Database ID: `a1b2c3d4e5f6` (remove dashes: `a1b2c3d4-e5f6-...` → `a1b2c3d4e5f6...`)

### 4. Configure GitHub Secrets

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add:

| Secret Name | Description | Example |
|-------------|-------------|----------|
| `NOTION_TOKEN` | Integration token from Step 1 | `secret_abc123...` |
| `CAPTAINS_LOG_DB_ID` | Database ID for Captain's Log | `a1b2c3d4e5f6...` |
| `PROJECTS_TRACKER_DB_ID` | Database ID for Master Projects Tracker | `f6e5d4c3b2a1...` |

### 5. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Enable workflows if prompted
3. The backup will run automatically every **Monday at 2:00 AM UTC**

## Local Development

### Installation

```bash
# Clone the repository
git clone https://github.com/ricktron/notion-backup-automation.git
cd notion-backup-automation

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   NOTION_TOKEN=your_integration_token_here
   CAPTAINS_LOG_DB_ID=your_captains_log_database_id
   PROJECTS_TRACKER_DB_ID=your_projects_tracker_database_id
   ```

### Running Locally

```bash
python backup_notion.py
```

Backups will be saved to the `backups/` directory with timestamps.

## GitHub Actions Workflow

The workflow (`.github/workflows/backup.yml`) runs:
- **Schedule**: Every Monday at 2:00 AM UTC
- **Manual trigger**: Via "Run workflow" button in Actions tab
- **Retention**: Backups stored as artifacts for 90 days

### Manual Trigger

1. Go to **Actions** tab
2. Select **"Notion Backup"** workflow
3. Click **"Run workflow"**
4. Select branch and click **"Run workflow"**

## Backup Storage

### GitHub Artifacts (Default)
- Backups are stored as workflow artifacts
- Retention period: 90 days
- Download from Actions → Workflow run → Artifacts section

### Alternative: Google Drive (Optional)

To use Google Drive instead:
1. Modify `backup_notion.py` to use Google Drive API
2. Add Google service account credentials as GitHub secret
3. Update workflow to include Google Drive upload step

## Notifications

The script includes basic console logging. For enhanced notifications:

### Email Notifications
Configure GitHub Actions email notifications in repository settings.

### Slack/Discord Webhooks
Add webhook URL as GitHub secret and modify script:
```python
import requests

WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
if WEBHOOK_URL:
    requests.post(WEBHOOK_URL, json={"text": "Backup completed successfully!"})
```

## Troubleshooting

### Common Issues

**"Could not find database"**
- Verify database ID is correct (remove dashes)
- Ensure database is shared with integration

**"Unauthorized"**
- Check that `NOTION_TOKEN` secret is set correctly
- Verify integration has read permissions

**"Workflow not running"**
- Ensure GitHub Actions is enabled
- Check workflow file syntax
- Verify repository has Actions enabled

### Logs

View detailed logs:
1. Go to **Actions** tab
2. Click on a workflow run
3. Expand the "Run backup script" step

## File Structure

```
notion-backup-automation/
├── .github/
│   └── workflows/
│       └── backup.yml          # GitHub Actions workflow
├── backup_notion.py            # Main backup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Security Best Practices

- ✅ Never commit `.env` file or tokens to repository
- ✅ Use GitHub Secrets for sensitive data
- ✅ Regularly rotate Notion integration tokens
- ✅ Review integration permissions periodically
- ✅ Limit integration access to only required databases

## Customization

### Change Backup Schedule

Edit `.github/workflows/backup.yml`:
```yaml
schedule:
  - cron: '0 2 * * 1'  # Monday at 2 AM UTC
  # Examples:
  # '0 0 * * *'  # Daily at midnight
  # '0 0 * * 0'  # Weekly on Sunday
  # '0 0 1 * *'  # Monthly on 1st
```

### Add More Databases

1. Share database with integration
2. Add database ID as GitHub secret
3. Update `backup_notion.py` to include new database

## License

MIT License - feel free to modify and use for your own backups.

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review workflow logs in Actions tab
3. Create an issue in this repository

## Credits

Built with:
- [notion-client](https://github.com/ramnes/notion-sdk-py) - Official Notion SDK for Python
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation

---

**Last Updated**: January 2026