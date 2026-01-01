"""
Gold Rate Fetcher - Fetch live gold rates from Indian sources
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Optional
import re


async def fetch_goodreturns_rates() -> Dict[str, float]:
    """
    Fetch gold rates from GoodReturns India
    Returns rates in INR per gram for different purities
    """
    try:
        url = "https://www.goodreturns.in/gold-rates/"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Initialize rates
            rates = {
                'gold_per_gram_24k': 0,
                'gold_per_gram_22k': 0,
                'gold_per_10g_24k': 0,
                'gold_per_10g_22k': 0,
                'source': 'GoodReturns India',
                'timestamp': datetime.now().isoformat()
            }

            # Try to find gold rate tables
            # GoodReturns typically shows rates in a table format
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        text = ' '.join([cell.get_text().strip() for cell in cells])

                        # Look for 24 carat / 22 carat patterns
                        if '24' in text or '24K' in text or '999' in text:
                            # Extract price
                            price = extract_price(text)
                            if price and 'gram' in text.lower():
                                rates['gold_per_gram_24k'] = price
                            elif price and '10' in text:
                                rates['gold_per_10g_24k'] = price
                                rates['gold_per_gram_24k'] = price / 10

                        if '22' in text or '22K' in text or '916' in text:
                            price = extract_price(text)
                            if price and 'gram' in text.lower():
                                rates['gold_per_gram_22k'] = price
                            elif price and '10' in text:
                                rates['gold_per_10g_22k'] = price
                                rates['gold_per_gram_22k'] = price / 10

            # Calculate derived rates if we have 24K or 22K
            if rates['gold_per_gram_24k'] > 0:
                if rates['gold_per_10g_24k'] == 0:
                    rates['gold_per_10g_24k'] = rates['gold_per_gram_24k'] * 10
                if rates['gold_per_gram_22k'] == 0:
                    rates['gold_per_gram_22k'] = rates['gold_per_gram_24k'] * 0.9167
                if rates['gold_per_10g_22k'] == 0:
                    rates['gold_per_10g_22k'] = rates['gold_per_10g_24k'] * 0.9167

            if rates['gold_per_gram_22k'] > 0:
                if rates['gold_per_10g_22k'] == 0:
                    rates['gold_per_10g_22k'] = rates['gold_per_gram_22k'] * 10
                if rates['gold_per_gram_24k'] == 0:
                    rates['gold_per_gram_24k'] = rates['gold_per_gram_22k'] / 0.9167
                if rates['gold_per_10g_24k'] == 0:
                    rates['gold_per_10g_24k'] = rates['gold_per_gram_24k'] * 10

            # Calculate 18K and 14K from 24K
            if rates['gold_per_gram_24k'] > 0:
                rates['gold_per_gram_18k'] = rates['gold_per_gram_24k'] * 0.75
                rates['gold_per_gram_14k'] = rates['gold_per_gram_24k'] * 0.5833
                rates['gold_per_10g_18k'] = rates['gold_per_gram_18k'] * 10

            return rates

    except Exception as e:
        print(f"Error fetching from GoodReturns: {e}")
        raise


def extract_price(text: str) -> Optional[float]:
    """Extract price from text string"""
    # Remove commas and rupee symbols
    text = text.replace(',', '').replace('₹', '').replace('Rs', '').replace('INR', '')

    # Find numbers
    numbers = re.findall(r'\d+\.?\d*', text)

    for num in numbers:
        try:
            price = float(num)
            # Filter out unrealistic prices (gold should be between 3000-10000 per gram)
            if 3000 <= price <= 100000:
                return price
        except ValueError:
            continue

    return None


async def get_indian_gold_rates() -> Dict[str, float]:
    """
    Get comprehensive gold rates from multiple sources
    Tries GoodReturns first, falls back to estimates
    """
    try:
        # Try GoodReturns first
        rates = await fetch_goodreturns_rates()
        if rates['gold_per_gram_22k'] > 0:
            return rates
    except Exception as e:
        print(f"GoodReturns fetch failed: {e}")

    # Fallback to manual rates
    return {
        'gold_per_gram_24k': 7500,
        'gold_per_gram_22k': 6875,
        'gold_per_gram_18k': 5625,
        'gold_per_gram_14k': 4375,
        'gold_per_10g_24k': 75000,
        'gold_per_10g_22k': 68750,
        'gold_per_10g_18k': 56250,
        'silver_per_gram': 92,
        'silver_per_kg': 92000,
        'platinum_per_gram': 3000,
        'platinum_per_10g': 30000,
        'copper_per_gram': 0.6,
        'copper_per_kg': 600,
        'source': 'Manual Fallback Rates',
        'timestamp': datetime.now().isoformat()
    }
