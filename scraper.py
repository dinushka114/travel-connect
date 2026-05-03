import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import re


class TravelConnectScraper:
    def __init__(self, url):
        """Initialize the scraper with the target URL"""
        self.url = url
        self.posts_data = []
        
    def fetch_page(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_location(self, text):
        locations = []
        text_lower = text.lower()
        
        if 'sri lanka' in text_lower:
            locations.append('Sri Lanka')
        if 'madagascar' in text_lower:
            locations.append('Madagascar')
        if 'seychelles' in text_lower:
            locations.append('Seychelles')
        
        return locations if locations else ['Not specified']
    
    def extract_intent_level(self, text):
        text_lower = text.lower()
        
        high_intent_keywords = [
            'looking to', 'booking', 'planning to', 'urgently need',
            'currently organizing', 'looking for', 'sourcing', 'need to',
            'email me', 'contact me', 'dm me', 'reach out', 'budget',
            'executive team', 'setting up', 'arrange', 'semi-permanent'
        ]
        
        medium_intent_keywords = [
            'thinking about', 'interested in', 'considering', 'planning',
            'want to', 'might', 'potentially', 'curious', 'asking',
            'advice', 'recommendation', 'experience'
        ]
        
        high_count = sum(1 for keyword in high_intent_keywords if keyword in text_lower)
        medium_count = sum(1 for keyword in medium_intent_keywords if keyword in text_lower)
        
        if high_count > 0:
            return 'High'
        elif medium_count > 0:
            return 'Medium'
        else:
            return 'Low'
    
    def extract_hotel_requirements(self, text):
        requirements = []
        text_lower = text.lower()
        
        if '5-star' in text_lower or 'five-star' in text_lower or 'luxury' in text_lower:
            requirements.append('Luxury 5-Star')
        if 'boutique' in text_lower:
            requirements.append('Boutique Hotel')
        if 'villa' in text_lower or 'private villa' in text_lower:
            requirements.append('Private Villa')
        if 'resort' in text_lower:
            requirements.append('Resort')
        if 'lodge' in text_lower:
            requirements.append('Lodge')
        
        if 'private' in text_lower and 'service' in text_lower:
            requirements.append('Private Service')
        if 'white-glove' in text_lower:
            requirements.append('White-Glove Service')
        if 'corporate' in text_lower or 'business' in text_lower or 'meeting' in text_lower:
            requirements.append('Corporate Facilities')
        if 'lounge' in text_lower or 'dining' in text_lower:
            requirements.append('Premium Amenities')
        
        budget_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)[k]?', text)
        if budget_match:
            requirements.append(f"Budget: ${budget_match.group(1)}{'k' if 'k' in text[budget_match.start():budget_match.end()] else ''}")
        
        return requirements if requirements else ['Standard']
    
    def extract_contact_info(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails if emails else []
    
    def parse_posts(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        posts = soup.find_all('div', class_='post')
        
        print(f"\nFound {len(posts)} posts to process...")
        
        for post in posts:
            try:
                post_id = post.get('data-post-id', 'N/A')
                
                # Extract author name
                author_elem = post.find('a', class_='post-author')
                author_name = author_elem.text.strip() if author_elem else 'Unknown'
                
                # Extract headline (role/business)
                headline_elem = post.find('div', class_='post-headline')
                headline = headline_elem.text.strip() if headline_elem else 'Not specified'
                
                # Extract post content
                content_elem = post.find('div', class_='post-content')
                content = content_elem.text.strip() if content_elem else ''
                
                # Extract post time
                time_elem = post.find('div', class_='post-time')
                post_time = time_elem.text.strip() if time_elem else 'Unknown'
                
                # Extract engagement stats
                stats_elem = post.find('div', class_='post-stats')
                stats = stats_elem.text.strip() if stats_elem else 'N/A'
                
                # Process extracted data
                locations = self.extract_location(content)
                intent_level = self.extract_intent_level(content)
                hotel_requirements = self.extract_hotel_requirements(content)
                contact_info = self.extract_contact_info(content)
                
                post_data = {
                    'post_id': post_id,
                    'author_name': author_name,
                    'role_business': headline,
                    'location': ', '.join(locations),
                    'travel_intent_level': intent_level,
                    'hotel_requirements': ', '.join(hotel_requirements),
                    'contact_email': ', '.join(contact_info) if contact_info else 'Not provided',
                    'post_content': content[:200] + '...' if len(content) > 200 else content,
                    'engagement_stats': stats,
                    'post_time': post_time,
                    'scraped_at': datetime.now().isoformat()
                }
                
                self.posts_data.append(post_data)
                print(f"✓ Extracted post {post_id}: {author_name} ({headline})")
                
            except Exception as e:
                print(f"Error parsing post: {e}")
                continue
    
    def save_to_json(self, filename='travel_data.json'):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.posts_data, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Data saved to {filename}")
        except Exception as e:
            print(f"Error saving JSON: {e}")
    
    def save_to_csv(self, filename='travel_data.csv'):
        try:
            if not self.posts_data:
                print("No data to save")
                return
            
            keys = self.posts_data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.posts_data)
            print(f"✓ Data saved to {filename}")
        except Exception as e:
            print(f"Error saving CSV: {e}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TRAVEL CONNECT DATA SCRAPING SUMMARY")
        print("="*60)
        
        if not self.posts_data:
            print("No data scraped")
            return
        
        print(f"\nTotal Posts Scraped: {len(self.posts_data)}")
        
        # Group by location
        locations = {}
        for post in self.posts_data:
            for loc in post['location'].split(', '):
                locations[loc] = locations.get(loc, 0) + 1
        
        print("\nBy Location:")
        for loc, count in sorted(locations.items()):
            print(f"  • {loc}: {count} posts")
        
        # Group by intent level
        intent_levels = {}
        for post in self.posts_data:
            intent = post['travel_intent_level']
            intent_levels[intent] = intent_levels.get(intent, 0) + 1
        
        print("\nBy Travel Intent Level:")
        for level in ['High', 'Medium', 'Low']:
            if level in intent_levels:
                print(f"  • {level}: {intent_levels[level]} posts")
        
        # Show high intent prospects
        high_intent = [p for p in self.posts_data if p['travel_intent_level'] == 'High']
        print(f"\n🎯 High Intent Prospects: {len(high_intent)}")
        for post in high_intent:
            print(f"  • {post['author_name']} ({post['role_business']})")
            print(f"    Location: {post['location']}")
            if post['contact_email'] != 'Not provided':
                print(f"    Email: {post['contact_email']}")
            print()
        
        print("="*60)
    
    def run(self):
        print(f"Starting scraper for: {self.url}\n")
        
        html = self.fetch_page()
        if not html:
            print("Failed to fetch page content")
            return False
        
        self.parse_posts(html)
        
        if self.posts_data:
            self.save_to_json()
            self.save_to_csv()
            self.print_summary()
            return True
        else:
            print("No posts were scraped")
            return False

