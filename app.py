import csv
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime
import os

class JobScraper:
    def __init__(self):
        self.jobs_data = []
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver with Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            # Use local chromedriver.exe
            chromedriver_path = './chromedriver.exe'
            if not os.path.exists(chromedriver_path):
                chromedriver_path = './chromedriver'  # For Linux/Mac
            
            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            print("✓ Selenium WebDriver initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing WebDriver: {e}")
            self.driver = None
    
    def scrape_internshala(self, role, location):
        """Scrape jobs from Internshala using Selenium"""
        print(f"\n🔍 Searching Internshala for '{role}' in '{location}'...")
        
        if not self.driver:
            print("✗ Selenium not available, skipping Internshala")
            return
        
        try:
            # Internshala search URL - using their search page
            base_url = "https://internshala.com/internships"
            
            self.driver.get(base_url)
            time.sleep(3)
            
            # Search for the role
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search_keywords"))
                )
                search_box.clear()
                search_box.send_keys(role)
                search_box.send_keys(Keys.RETURN)
                time.sleep(4)
            except:
                # Try alternate search approach
                self.driver.get(f"https://internshala.com/internships/keywords-{role.replace(' ', '%20')}")
                time.sleep(4)
            
            # Scroll to load more jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Find job containers
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Multiple selectors for job cards
            job_cards = soup.find_all('div', class_='individual_internship') or \
                       soup.find_all('div', {'id': lambda x: x and x.startswith('internship_')}) or \
                       soup.find_all('div', class_='internship_meta')
            
            count = 0
            for card in job_cards[:25]:
                try:
                    # Extract title
                    title_elem = card.find('h3') or card.find('h4') or card.find('a', class_='view_detail_button')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract company
                    company_elem = card.find('p', class_='company-name') or \
                                  card.find('a', class_='link_display_like_text') or \
                                  card.find('div', class_='company')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    # Extract location
                    location_elem = card.find('a', {'id': lambda x: x and 'location_link' in str(x)}) or \
                                   card.find('span', class_='location') or \
                                   card.find('div', class_='location')
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract link
                    link_elem = card.find('a', {'class': 'view_detail_button'}) or card.find('a', href=True)
                    if link_elem and link_elem.get('href'):
                        link = link_elem['href']
                        if not link.startswith('http'):
                            link = f"https://internshala.com{link}"
                    else:
                        link = base_url
                    
                    self.jobs_data.append({
                        'Platform': 'Internshala',
                        'Job Title': title,
                        'Company': company,
                        'Location': job_location,
                        'Apply Link': link,
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d')
                    })
                    count += 1
                except Exception as e:
                    continue
            
            print(f"✓ Found {count} jobs on Internshala")
            
        except Exception as e:
            print(f"✗ Error scraping Internshala: {e}")
    
    def scrape_ycombinator(self, role, location):
        """Scrape jobs from Y Combinator Work at a Startup"""
        print(f"\n🔍 Searching Y Combinator for '{role}' in '{location}'...")
        
        if not self.driver:
            print("✗ Selenium not available, skipping Y Combinator")
            return
        
        try:
            # YC's job board
            url = "https://www.workatastartup.com/jobs"
            
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll to load jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find job listings - YC uses various structures
            job_cards = soup.find_all('div', class_='job') or \
                       soup.find_all('a', href=lambda x: x and '/jobs/' in str(x)) or \
                       soup.find_all('div', {'data-testid': 'job-card'})
            
            count = 0
            role_lower = role.lower()
            
            for card in job_cards[:30]:
                try:
                    # Extract job details
                    title_elem = card.find('h3') or card.find('h2') or card.find('span', class_='title')
                    
                    if not title_elem:
                        # Try to find in link text
                        if card.name == 'a':
                            title_text = card.get_text(strip=True)
                            if len(title_text) > 10 and len(title_text) < 100:
                                title_elem = card
                    
                    if not title_elem:
                        continue
                    
                    job_title = title_elem.get_text(strip=True)
                    
                    # Filter by role keywords
                    if not any(keyword in job_title.lower() for keyword in role_lower.split()):
                        continue
                    
                    # Extract company
                    company_elem = card.find('span', class_='company') or \
                                  card.find('div', class_='company-name') or \
                                  card.find_next('span')
                    company_name = company_elem.get_text(strip=True) if company_elem else "YC Startup"
                    
                    # Extract location
                    location_elem = card.find('span', class_='location') or \
                                   card.find('div', class_='location')
                    job_location = location_elem.get_text(strip=True) if location_elem else "Remote/Various"
                    
                    # Extract link
                    link = card.get('href', '') if card.name == 'a' else ''
                    if not link:
                        link_elem = card.find('a')
                        link = link_elem.get('href', '') if link_elem else url
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.workatastartup.com{link}"
                    
                    if not link:
                        link = url
                    
                    self.jobs_data.append({
                        'Platform': 'Y Combinator',
                        'Job Title': job_title,
                        'Company': company_name,
                        'Location': job_location,
                        'Apply Link': link,
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d')
                    })
                    count += 1
                    
                except Exception as e:
                    continue
            
            print(f"✓ Found {count} jobs on Y Combinator")
            
        except Exception as e:
            print(f"✗ Error scraping Y Combinator: {e}")
    
    def scrape_naukri(self, role, location):
        """Scrape jobs from Naukri (requires Selenium due to dynamic content)"""
        print(f"\n🔍 Searching Naukri for '{role}' in '{location}'...")
        
        if not self.driver:
            print("✗ Selenium not available, skipping Naukri")
            return
        
        try:
            role_formatted = role.replace(' ', '-')
            location_formatted = location.replace(' ', '-')
            
            url = f"https://www.naukri.com/{role_formatted}-jobs-in-{location_formatted}"
            
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll to load more jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CLASS_NAME, 'srp-jobtuple-wrapper')
            
            if not job_cards:
                job_cards = self.driver.find_elements(By.CLASS_NAME, 'jobTuple')
            
            count = 0
            for card in job_cards[:20]:
                try:
                    title = card.find_element(By.CLASS_NAME, 'title').text
                    company = card.find_element(By.CLASS_NAME, 'comp-name').text
                    job_location = card.find_element(By.CLASS_NAME, 'locWdth').text
                    link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    
                    self.jobs_data.append({
                        'Platform': 'Naukri',
                        'Job Title': title,
                        'Company': company,
                        'Location': job_location,
                        'Apply Link': link,
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d')
                    })
                    count += 1
                except Exception as e:
                    continue
            
            print(f"✓ Found {count} jobs on Naukri")
            
        except Exception as e:
            print(f"✗ Error scraping Naukri: {e}")
    
    def scrape_linkedin(self, role, location):
        """Scrape jobs from LinkedIn using Selenium"""
        print(f"\n🔍 Searching LinkedIn for '{role}' in '{location}'...")
        print("⚠️  Note: LinkedIn has strict anti-scraping measures. Results may be limited.")
        
        if not self.driver:
            print("✗ Selenium not available, skipping LinkedIn")
            return
        
        try:
            role_formatted = role.replace(' ', '%20')
            location_formatted = location.replace(' ', '%20')
            
            url = f"https://www.linkedin.com/jobs/search/?keywords={role_formatted}&location={location_formatted}"
            
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll to load jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # LinkedIn job cards
            job_cards = soup.find_all('div', class_='base-card') or \
                       soup.find_all('div', class_='job-search-card')
            
            count = 0
            for card in job_cards[:15]:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title') or \
                                card.find('h3', class_='job-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle') or \
                                  card.find('h4', class_='job-search-card__company-name')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link') or \
                               card.find('a', href=True)
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        link = link_elem['href'] if link_elem else url
                        
                        self.jobs_data.append({
                            'Platform': 'LinkedIn',
                            'Job Title': title,
                            'Company': company,
                            'Location': job_location,
                            'Apply Link': link,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d')
                        })
                        count += 1
                except Exception as e:
                    continue
            
            print(f"✓ Found {count} jobs on LinkedIn")
            
        except Exception as e:
            print(f"✗ Error scraping LinkedIn: {e}")
    
    def save_to_csv(self, filename='jobs_scraped.csv'):
        """Save all scraped jobs to CSV"""
        if not self.jobs_data:
            print("\n❌ No jobs found to save!")
            return
        
        df = pd.DataFrame(self.jobs_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✅ Successfully saved {len(self.jobs_data)} jobs to '{filename}'")
        print(f"\n📊 Summary:")
        print(df['Platform'].value_counts())
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")

def main():
    print("=" * 60)
    print("🚀 MULTI-PLATFORM JOB SCRAPER")
    print("=" * 60)
    
    # Get user input
    role = input("\n📝 Enter the job role you're looking for (e.g., Python Developer, Data Analyst): ").strip()
    location = input("📍 Enter the location (e.g., Mumbai, Bangalore, Remote): ").strip()
    
    if not role or not location:
        print("❌ Role and location are required!")
        return
    
    print(f"\n🎯 Searching for '{role}' jobs in '{location}'...\n")
    
    # Initialize scraper
    scraper = JobScraper()
    
    # Scrape from all platforms
    scraper.scrape_internshala(role, location)
    time.sleep(2)
    
    scraper.scrape_ycombinator(role, location)
    time.sleep(2)
    
    scraper.scrape_naukri(role, location)
    time.sleep(2)
    
    scraper.scrape_linkedin(role, location)
    
    # Save results
    filename = f"jobs_{role.replace(' ', '_')}_{location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    scraper.save_to_csv(filename)
    
    # Cleanup
    scraper.close()
    
    print("\n✨ Scraping complete!")

if __name__ == "__main__":
    main()