import time
import requests
import pandas as pd
import json
import random
from threading import Thread
import urllib3
from tqdm import tqdm
import os
from datetime import datetime, timedelta
import logging
from playwright.sync_api import sync_playwright
import re
from typing import Dict, List, Optional, Any
import warnings
import hashlib

warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(
    filename='planning_applications_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Suppress warnings from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
BATCH_SIZE = 100  # Process applications in batches
SAVE_INTERVAL = 50  # Save data more frequently
CHECKPOINT_FILE = 'planning_checkpoint.json'
TEMP_DATA_FILE = 'planning_data_temp.json'
SKIPPED_AREAS_FILE = 'planning_skipped_areas.txt'
STATUS_HISTORY_FILE = 'planning_status_history.json'
APPLICATIONS_INDEX_FILE = 'planning_applications_index.json'

# Complete list of 425 UK Planning Authorities
# Source: https://www.planit.org.uk/find/areas/?area_type=active
# Extracted: 2025-09-18 (all 425 active planning authorities)
UK_PLANNING_AUTHORITIES = [
    "Aberdeen", "Aberdeenshire", "Adur and Worthing", "Alderney", "Allerdale", "Amber Valley",
    "Anglesey", "Angus", "Antrim and Newtownabbey", "Ards and North Down", "Argyll",
    "Armagh Banbridge Craigavon", "Arun", "Ashfield", "Ashford", "Aylesbury Vale", "BCP",
    "Babergh Mid Suffolk", "Barking and Dagenham", "Barnet", "Barnsley", "Barrow", "Basildon",
    "Basingstoke", "Bassetlaw", "Bath", "Bedford", "Belfast", "Bexley", "Birmingham", "Blaby",
    "Blackburn", "Blackpool", "Blaenau Gwent", "Bolsover", "Bolton", "Boston", "Bracknell",
    "Bradford", "Braintree", "Breckland", "Brecon Beacons", "Brent", "Brentwood", "Bridgend",
    "Brighton", "Bristol", "Broads", "Bromley", "Bromsgrove Redditch", "Broxbourne", "Broxtowe",
    "Buckinghamshire", "Burnley", "Bury", "Caerphilly", "Cairngorms", "Calderdale", "Cambridge",
    "Cambridgeshire", "Camden", "Cannock Chase", "Canterbury", "Cardiff", "Carlisle",
    "Carmarthenshire", "Castle Point", "Causeway and Glens", "Central Bedfordshire", "Ceredigion",
    "Charnwood", "Chelmsford", "Cheltenham", "Cherwell", "Cheshire East", "Chester", "Chesterfield",
    "Chichester", "Chiltern South Bucks", "Chorley", "City", "Clackmannanshire", "Colchester",
    "Conwy", "Copeland", "Corby", "Cornwall", "Cotswold", "Coventry", "Craven", "Crawley",
    "Croydon", "Cumbria", "Dacorum", "Darlington", "Dartford", "Dartmoor", "Denbighshire",
    "Derby", "Derbyshire", "Derbyshire Dales", "Derry and Strabane", "Devon", "DNS Wales",
    "Doncaster", "Dorset", "Dover", "Dudley", "Dumfries", "Dundee", "Durham", "Ealing",
    "East Ayrshire", "Eastbourne", "East Cambridgeshire", "East Devon", "East Dunbartonshire",
    "East Hampshire", "East Hertfordshire", "Eastleigh", "East Lindsey", "East Lothian",
    "East Northamptonshire", "East Renfrewshire", "East Riding", "East Staffordshire",
    "East Suffolk", "East Sussex", "Edinburgh", "Elmbridge", "Energy Consents Unit", "Enfield",
    "Epping Forest", "Epsom and Ewell", "Erewash", "Essex", "Exeter", "Exmoor", "Falkirk",
    "Fareham", "Fenland", "Fermanagh and Omagh", "Fife", "Flintshire", "Forest of Dean",
    "Fylde", "Gateshead", "Gedling", "Glamorgan", "Glasgow", "Gloucester", "Gloucestershire",
    "Gosport", "Gravesham", "Great Yarmouth", "Greenwich", "Guernsey", "Guildford", "Gwynedd",
    "Hackney", "Halton", "Hambleton", "Hammersmith and Fulham", "Hampshire", "Harborough",
    "Haringey", "Harlow", "Harrogate", "Harrow", "Hart", "Hartlepool", "Hastings", "Havant",
    "Havering", "Herefordshire", "Hertfordshire", "Hertsmere", "Highland", "High Peak",
    "Hillingdon", "Hinckley and Bosworth", "Horsham", "Hounslow", "Hull", "Huntingdonshire",
    "Hyndburn", "Inverclyde", "Ipswich", "Isle of Man", "Isle of Wight", "Islington", "Jersey",
    "Kensington", "Kent", "Kettering", "Kings Lynn", "Kingston", "Kirklees", "Knowsley",
    "Lake District", "Lambeth", "Lancashire", "Lancaster", "Leeds", "Leicester", "Leicestershire",
    "Lewes", "Lewisham", "Lichfield", "Lincoln", "Lincolnshire", "Lisburn and Castlereagh",
    "Liverpool", "Loch Lomond", "London Legacy", "Luton", "Maldon", "Malvern Hills", "Manchester",
    "Mansfield", "Medway", "Melton", "Mendip", "Merthyr Tydfil", "Merton", "Mid Devon",
    "Middlesbrough", "Mid East Antrim", "Mid Kent", "Midlothian", "Mid Sussex", "Mid Ulster",
    "Milton Keynes", "Mole Valley", "Monmouthshire", "Moray", "Neath", "Newark and Sherwood",
    "Newcastle under Lyme", "Newcastle upon Tyne", "New Forest (District)", "New Forest (Park)",
    "Newham", "Newport", "Newry Mourne Down", "NI Strategic Planning", "Norfolk", "North Ayrshire",
    "North Devon", "North East Derbyshire", "North East Lincs", "North Hertfordshire",
    "North Kesteven", "North Lanarkshire", "North Lincs", "North Norfolk", "North Northamptonshire",
    "North Somerset", "North Tyneside", "Northumberland (County)", "Northumberland (Park)",
    "North Warwickshire", "North West Leicestershire", "North York Moors", "North Yorkshire",
    "Norwich", "Nottingham", "Nottinghamshire", "NSIP England", "NSIP Wales", "Nuneaton",
    "Oadby and Wigston", "Oldham", "Old Oak Park Royal", "Orkney", "Oxford", "Oxfordshire",
    "Peak District", "Pembroke Coast", "Pembrokeshire", "Pendle", "Perth", "Peterborough",
    "Plymouth", "Portsmouth", "Powys", "Preston", "Reading", "Redbridge", "Redcar and Cleveland",
    "Reigate", "Renfrewshire", "Rhondda", "Ribble Valley", "Richmond", "Richmondshire", "Rochdale",
    "Rochford", "Rossendale", "Rother", "Rotherham", "Rugby", "Runnymede", "Rushcliffe",
    "Rushmoor", "Rutland", "Ryedale", "Salford", "Sandwell", "Scarborough", "Scilly Isles",
    "Scottish Borders", "Sedgemoor", "Sefton", "Selby", "Sevenoaks", "Sheffield", "Shepway",
    "Shetlands", "Shropshire", "Slough", "Snowdonia", "Solihull", "Somerset", "Southampton",
    "South Ayrshire", "South Cambridgeshire", "South Derbyshire", "South Downs", "Southend",
    "South Gloucestershire", "South Holland", "South Kesteven", "South Lanarkshire",
    "South Norfolk Broadland", "South Oxfordshire", "South Ribble", "South Somerset",
    "South Staffordshire", "South Tyneside", "Southwark", "South West Devon", "Spelthorne",
    "Stafford", "Staffordshire", "Staffordshire Moorlands", "St Albans", "Stevenage", "St Helens",
    "Stirling", "Stockport", "Stockton-on-Tees", "Stoke on Trent", "Stratford on Avon", "Stroud",
    "Suffolk", "Sunderland", "Surrey", "Surrey Heath", "Sutton", "Swansea", "Swindon", "Tameside",
    "Tamworth", "Tandridge", "Taunton Deane", "Teignbridge", "Telford", "Tendring", "Test Valley",
    "Tewkesbury", "Thanet", "Three Rivers", "Thurrock", "Tonbridge", "Torbay", "Torfaen",
    "Torridge", "Tower Hamlets", "Trafford", "Tunbridge Wells", "Uttlesford", "Vale of White Horse",
    "Wakefield", "Walsall", "Waltham Forest", "Wandsworth", "Warrington", "Warwick", "Warwickshire",
    "Watford", "Waverley", "Wealden", "Wellingborough", "Welwyn Hatfield", "West Berkshire",
    "West Dunbartonshire", "Western Isles", "West Lancashire", "West Lindsey", "West Lothian",
    "Westminster", "Westmorland and Furness", "West Northamptonshire", "West Oxfordshire",
    "West Somerset", "West Suffolk", "West Sussex", "Wigan", "Wiltshire", "Winchester", "Windsor",
    "Wirral", "Woking", "Wokingham", "Wolverhampton", "Worcester", "Worcestershire", "Wrexham",
    "Wychavon", "Wycombe", "Wyre", "Wyre Forest", "York", "Yorkshire Dales"
]

class PlanningApplicationsScraper:
    def __init__(self):
        self.all_data = []
        self.processed_authorities = []
        self.failed_authorities = []
        self.start_time = time.time()
        
        # Status tracking
        self.applications_index = {}  # uid -> application data
        self.status_history = {}  # uid -> list of status changes
        self.updated_applications = []  # Track applications with changes
        self.new_applications = []  # Track genuinely new applications
        
        # User agents for stealth
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Proxies (if needed)
        self.proxies = {
            'http': 'http://cxmzvqtw-rotate:zgp8h079llzg@p.webshare.io:80',
            'https': 'http://cxmzvqtw-rotate:zgp8h079llzg@p.webshare.io:80',
        }
        
        # Load previous progress and indices
        self.load_checkpoint()
        self.load_temp_data()
        self.load_applications_index()
        self.load_status_history()

    def generate_application_hash(self, app_data: Dict) -> str:
        """Generate a hash for application data to detect changes"""
        # Create a hash based on key fields that might change
        hash_fields = {
            'app_state': app_data.get('app_state', ''),
            'description': app_data.get('description', ''),
            'decided_date': app_data.get('decided_date', ''),
            'consulted_date': app_data.get('consulted_date', ''),
        }
        
        # Include other_fields that might change
        if app_data.get('other_fields'):
            other_fields = app_data['other_fields']
            hash_fields.update({
                'status': other_fields.get('status', ''),
                'target_decision_date': other_fields.get('target_decision_date', ''),
                'comment_date': other_fields.get('comment_date', ''),
            })
        
        hash_string = json.dumps(hash_fields, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def load_applications_index(self):
        """Load the applications index from previous runs"""
        if os.path.exists(APPLICATIONS_INDEX_FILE):
            try:
                with open(APPLICATIONS_INDEX_FILE, 'r') as f:
                    self.applications_index = json.load(f)
                    logging.info(f"Loaded {len(self.applications_index)} applications from index")
            except Exception as e:
                logging.error(f"Error loading applications index: {e}")
                self.applications_index = {}

    def load_status_history(self):
        """Load status history from previous runs"""
        if os.path.exists(STATUS_HISTORY_FILE):
            try:
                with open(STATUS_HISTORY_FILE, 'r') as f:
                    self.status_history = json.load(f)
                    logging.info(f"Loaded status history for {len(self.status_history)} applications")
            except Exception as e:
                logging.error(f"Error loading status history: {e}")
                self.status_history = {}

    def save_applications_index(self):
        """Save the applications index"""
        try:
            with open(APPLICATIONS_INDEX_FILE, 'w') as f:
                json.dump(self.applications_index, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving applications index: {e}")

    def save_status_history(self):
        """Save status history"""
        try:
            with open(STATUS_HISTORY_FILE, 'w') as f:
                json.dump(self.status_history, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving status history: {e}")

    def track_status_change(self, uid: str, old_status: str, new_status: str, application_data: Dict):
        """Track a status change for an application"""
        if uid not in self.status_history:
            self.status_history[uid] = []
        
        status_change = {
            'timestamp': datetime.now().isoformat(),
            'old_status': old_status,
            'new_status': new_status,
            'old_app_state': application_data.get('previous_app_state'),
            'new_app_state': application_data.get('app_state'),
            'scraper_run': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        self.status_history[uid].append(status_change)
        logging.info(f"Status change tracked for {uid}: {old_status} -> {new_status}")

    def detect_application_changes(self, new_app: Dict) -> Dict:
        """Detect if an application has changed and what type of change it is"""
        uid = new_app.get('uid')
        if not uid:
            return {'type': 'new', 'changes': []}
        
        existing_app = self.applications_index.get(uid)
        if not existing_app:
            return {'type': 'new', 'changes': []}
        
        # Generate hashes to detect changes
        old_hash = existing_app.get('content_hash', '')
        new_hash = self.generate_application_hash(new_app)
        
        if old_hash == new_hash:
            return {'type': 'unchanged', 'changes': []}
        
        # Detect specific changes
        changes = []
        
        # Check status changes
        old_status = existing_app.get('app_state', '')
        new_status = new_app.get('app_state', '')
        if old_status != new_status:
            changes.append({
                'field': 'app_state',
                'old_value': old_status,
                'new_value': new_status,
                'change_type': 'status_change'
            })
        
        # Check decision date changes
        old_decided = existing_app.get('decided_date')
        new_decided = new_app.get('decided_date')
        if old_decided != new_decided:
            changes.append({
                'field': 'decided_date',
                'old_value': old_decided,
                'new_value': new_decided,
                'change_type': 'decision_date_update'
            })
        
        # Check other significant fields
        significant_fields = ['description', 'consulted_date']
        for field in significant_fields:
            if existing_app.get(field) != new_app.get(field):
                changes.append({
                    'field': field,
                    'old_value': existing_app.get(field),
                    'new_value': new_app.get(field),
                    'change_type': 'field_update'
                })
        
        # Check other_fields for changes
        if existing_app.get('other_fields') and new_app.get('other_fields'):
            old_other = existing_app['other_fields']
            new_other = new_app['other_fields']
            
            important_other_fields = ['status', 'target_decision_date', 'comment_date']
            for field in important_other_fields:
                if old_other.get(field) != new_other.get(field):
                    changes.append({
                        'field': f'other_fields.{field}',
                        'old_value': old_other.get(field),
                        'new_value': new_other.get(field),
                        'change_type': 'other_field_update'
                    })
        
        return {
            'type': 'updated' if changes else 'unchanged',
            'changes': changes
        }

    def update_application_index(self, application: Dict, change_info: Dict):
        """Update the application in the index"""
        uid = application.get('uid')
        if not uid:
            return
        
        # Store previous state for tracking
        existing_app = self.applications_index.get(uid, {})
        application['previous_app_state'] = existing_app.get('app_state')
        
        # Add metadata
        application['content_hash'] = self.generate_application_hash(application)
        application['last_updated'] = datetime.now().isoformat()
        application['change_info'] = change_info
        
        # Track status changes
        if change_info['type'] == 'updated':
            for change in change_info['changes']:
                if change['change_type'] == 'status_change':
                    self.track_status_change(
                        uid, 
                        change['old_value'], 
                        change['new_value'], 
                        application
                    )
        
        # Update the index
        self.applications_index[uid] = application
        
        # Add to appropriate tracking lists
        if change_info['type'] == 'new':
            self.new_applications.append(application)
            logging.info(f"New application: {uid}")
        elif change_info['type'] == 'updated':
            self.updated_applications.append(application)
            logging.info(f"Updated application: {uid} - {len(change_info['changes'])} changes")

    def save_checkpoint(self):
        """Save current progress to checkpoint files"""
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'processed_authorities': self.processed_authorities,
                'failed_authorities': self.failed_authorities,
                'timestamp': datetime.now().isoformat(),
                'new_applications_count': len(self.new_applications),
                'updated_applications_count': len(self.updated_applications)
            }, f)
        
        # Update temp data file
        with open(TEMP_DATA_FILE, 'w') as f:
            json.dump(self.all_data, f, indent=2)
        
        # Save indices
        self.save_applications_index()
        self.save_status_history()

    def load_checkpoint(self):
        """Load processed authorities from checkpoint"""
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, 'r') as f:
                    data = json.load(f)
                    self.processed_authorities = data.get('processed_authorities', [])
                    self.failed_authorities = data.get('failed_authorities', [])
                    logging.info(f"Loaded checkpoint: {len(self.processed_authorities)} processed, {len(self.failed_authorities)} failed")
            except Exception as e:
                logging.error(f"Error loading checkpoint: {e}")

    def load_temp_data(self):
        """Load temporary data from previous runs"""
        if os.path.exists(TEMP_DATA_FILE):
            try:
                with open(TEMP_DATA_FILE, 'r') as f:
                    self.all_data = json.load(f)
                    logging.info(f"Loaded {len(self.all_data)} existing records")
            except Exception as e:
                logging.error(f"Error loading temp data: {e}")

    def get_planit_search_url(self, authority: str, days_back: int = 14) -> str:
        """Generate planit.org.uk search URL for recent applications"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for the API
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # planit.org.uk API endpoint
        base_url = "https://www.planit.org.uk/api/applics/"
        params = {
            'authority': authority.lower().replace(' ', '_'),
            'start_date': start_str,
            'end_date': end_str,
            'limit': 100,
            'offset': 0
        }
        
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return url

    def scrape_planit_with_playwright(self, authority: str) -> List[Dict]:
        """Scrape planning applications using Playwright for stealth"""
        applications = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with stealth settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',
                        '--disable-javascript',
                        '--user-agent=' + random.choice(self.user_agents)
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice(self.user_agents)
                )
                
                page = context.new_page()
                
                # Set additional headers
                page.set_extra_http_headers({
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                })
                
                # Navigate to planit search page
                search_url = f"https://www.planit.org.uk/find/applications/{authority.lower().replace(' ', '_')}"
                
                try:
                    response = page.goto(search_url, wait_until='networkidle', timeout=30000)
                    
                    if response and response.status == 200:
                        # Wait for content to load
                        page.wait_for_selector('[data-testid="application-card"], .application-item, .planning-application', timeout=10000)
                        
                        # Extract applications data
                        applications_data = page.evaluate("""
                            () => {
                                const apps = [];
                                const cards = document.querySelectorAll('[data-testid="application-card"], .application-item, .planning-application');
                                
                                cards.forEach(card => {
                                    const app = {};
                                    
                                    // Extract basic information
                                    const addressEl = card.querySelector('.address, [data-testid="address"]');
                                    if (addressEl) app.address = addressEl.textContent.trim();
                                    
                                    const refEl = card.querySelector('.reference, [data-testid="reference"]');
                                    if (refEl) app.reference = refEl.textContent.trim();
                                    
                                    const descEl = card.querySelector('.description, [data-testid="description"]');
                                    if (descEl) app.description = descEl.textContent.trim();
                                    
                                    const statusEl = card.querySelector('.status, [data-testid="status"]');
                                    if (statusEl) app.app_state = statusEl.textContent.trim();
                                    
                                    const typeEl = card.querySelector('.type, [data-testid="type"]');
                                    if (typeEl) app.app_type = typeEl.textContent.trim();
                                    
                                    const linkEl = card.querySelector('a[href]');
                                    if (linkEl) app.link = linkEl.href;
                                    
                                    // Extract dates
                                    const dateElements = card.querySelectorAll('.date, [data-testid*="date"]');
                                    dateElements.forEach(dateEl => {
                                        const text = dateEl.textContent.toLowerCase();
                                        if (text.includes('received') || text.includes('submitted')) {
                                            app.start_date = dateEl.textContent.match(/\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\/\\d{1,2}\/\\d{4}/)?.[0];
                                        }
                                        if (text.includes('decided') || text.includes('decision')) {
                                            app.decided_date = dateEl.textContent.match(/\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\/\\d{1,2}\/\\d{4}/)?.[0];
                                        }
                                    });
                                    
                                    if (app.address || app.reference) {
                                        apps.push(app);
                                    }
                                });
                                
                                return apps;
                            }
                        """)
                        
                        # Process each application to get full details and track changes
                        for app_data in applications_data:
                            try:
                                full_app = self.enrich_application_data(page, app_data, authority)
                                if full_app:
                                    # Detect changes
                                    change_info = self.detect_application_changes(full_app)
                                    
                                    # Update application index
                                    self.update_application_index(full_app, change_info)
                                    
                                    # Only add to results if it's new or updated
                                    if change_info['type'] in ['new', 'updated']:
                                        applications.append(full_app)
                                    
                            except Exception as e:
                                logging.warning(f"Error enriching application data: {e}")
                                continue
                    
                except Exception as e:
                    logging.error(f"Error navigating to {search_url}: {e}")
                
                finally:
                    browser.close()
                    
        except Exception as e:
            logging.error(f"Playwright error for {authority}: {e}")
        
        return applications

    def enrich_application_data(self, page, basic_data: Dict, authority: str) -> Dict:
        """Enrich application data with additional details"""
        try:
            # Create the full application structure
            application = {
                "address": basic_data.get('address', ''),
                "altid": None,
                "app_size": self.determine_app_size(basic_data.get('description', '')),
                "app_state": self.normalize_app_state(basic_data.get('app_state', 'Undecided')),
                "app_type": basic_data.get('app_type', 'Unknown'),
                "area_id": self.get_area_id(authority),
                "area_name": authority,
                "associated_id": None,
                "consulted_date": None,
                "decided_date": self.parse_date(basic_data.get('decided_date')),
                "description": basic_data.get('description', ''),
                "last_changed": datetime.now().isoformat(),
                "last_different": datetime.now().isoformat(),
                "last_scraped": datetime.now().isoformat(),
                "link": basic_data.get('link', ''),
                "location": None,
                "location_x": None,
                "location_y": None,
                "name": f"{authority}/{basic_data.get('reference', 'Unknown')}",
                "other_fields": {},
                "postcode": self.extract_postcode(basic_data.get('address', '')),
                "reference": basic_data.get('reference'),
                "scraper_name": authority,
                "start_date": self.parse_date(basic_data.get('start_date')),
                "uid": basic_data.get('reference', f"unknown_{int(time.time())}"),
                "url": basic_data.get('link', '')
            }
            
            # Try to get additional details if link is available
            if basic_data.get('link'):
                try:
                    additional_data = self.scrape_application_details(page, basic_data['link'])
                    if additional_data:
                        application['other_fields'].update(additional_data)
                except Exception as e:
                    logging.warning(f"Error getting additional details: {e}")
            
            return application
            
        except Exception as e:
            logging.error(f"Error enriching application data: {e}")
            return None

    def scrape_application_details(self, page, detail_url: str) -> Dict:
        """Scrape additional details from application detail page"""
        try:
            response = page.goto(detail_url, wait_until='networkidle', timeout=15000)
            
            if response and response.status == 200:
                details = page.evaluate("""
                    () => {
                        const data = {};
                        
                        // Look for common field patterns
                        const fieldMappings = {
                            'applicant': ['applicant_name', 'applicant'],
                            'agent': ['agent_name', 'agent_company', 'agent_address'],
                            'case officer': ['case_officer'],
                            'ward': ['ward_name'],
                            'parish': ['parish'],
                            'easting': ['easting'],
                            'northing': ['northing'],
                            'documents': ['n_documents', 'docs_url'],
                            'consultation': ['comment_date', 'comment_url'],
                            'target decision': ['target_decision_date'],
                            'status': ['status'],
                            'application type': ['application_type']
                        };
                        
                        // Extract data from various selectors
                        document.querySelectorAll('tr, .field, .detail-row, dt, dd').forEach(el => {
                            const text = el.textContent.toLowerCase().trim();
                            const value = el.textContent.trim();
                            
                            Object.keys(fieldMappings).forEach(key => {
                                if (text.includes(key)) {
                                    const nextEl = el.nextElementSibling;
                                    if (nextEl) {
                                        const nextValue = nextEl.textContent.trim();
                                        if (nextValue && nextValue !== value) {
                                            fieldMappings[key].forEach(field => {
                                                data[field] = nextValue;
                                            });
                                        }
                                    }
                                }
                            });
                        });
                        
                        // Extract coordinates if available
                        const coordinateElements = document.querySelectorAll('script, [data-lat], [data-lng]');
                        coordinateElements.forEach(el => {
                            const content = el.textContent || el.outerHTML;
                            const latMatch = content.match(/lat['":\\s]*([\\-\\d\\.]+)/i);
                            const lngMatch = content.match(/lng['":\\s]*([\\-\\d\\.]+)|lon['":\\s]*([\\-\\d\\.]+)/i);
                            
                            if (latMatch) data.lat = parseFloat(latMatch[1]);
                            if (lngMatch) data.lng = parseFloat(lngMatch[1] || lngMatch[2]);
                        });
                        
                        return data;
                    }
                """)
                
                return details
                
        except Exception as e:
            logging.warning(f"Error scraping application details from {detail_url}: {e}")
        
        return {}

    def determine_app_size(self, description: str) -> str:
        """Determine application size based on description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['extension', 'single', 'minor', 'small']):
            return "Small"
        elif any(word in description_lower for word in ['new build', 'construction', 'development', 'major']):
            return "Large"
        else:
            return "Medium"

    def normalize_app_state(self, state: str) -> str:
        """Normalize application state"""
        state_lower = state.lower().strip()
        
        if 'approved' in state_lower or 'granted' in state_lower:
            return "Approved"
        elif 'refused' in state_lower or 'rejected' in state_lower:
            return "Refused"
        elif 'withdrawn' in state_lower:
            return "Withdrawn"
        elif 'pending' in state_lower or 'under' in state_lower:
            return "Undecided"
        else:
            return "Undecided"

    def get_area_id(self, authority: str) -> int:
        """Get area ID for authority (hash-based for consistency)"""
        return hash(authority.lower()) % 10000

    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse and normalize date string"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    parsed = datetime.strptime(date_str.strip(), fmt)
                    return parsed.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None

    def extract_postcode(self, address: str) -> Optional[str]:
        """Extract UK postcode from address"""
        if not address:
            return None
        
        # UK postcode pattern
        postcode_pattern = r'[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][ABD-HJLNP-UW-Z]{2}'
        match = re.search(postcode_pattern, address.upper())
        
        return match.group(0) if match else None

    def scrape_authority(self, authority: str) -> List[Dict]:
        """Scrape planning applications for a single authority"""
        logging.info(f"Starting scrape for {authority}")
        
        try:
            applications = self.scrape_planit_with_playwright(authority)
            
            if applications:
                logging.info(f"Successfully scraped {len(applications)} applications from {authority}")
                return applications
            else:
                logging.warning(f"No applications found for {authority}")
                return []
                
        except Exception as e:
            logging.error(f"Error scraping {authority}: {e}")
            self.failed_authorities.append(authority)
            return []

    def run_scraper(self):
        """Main scraper execution"""
        logging.info("Starting Planning Applications Scraper")
        print("🏗️  Planning Applications Scraper Started")
        print(f"📊 Total authorities to process: {len(UK_PLANNING_AUTHORITIES)} (complete list from PlanIt)")
        
        # Filter out already processed authorities
        remaining_authorities = [auth for auth in UK_PLANNING_AUTHORITIES if auth not in self.processed_authorities]
        
        print(f"⏭️  Remaining authorities: {len(remaining_authorities)}")
        print(f"📚 Known applications in index: {len(self.applications_index)}")
        
        try:
            for i, authority in enumerate(remaining_authorities):
                print(f"\n🔍 Processing {authority} ({i+1}/{len(remaining_authorities)})")
                
                applications = self.scrape_authority(authority)
                
                if applications:
                    self.all_data.extend(applications)
                    print(f"✅ Added {len(applications)} applications from {authority}")
                else:
                    print(f"❌ No data for {authority}")
                
                self.processed_authorities.append(authority)
                
                # Save progress periodically
                if (i + 1) % SAVE_INTERVAL == 0:
                    self.save_checkpoint()
                    print(f"💾 Progress saved at {i+1} authorities")
                
                # Random delay between requests
                time.sleep(random.uniform(2, 5))
            
            # Final save
            self.save_checkpoint()
            self.save_final_data()
            
            # Print summary
            print(f"\n🎉 Scraping completed!")
            print(f"📈 Total applications collected: {len(self.all_data)}")
            print(f"🆕 New applications: {len(self.new_applications)}")
            print(f"🔄 Updated applications: {len(self.updated_applications)}")
            print(f"✅ Successful authorities: {len(self.processed_authorities)}")
            print(f"❌ Failed authorities: {len(self.failed_authorities)}")
            print(f"⏱️  Total time: {(time.time() - self.start_time)/60:.1f} minutes")
            
        except KeyboardInterrupt:
            print("\n⚠️  Scraping interrupted by user")
            self.save_checkpoint()
            print("💾 Progress saved")
        except Exception as e:
            logging.error(f"Fatal error in scraper: {e}")
            print(f"💥 Fatal error: {e}")
            self.save_checkpoint()

    def save_final_data(self):
        """Save final scraped data to timestamped file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'planning_applications_data_{timestamp}.json'
        
        final_data = {
            'scrape_info': {
                'timestamp': datetime.now().isoformat(),
                'total_applications': len(self.all_data),
                'new_applications': len(self.new_applications),
                'updated_applications': len(self.updated_applications),
                'total_in_index': len(self.applications_index),
                'processed_authorities': len(self.processed_authorities),
                'failed_authorities': len(self.failed_authorities),
                'source': 'planit.org.uk',
                'scraper_version': '2.0-status-tracking',
                'next_run_recommended': (datetime.now() + timedelta(days=2)).isoformat()
            },
            'applications': self.all_data,
            'status_changes_summary': {
                'total_applications_with_history': len(self.status_history),
                'recent_changes': len([uid for uid, history in self.status_history.items() 
                                    if any(change['timestamp'] > (datetime.now() - timedelta(days=7)).isoformat() 
                                          for change in history)])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(final_data, f, indent=2)
        
        logging.info(f"Final data saved to {filename}")
        print(f"💾 Final data saved to {filename}")

if __name__ == "__main__":
    scraper = PlanningApplicationsScraper()
    scraper.run_scraper() 