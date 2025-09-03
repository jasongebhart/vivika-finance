"""
External data integration service for cost-of-living, education, and other financial data.
"""

import asyncio
import httpx
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from models.financial_models import CityComparisonData

logger = logging.getLogger(__name__)

class ExternalDataService:
    """Service for fetching external financial and cost-of-living data."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache = {}
        self.cache_duration = timedelta(hours=24)  # Cache data for 24 hours
    
    async def get_city_cost_data(self, city_name: str) -> CityComparisonData:
        """
        Fetch cost of living data for a city.
        In production, this would integrate with real APIs like Numbeo, BLS, etc.
        """
        cache_key = f"city_cost_{city_name.lower()}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.info(f"Using cached cost data for {city_name}")
                return CityComparisonData.parse_obj(cached_data)
        
        try:
            # In a real implementation, this would call actual APIs
            # For demo purposes, using mock data based on known city patterns
            cost_data = await self._fetch_mock_city_data(city_name)
            
            # Cache the result
            self.cache[cache_key] = (cost_data.dict(), datetime.now())
            
            logger.info(f"Fetched cost data for {city_name}")
            return cost_data
            
        except Exception as e:
            logger.error(f"Failed to fetch cost data for {city_name}: {e}")
            # Return default data if API fails
            return self._get_default_city_data(city_name)
    
    async def _fetch_mock_city_data(self, city_name: str) -> CityComparisonData:
        """
        Mock implementation of city cost data fetching.
        In production, replace with actual API calls to services like:
        - Numbeo API
        - Bureau of Labor Statistics
        - Zillow API for housing
        - GasBuddy API for transportation
        """
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Mock cost data based on known expensive/cheap cities
        city_lower = city_name.lower()
        
        if any(expensive in city_lower for expensive in ['san francisco', 'new york', 'manhattan', 'boston', 'seattle']):
            return CityComparisonData(
                city_name=city_name,
                state="CA" if "san francisco" in city_lower else "NY",
                cost_index=180.0,  # 80% above national average
                housing_cost=4500.0,  # Monthly rent/mortgage
                utilities_cost=250.0,
                grocery_cost=450.0,
                transportation_cost=200.0,
                healthcare_cost=350.0,
                overall_cost_difference=0.8  # 80% more expensive
            )
        elif any(expensive in city_lower for expensive in ['los angeles', 'chicago', 'washington dc', 'miami']):
            return CityComparisonData(
                city_name=city_name,
                state="CA" if "los angeles" in city_lower else "IL",
                cost_index=140.0,  # 40% above national average
                housing_cost=2800.0,
                utilities_cost=180.0,
                grocery_cost=380.0,
                transportation_cost=150.0,
                healthcare_cost=280.0,
                overall_cost_difference=0.4
            )
        elif any(affordable in city_lower for affordable in ['austin', 'denver', 'atlanta', 'phoenix']):
            return CityComparisonData(
                city_name=city_name,
                state="TX" if "austin" in city_lower else "CO",
                cost_index=110.0,  # 10% above national average
                housing_cost=1800.0,
                utilities_cost=150.0,
                grocery_cost=320.0,
                transportation_cost=120.0,
                healthcare_cost=220.0,
                overall_cost_difference=0.1
            )
        else:
            # Default to national average
            return CityComparisonData(
                city_name=city_name,
                state="Unknown",
                cost_index=100.0,  # National average
                housing_cost=1500.0,
                utilities_cost=130.0,
                grocery_cost=300.0,
                transportation_cost=100.0,
                healthcare_cost=200.0,
                overall_cost_difference=0.0
            )
    
    def _get_default_city_data(self, city_name: str) -> CityComparisonData:
        """Return default city data when API fails."""
        return CityComparisonData(
            city_name=city_name,
            state="Unknown",
            cost_index=100.0,
            housing_cost=1500.0,
            utilities_cost=130.0,
            grocery_cost=300.0,
            transportation_cost=100.0,
            healthcare_cost=200.0,
            overall_cost_difference=0.0
        )
    
    async def get_education_cost_data(self, state: str, institution_type: str) -> Dict[str, float]:
        """
        Fetch education cost data by state and institution type.
        In production, integrate with Department of Education APIs.
        """
        cache_key = f"education_{state}_{institution_type}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # Mock education costs - in production, use real APIs
            costs = await self._fetch_mock_education_data(state, institution_type)
            
            # Cache the result
            self.cache[cache_key] = (costs, datetime.now())
            
            return costs
            
        except Exception as e:
            logger.error(f"Failed to fetch education data for {state}, {institution_type}: {e}")
            return self._get_default_education_costs(institution_type)
    
    async def _fetch_mock_education_data(self, state: str, institution_type: str) -> Dict[str, float]:
        """Mock education cost data."""
        
        # Base costs by type
        base_costs = {
            "private_k12": 25000,
            "public_college_in_state": 28000,
            "public_college_out_state": 45000,
            "private_college": 58000
        }
        
        # State multipliers (some states more expensive)
        state_multipliers = {
            "CA": 1.3, "NY": 1.25, "MA": 1.2, "CT": 1.15,
            "TX": 0.9, "FL": 0.85, "OH": 0.8, "NC": 0.85
        }
        
        multiplier = state_multipliers.get(state, 1.0)
        base_cost = base_costs.get(institution_type, 30000)
        
        return {
            "annual_tuition": base_cost * multiplier,
            "annual_fees": base_cost * 0.1 * multiplier,
            "room_board": 15000 * multiplier if "college" in institution_type else 0,
            "books_supplies": 1200 * multiplier,
            "transportation": 1000,
            "personal_expenses": 2000
        }
    
    def _get_default_education_costs(self, institution_type: str) -> Dict[str, float]:
        """Default education costs when API fails."""
        return {
            "annual_tuition": 30000,
            "annual_fees": 3000,
            "room_board": 12000,
            "books_supplies": 1200,
            "transportation": 1000,
            "personal_expenses": 2000
        }
    
    async def get_vehicle_cost_data(self, vehicle_type: str, region: str) -> Dict[str, float]:
        """
        Fetch vehicle ownership cost data by type and region.
        In production, integrate with automotive APIs like Edmunds, KBB.
        """
        cache_key = f"vehicle_{vehicle_type}_{region}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            costs = await self._fetch_mock_vehicle_data(vehicle_type, region)
            self.cache[cache_key] = (costs, datetime.now())
            return costs
            
        except Exception as e:
            logger.error(f"Failed to fetch vehicle data for {vehicle_type}, {region}: {e}")
            return self._get_default_vehicle_costs(vehicle_type)
    
    async def _fetch_mock_vehicle_data(self, vehicle_type: str, region: str) -> Dict[str, float]:
        """Mock vehicle cost data."""
        
        base_costs = {
            "economy": {"price": 25000, "insurance": 1200, "maintenance": 800, "fuel_mpg": 30},
            "midsize": {"price": 35000, "insurance": 1400, "maintenance": 1000, "fuel_mpg": 25},
            "luxury": {"price": 55000, "insurance": 2000, "maintenance": 1500, "fuel_mpg": 22},
            "suv": {"price": 45000, "insurance": 1600, "maintenance": 1200, "fuel_mpg": 20},
            "electric": {"price": 45000, "insurance": 1300, "maintenance": 600, "fuel_mpg": 100}
        }
        
        # Regional multipliers for insurance and gas
        region_multipliers = {
            "northeast": {"insurance": 1.2, "gas": 1.1},
            "west": {"insurance": 1.3, "gas": 1.15},
            "south": {"insurance": 0.9, "gas": 0.95},
            "midwest": {"insurance": 0.85, "gas": 0.9}
        }
        
        base = base_costs.get(vehicle_type, base_costs["midsize"])
        multipliers = region_multipliers.get(region.lower(), {"insurance": 1.0, "gas": 1.0})
        
        return {
            "purchase_price": base["price"],
            "annual_insurance": base["insurance"] * multipliers["insurance"],
            "annual_maintenance": base["maintenance"],
            "fuel_efficiency_mpg": base["fuel_mpg"],
            "regional_gas_price": 3.50 * multipliers["gas"],
            "depreciation_rate": 0.15  # 15% per year
        }
    
    def _get_default_vehicle_costs(self, vehicle_type: str) -> Dict[str, float]:
        """Default vehicle costs when API fails."""
        return {
            "purchase_price": 35000,
            "annual_insurance": 1400,
            "annual_maintenance": 1000,
            "fuel_efficiency_mpg": 25,
            "regional_gas_price": 3.50,
            "depreciation_rate": 0.15
        }
    
    async def get_inflation_data(self) -> Dict[str, float]:
        """
        Fetch current inflation data from economic APIs.
        In production, integrate with FRED (Federal Reserve Economic Data) API.
        """
        cache_key = "inflation_data"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=6):  # Refresh every 6 hours
                return cached_data
        
        try:
            # Mock inflation data - in production, fetch from FRED API
            inflation_data = {
                "current_cpi": 3.2,  # Current Consumer Price Index
                "core_cpi": 2.8,    # Core CPI (excluding food and energy)
                "pce": 2.9,         # Personal Consumption Expenditures
                "housing_inflation": 4.1,
                "education_inflation": 5.2,
                "healthcare_inflation": 3.8,
                "energy_inflation": 8.5
            }
            
            self.cache[cache_key] = (inflation_data, datetime.now())
            return inflation_data
            
        except Exception as e:
            logger.error(f"Failed to fetch inflation data: {e}")
            return {
                "current_cpi": 3.0,
                "core_cpi": 2.5,
                "pce": 2.8,
                "housing_inflation": 4.0,
                "education_inflation": 5.0,
                "healthcare_inflation": 3.5,
                "energy_inflation": 6.0
            }
    
    async def get_market_data(self) -> Dict[str, float]:
        """
        Fetch current market data for investment projections.
        In production, integrate with financial APIs like Alpha Vantage, IEX Cloud.
        """
        cache_key = "market_data"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=1):  # Refresh hourly during market hours
                return cached_data
        
        try:
            # Mock market data
            market_data = {
                "sp500_return_ytd": 0.12,
                "bond_yield_10yr": 0.045,
                "volatility_index": 18.5,
                "dollar_strength_index": 102.3,
                "real_estate_index": 0.085
            }
            
            self.cache[cache_key] = (market_data, datetime.now())
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return {
                "sp500_return_ytd": 0.10,
                "bond_yield_10yr": 0.04,
                "volatility_index": 20.0,
                "dollar_strength_index": 100.0,
                "real_estate_index": 0.08
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()