# Cycling Events Automation

Automated system for discovering and adding cycling events and holidays across Europe to your cycling events platform on Vercel.

## Features

- **Multi-Source Event Scraping**: Automatically scrapes cycling events from multiple sources including:
  - Alpenbrevet
  - RideGravel.ch
  - MySwitzerland.com
  - Kudos Cycling
  - SunVelo
  - GroupRides.cc
  - Bikepacking.com

- **European Holiday Integration**: Fetches public holidays for 18+ European countries and creates cycling weekend suggestions

- **Automatic Database Updates**: Directly integrates with your PostgreSQL database on Vercel

- **Duplicate Prevention**: Checks for existing events before adding

- **Flexible Scheduling**: Can run on-demand or scheduled (daily/weekly)

## Setup

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database (from your Vercel project)
- Git

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd cycling-events-automation

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
```

### 3. Configuration

Edit `.env` file with your database credentials:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

Get your DATABASE_URL from:
1. Go to your Vercel Dashboard
2. Select your cycling-events-platform project
3. Go to Storage tab
4. Click on your database
5. Copy the connection string from `.env.local` tab

### 4. Running the Automation

#### Manual Run (One-time)
```bash
python event_scraper.py
```

#### Scheduled Run (Continuous)
```bash
python scheduler.py
```

This will:
- Run immediately on startup
- Run daily at 3 AM
- Run comprehensive update every Sunday at 2 AM

### 5. GitHub Actions (Automated)

The automation can run automatically via GitHub Actions:

1. Add your DATABASE_URL to GitHub Secrets:
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `DATABASE_URL`
   - Value: Your PostgreSQL connection string

2. The workflow will run:
   - Daily at 3 AM UTC
   - On manual trigger from Actions tab

## Event Sources

### Currently Implemented

1. **Alpenbrevet** - Classic Swiss cycling challenges
2. **RideGravel.ch** - Swiss gravel events
3. **European Holidays** - Public holidays from 18 countries
4. **MySwitzerland** - Swiss tourism cycling events
5. **Kudos Cycling** - Training camps and holidays
6. **SunVelo** - Sunny cycling destinations
7. **GroupRides.cc** - Community organized rides
8. **Bikepacking.com** - Bikepacking adventures

### Adding New Sources

To add a new event source, create a new scraper class in `advanced_scrapers.py`:

```python
class YourSourceScraper(EventScraper):
    def scrape(self) -> List[CyclingEvent]:
        events = []
        # Your scraping logic here
        return events
```

## Event Types

- `TRAINING_CAMP` - Professional training camps
- `CYCLING_HOLIDAY` - Leisure cycling holidays
- `WEEKEND_GETAWAY` - Short weekend trips
- `TOUR` - Multi-day tours
- `EXPEDITION` - Adventure/bikepacking expeditions

## Monitoring

Check the logs for scraping status:
- `event_scraper.log` - Main scraping activities
- `scheduler.log` - Scheduling information

## Troubleshooting

### Database Connection Issues
- Verify your DATABASE_URL is correct
- Check if your IP is whitelisted in Vercel/Neon dashboard
- Ensure SSL mode is set to `require`

### No Events Added
- Check if events already exist (duplicates are skipped)
- Review logs for scraping errors
- Verify date ranges are in the future

### Scheduling Not Working
- Ensure the scheduler process stays running
- Consider using systemd service (Linux) or launchd (macOS) for production
- Check GitHub Actions workflow status

## Production Deployment

For production use, consider:

1. **Using GitHub Actions** (recommended)
   - Already configured in `.github/workflows/scrape-events.yml`
   - Runs automatically on schedule
   - No server required

2. **Deploy to a VPS**
   ```bash
   # Use systemd service (Linux)
   sudo cp cycling-events.service /etc/systemd/system/
   sudo systemctl enable cycling-events
   sudo systemctl start cycling-events
   ```

3. **Use a Platform Service**
   - Deploy to Heroku with Scheduler add-on
   - Use AWS Lambda with CloudWatch Events
   - Deploy to Google Cloud Functions with Cloud Scheduler

## Contributing

To add more event sources or improve existing scrapers:

1. Add your scraper class to `advanced_scrapers.py`
2. Follow the `CyclingEvent` data structure
3. Handle errors gracefully
4. Add appropriate logging
5. Test locally before deploying

## License

MIT