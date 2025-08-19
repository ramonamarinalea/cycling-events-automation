#!/usr/bin/env python3
"""
Cycling Events and Holidays Scraper for Europe
Automatically searches and adds new events to the cycling platform
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from dataclasses import dataclass, asdict
import time
import hashlib
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('event_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CyclingEvent:
    """Data class for cycling events"""
    title: str
    description: str
    type: str  # TRAINING_CAMP, CYCLING_HOLIDAY, WEEKEND_GETAWAY, TOUR, EXPEDITION
    country: str
    start_date: datetime
    end_date: datetime
    duration: int
    region: Optional[str] = None
    city: Optional[str] = None
    venue: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "EUR"
    difficulty: str = "INTERMEDIATE"  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    terrain: List[str] = None  # ROAD, GRAVEL, MOUNTAIN, MIXED
    distance: Optional[float] = None
    elevation: Optional[float] = None
    max_participants: Optional[int] = None
    booking_url: Optional[str] = None
    website_url: Optional[str] = None
    amenities: List[str] = None
    included: List[str] = None
    not_included: List[str] = None
    languages: List[str] = None
    cover_image: Optional[str] = None
    images: List[str] = None
    source: str = "SCRAPED"
    source_url: Optional[str] = None
    
    def __post_init__(self):
        if self.terrain is None:
            self.terrain = ["ROAD"]
        if self.amenities is None:
            self.amenities = []
        if self.included is None:
            self.included = []
        if self.not_included is None:
            self.not_included = []
        if self.languages is None:
            self.languages = ["English"]
        if self.images is None:
            self.images = []
            
    def generate_slug(self) -> str:
        """Generate a unique slug for the event"""
        base_slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        base_slug = re.sub(r'[-\s]+', '-', base_slug)
        date_str = self.start_date.strftime('%Y%m%d')
        return f"{base_slug}-{date_str}"


class EventScraper:
    """Base class for event scrapers"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape(self) -> List[CyclingEvent]:
        """Override this method in subclasses"""
        raise NotImplementedError
        
    def save_to_database(self, events: List[CyclingEvent]):
        """Save events to PostgreSQL database"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        for event in events:
            try:
                # Check if event already exists
                slug = event.generate_slug()
                cur.execute("SELECT id FROM \"Event\" WHERE slug = %s", (slug,))
                
                if cur.fetchone():
                    logger.info(f"Event '{event.title}' already exists, skipping")
                    continue
                
                # Insert new event
                insert_query = """
                    INSERT INTO "Event" (
                        id, title, slug, description, type, country, region, city, venue,
                        latitude, longitude, "startDate", "endDate", duration,
                        "priceMin", "priceMax", currency, difficulty, terrain,
                        distance, elevation, "maxParticipants", "bookingUrl", "websiteUrl",
                        amenities, included, "notIncluded", languages, "coverImage", images,
                        source, "sourceUrl", verified, published, "createdAt", "updatedAt"
                    ) VALUES (
                        gen_random_uuid()::text, %s, %s, %s, %s::"EventType", %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s::"Difficulty", %s::"Terrain"[],
                        %s, %s, %s, %s, %s, %s::text[], %s::text[], %s::text[], 
                        %s::text[], %s, %s::text[], %s::"EventSource", %s, false, true, NOW(), NOW()
                    )
                """
                
                cur.execute(insert_query, (
                    event.title, slug, event.description, event.type,
                    event.country, event.region, event.city, event.venue,
                    event.latitude, event.longitude, event.start_date, event.end_date,
                    event.duration, event.price_min, event.price_max, event.currency,
                    event.difficulty, event.terrain, event.distance, event.elevation,
                    event.max_participants, event.booking_url, event.website_url,
                    event.amenities, event.included, event.not_included,
                    event.languages, event.cover_image, event.images,
                    event.source, event.source_url
                ))
                
                conn.commit()
                logger.info(f"Successfully added event: {event.title}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Error saving event '{event.title}': {e}")
                
        cur.close()
        conn.close()


class AlpenbrevetScraper(EventScraper):
    """Scraper for Alpenbrevet cycling events"""
    
    def scrape(self) -> List[CyclingEvent]:
        events = []
        try:
            # This is a placeholder - would need actual scraping logic
            # based on the website structure
            logger.info("Scraping Alpenbrevet events...")
            
            # Example event (would be scraped from actual website)
            event = CyclingEvent(
                title="Alpenbrevet 2025",
                description="The classic alpine cycling challenge through Swiss mountain passes",
                type="TOUR",
                country="Switzerland",
                region="Alps",
                city="Andermatt",
                start_date=datetime(2025, 8, 30),
                end_date=datetime(2025, 8, 31),
                duration=2,
                difficulty="EXPERT",
                terrain=["ROAD"],
                distance=270,
                elevation=7000,
                website_url="https://alpenbrevet.ch",
                source_url="https://alpenbrevet.ch",
                languages=["German", "English", "French"]
            )
            events.append(event)
            
        except Exception as e:
            logger.error(f"Error scraping Alpenbrevet: {e}")
            
        return events


class RideGravelScraper(EventScraper):
    """Scraper for RideGravel.ch events"""
    
    def scrape(self) -> List[CyclingEvent]:
        events = []
        try:
            logger.info("Scraping RideGravel.ch events...")
            
            # Example gravel events (would be scraped from actual website)
            sample_events = [
                {
                    "title": "Swiss Gravel Challenge",
                    "description": "Epic gravel adventure through Swiss countryside",
                    "type": "TOUR",
                    "country": "Switzerland",
                    "region": "Central Switzerland",
                    "start_date": datetime(2025, 6, 15),
                    "end_date": datetime(2025, 6, 16),
                    "duration": 2,
                    "difficulty": "ADVANCED",
                    "terrain": ["GRAVEL", "MIXED"],
                    "distance": 150,
                    "elevation": 3000,
                    "website_url": "https://ridegravel.ch",
                    "source_url": "https://ridegravel.ch"
                },
                {
                    "title": "Gravel Explorer Weekend",
                    "description": "Weekend gravel exploration for all levels",
                    "type": "WEEKEND_GETAWAY",
                    "country": "Switzerland",
                    "region": "Valais",
                    "start_date": datetime(2025, 7, 20),
                    "end_date": datetime(2025, 7, 21),
                    "duration": 2,
                    "difficulty": "INTERMEDIATE",
                    "terrain": ["GRAVEL"],
                    "distance": 100,
                    "elevation": 2000,
                    "website_url": "https://ridegravel.ch",
                    "source_url": "https://ridegravel.ch"
                }
            ]
            
            for event_data in sample_events:
                event = CyclingEvent(**event_data)
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error scraping RideGravel: {e}")
            
        return events


class EuropeanHolidaysFetcher:
    """Fetches public holidays for European countries"""
    
    def __init__(self):
        self.api_base = "https://date.nager.at/api/v3"
        self.cycling_relevant_countries = [
            'AT', 'BE', 'CH', 'DE', 'DK', 'ES', 'FR', 'GB', 'IT', 'NL', 
            'NO', 'PT', 'SE', 'CZ', 'PL', 'HR', 'SI', 'GR'
        ]
        
    def fetch_holidays(self, year: int) -> List[Dict]:
        """Fetch holidays for all cycling-relevant European countries"""
        all_holidays = []
        
        for country_code in self.cycling_relevant_countries:
            try:
                url = f"{self.api_base}/publicholidays/{year}/{country_code}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    holidays = response.json()
                    for holiday in holidays:
                        holiday['countryCode'] = country_code
                        all_holidays.append(holiday)
                    logger.info(f"Fetched {len(holidays)} holidays for {country_code}")
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching holidays for {country_code}: {e}")
                
        return all_holidays
    
    def create_holiday_events(self, holidays: List[Dict]) -> List[CyclingEvent]:
        """Convert holidays into cycling holiday events"""
        events = []
        country_names = {
            'AT': 'Austria', 'BE': 'Belgium', 'CH': 'Switzerland',
            'DE': 'Germany', 'DK': 'Denmark', 'ES': 'Spain',
            'FR': 'France', 'GB': 'United Kingdom', 'IT': 'Italy',
            'NL': 'Netherlands', 'NO': 'Norway', 'PT': 'Portugal',
            'SE': 'Sweden', 'CZ': 'Czech Republic', 'PL': 'Poland',
            'HR': 'Croatia', 'SI': 'Slovenia', 'GR': 'Greece'
        }
        
        for holiday in holidays:
            try:
                # Create long weekend events for holidays
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
                
                # Check if it creates a long weekend
                if holiday_date.weekday() in [0, 4]:  # Monday or Friday
                    if holiday_date.weekday() == 0:  # Monday
                        start_date = holiday_date - timedelta(days=2)
                        end_date = holiday_date
                    else:  # Friday
                        start_date = holiday_date
                        end_date = holiday_date + timedelta(days=2)
                    
                    country = country_names.get(holiday['countryCode'], holiday['countryCode'])
                    
                    event = CyclingEvent(
                        title=f"{holiday['localName']} Cycling Weekend - {country}",
                        description=f"Special cycling weekend during {holiday['name']} holiday. "
                                  f"Perfect time for a cycling getaway in {country}.",
                        type="WEEKEND_GETAWAY",
                        country=country,
                        start_date=start_date,
                        end_date=end_date,
                        duration=3,
                        difficulty="INTERMEDIATE",
                        terrain=["ROAD", "MIXED"],
                        source="API",
                        source_url="https://date.nager.at"
                    )
                    events.append(event)
                    
            except Exception as e:
                logger.error(f"Error creating holiday event: {e}")
                
        return events


class CyclingEventAutomation:
    """Main automation class"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        self.scrapers = [
            AlpenbrevetScraper(self.database_url),
            RideGravelScraper(self.database_url)
        ]
        self.holiday_fetcher = EuropeanHolidaysFetcher()
        
    def run(self):
        """Run the complete automation"""
        logger.info("Starting cycling event automation...")
        
        all_events = []
        
        # Scrape events from various sources
        for scraper in self.scrapers:
            try:
                events = scraper.scrape()
                all_events.extend(events)
                logger.info(f"Scraped {len(events)} events from {scraper.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error with {scraper.__class__.__name__}: {e}")
        
        # Fetch and create holiday events
        try:
            current_year = datetime.now().year
            holidays = self.holiday_fetcher.fetch_holidays(current_year)
            holiday_events = self.holiday_fetcher.create_holiday_events(holidays)
            all_events.extend(holiday_events)
            logger.info(f"Created {len(holiday_events)} holiday events")
        except Exception as e:
            logger.error(f"Error fetching holidays: {e}")
        
        # Save all events to database
        if all_events:
            logger.info(f"Saving {len(all_events)} events to database...")
            scraper = EventScraper(self.database_url)
            scraper.save_to_database(all_events)
            
        logger.info("Automation complete!")
        return len(all_events)


if __name__ == "__main__":
    automation = CyclingEventAutomation()
    events_added = automation.run()
    print(f"Successfully processed {events_added} events")