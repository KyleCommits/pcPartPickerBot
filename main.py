from pcpartpicker import API as pcpartpickerAPI
from amazon_buddy import AmazonBuddy, Category, SortType
from newegg import NeweggAPI
from typing import Dict, List, Tuple
from tqdm import tqdm
import time
import statistics

class PCBuildBot:
    def __init__(self):
        self.part_picker_api = pcpartpickerAPI('us')
        # Update required parts to match PCPartPicker's API categories
        self.required_parts = ['cpu', 'motherboard', 'memory', 'internal-hard-drive', 'video-card', 'case', 'power-supply']
        self.part_keywords = {
            'cpu': ['processor', 'cpu', 'ryzen', 'intel', 'core'],
            'motherboard': ['motherboard', 'mainboard', 'mobo'],
            'memory': ['ram', 'ddr4', 'ddr5', 'memory'],
            'internal-hard-drive': ['ssd', 'hdd', 'nvme', 'm.2'],  # Updated from 'storage'
            'video-card': ['gpu', 'graphics card', 'rtx', 'radeon', 'geforce'],
            'case': ['pc case', 'computer case', 'atx'],
            'power-supply': ['psu', 'power supply']
        }
        self.excluded_terms = [
            'code', 'dlc', 'game', 'software', 'cables', 'refurbished', 
            'guide', 'manual', 'warranty', 'support', 'key', 'digital',
            'accessories', 'bundle', 'kit', 'replacement', 'cover'
        ]
        
        # Add minimum price thresholds to avoid irrelevant items
        self.min_price_thresholds = {
            'cpu': 50,
            'motherboard': 40,
            'memory': 30,
            'internal-hard-drive': 20,  # Updated from 'storage'
            'video-card': 100,
            'case': 30,
            'power-supply': 25
        }
        
    def get_build_requirements(self) -> Dict:
        """Get user requirements for the PC build"""
        print("Welcome to PC Build Bot! Let's build your perfect PC.")
        budget = float(input("What's your total budget? $"))
        purpose = input("What's the main purpose of this PC? (gaming/work/general): ")
        return {"budget": budget, "purpose": purpose}
        
    def is_valid_part(self, part: Dict, part_type: str) -> bool:
        """Validate if the part matches the required category"""
        if not part or 'title' not in part or 'price' not in part:
            return False
            
        title = part['title'].lower()
        price = float(part['price'])
        
        # Check minimum price threshold
        if price < self.min_price_thresholds[part_type]:
            return False
            
        # Check for excluded terms
        if any(term in title for term in self.excluded_terms):
            return False
            
        # Check if part matches category keywords
        has_keywords = any(keyword in title for keyword in self.part_keywords[part_type])
        
        # Additional validation for specific part types
        if part_type == 'video-card' and not any(brand in title for brand in ['nvidia', 'amd', 'rtx', 'radeon', 'geforce']):
            return False
            
        if part_type == 'cpu' and not any(brand in title for brand in ['intel', 'ryzen', 'amd']):
            return False
            
        return has_keywords

    def search_part(self, part_type: str, budget: float) -> Dict:
        """Search for a specific part within budget"""
        try:
            # Get parts from PCPartPicker only
            parts_data = self.part_picker_api.retrieve(part_type)
            
            return {
                "pcpartpicker": parts_data.get(part_type, []),
                "amazon": [],  # Removed Amazon searching
                "newegg": []   # Removed Newegg searching
            }
        except Exception as e:
            print(f"Error searching for {part_type}: {e}")
            return {"pcpartpicker": [], "amazon": [], "newegg": []}

    def get_best_parts(self, suggestions: Dict, budget: float) -> Tuple[Dict, str]:
        """Select the best parts based on price and availability"""
        best_part = None
        best_price = float('inf')
        
        # Only check PCPartPicker results
        for part in suggestions["pcpartpicker"]:
            if isinstance(part, dict) and 'price' in part:
                price = float(part['price'])
                if price <= budget and price < best_price:
                    best_part = part
                    best_price = price

        return (best_part, "pcpartpicker") if best_part else (None, None)

    def suggest_build(self, requirements: Dict) -> Tuple[Dict, float]:
        """Suggest a PC build based on requirements"""
        build = {}
        total_cost = 0
        budget_allocation = self._get_budget_allocation(requirements["purpose"])
        
        print("\nSearching for compatible parts...")
        with tqdm(total=len(self.required_parts)) as pbar:
            for part in self.required_parts:
                part_budget = requirements["budget"] * budget_allocation[part]
                part_suggestions = self.search_part(part, part_budget)
                best_part, source = self.get_best_parts(part_suggestions, part_budget)
                
                if best_part:
                    build[part] = {
                        "part": best_part,
                        "source": source,
                        "price": float(best_part['price'])
                    }
                    total_cost += float(best_part['price'])
                pbar.update(1)
                
        return build, total_cost

    def _get_budget_allocation(self, purpose: str) -> Dict[str, float]:
        """Return budget allocation percentages for each part based on PC purpose"""
        if purpose.lower() == "gaming":
            return {
                "cpu": 0.20,
                "motherboard": 0.15,
                "memory": 0.10,
                "internal-hard-drive": 0.10,  # Updated from 'storage'
                "video-card": 0.30,
                "case": 0.05,
                "power-supply": 0.10
            }
        # Add more purpose-specific allocations here
        return {}

def format_price(price: float) -> str:
    return f"${price:,.2f}"

def main():
    bot = PCBuildBot()
    requirements = bot.get_build_requirements()
    print("\nFinding the best components for your build...")
    suggested_build, total_cost = bot.suggest_build(requirements)
    
    print("\n=== Recommended Build ===")
    print(f"Budget: {format_price(requirements['budget'])}")
    print(f"Purpose: {requirements['purpose'].title()}\n")
    
    if not suggested_build:
        print("Could not find compatible parts within budget.")
        return

    for part, details in suggested_build.items():
        print(f"{part.upper()}:")
        print(f"  • {details['part']['title'][:80]}...")
        print(f"  • Price: {format_price(details['price'])} ({details['source']})")
        print()

    remaining_budget = requirements["budget"] - total_cost
    print("=== Build Summary ===")
    print(f"Total Cost: {format_price(total_cost)}")
    print(f"Remaining Budget: {format_price(remaining_budget)}")
    print(f"Budget Utilization: {(total_cost/requirements['budget']*100):.1f}%")

if __name__ == '__main__':
    main()
