#!/usr/bin/env python3
"""
FastAPI main application for Long-Term Financial Planning & Projection Application.
Fixed version with working WebSocket connections.
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

# Import services (restored)
from services.financial_config_service import FinancialConfigService
from services.scenario_manager import ScenarioManager
from services.expense_service import ExpenseService
from services.life_planning_service import life_planning_service, Child

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
try:
    financial_config = FinancialConfigService()
    logger.info("Financial config service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize financial config service: {e}")
    import traceback
    traceback.print_exc()
    financial_config = None

try:
    scenario_manager = ScenarioManager()
    logger.info("Scenario manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize scenario manager: {e}")
    import traceback
    traceback.print_exc()
    scenario_manager = None

try:
    expense_service = ExpenseService()
    logger.info("Expense service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize expense service: {e}")
    import traceback
    traceback.print_exc()
    expense_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Long-Term Financial Planning Application")
    
    # Initialize databases
    if scenario_manager:
        try:
            await scenario_manager.initialize_database()
            logger.info("Scenario database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scenario database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title="Long-Term Financial Planning & Projection API",
    description="Advanced financial planning with scenario modeling and Monte Carlo simulations",
    version="2.0.0",
    lifespan=lifespan
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS configuration based on environment
if ENVIRONMENT == "production":
    # Production: Use specific allowed origins
    allowed_origins = json.loads(os.getenv("ALLOWED_ORIGINS", '["http://localhost:3001"]'))
else:
    # Development: Allow all origins
    allowed_origins = ["*"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscribers: Dict[str, List[WebSocket]] = {
            'config_updates': [],
            'scenario_updates': [],
            'simulation_updates': []
        }

    async def connect(self, websocket: WebSocket, topic: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Subscribe to specific topics
        if topic and topic in self.subscribers:
            self.subscribers[topic].append(websocket)
            logger.info(f"Client subscribed to topic: {topic}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all topic subscriptions
        for topic, subscribers in self.subscribers.items():
            if websocket in subscribers:
                subscribers.remove(websocket)
                logger.info(f"Client unsubscribed from topic: {topic}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_to_topic(self, topic: str, message: str):
        """Broadcast message to subscribers of a specific topic."""
        if topic not in self.subscribers:
            return
        
        disconnected = []
        for connection in self.subscribers[topic]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to topic {topic}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def notify_config_update(self, config_type: str, data: dict):
        """Notify subscribers of configuration updates."""
        message = {
            "type": "config_update",
            "config_type": config_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_topic('config_updates', json.dumps(message))

manager = ConnectionManager()

# Background task functions
async def process_scenario_background(scenario_data: Dict[str, Any]):
    """Background task to process scenario calculations."""
    try:
        scenario_name = scenario_data.get('name', 'Unknown Scenario')
        logger.info(f"Processing scenario in background: {scenario_name}")
        
        # Simulate scenario processing (replace with actual calculation logic)
        await asyncio.sleep(2)  # Simulate processing time
        
        # Notify WebSocket subscribers of completion
        completion_message = {
            "type": "scenario_completed",
            "scenario_name": scenario_name,
            "status": "completed",
            "projected_net_worth": 1500000,  # Placeholder result
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast_to_topic('scenario_updates', json.dumps(completion_message))
        logger.info(f"Scenario processing completed: {scenario_name}")
        
    except Exception as e:
        logger.error(f"Background scenario processing failed: {e}")
        error_message = {
            "type": "scenario_error",
            "scenario_name": scenario_data.get('name', 'Unknown'),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast_to_topic('scenario_updates', json.dumps(error_message))

async def process_dynamic_scenario_background(scenario_id: str):
    """Background task to process dynamic scenario calculations."""
    try:
        logger.info(f"Processing dynamic scenario in background: {scenario_id}")
        
        if not scenario_manager:
            raise Exception("Scenario manager not initialized")
        
        # Run the scenario projection
        projection_results = await scenario_manager.run_dynamic_scenario(scenario_id)
        
        # Get updated scenario
        scenario = await scenario_manager.get_dynamic_scenario(scenario_id)
        
        # Notify WebSocket subscribers of completion
        completion_message = {
            "type": "scenario_completed",
            "scenario_id": scenario_id,
            "scenario_name": scenario['name'] if scenario else 'Unknown',
            "status": "completed",
            "projected_net_worth": projection_results.get('final_net_worth', 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast_to_topic('scenario_updates', json.dumps(completion_message))
        logger.info(f"Dynamic scenario processing completed: {scenario_id}")
        
    except Exception as e:
        logger.error(f"Background dynamic scenario processing failed: {e}")
        error_message = {
            "type": "scenario_error",
            "scenario_id": scenario_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast_to_topic('scenario_updates', json.dumps(error_message))

# API Routes

@app.get("/")
async def root():
    """Redirect to the Next.js frontend running on port 3001."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="http://localhost:3001", status_code=302)

@app.get("/api/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "service": "long-term-financial-planning"}

# Financial Configuration Management

@app.get("/api/financial-config")
async def get_financial_config(config_name: str = "default"):
    """Get financial configuration data."""
    try:
        config = await financial_config.get_financial_config(config_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Financial config '{config_name}' not found")
        return config
    except Exception as e:
        logger.error(f"Failed to get financial config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/financial-config/house-data")
async def get_house_data(config_name: str = "default"):
    """Get house data from financial configuration."""
    try:
        houses = await financial_config.get_house_data(config_name)
        if not houses:
            raise HTTPException(status_code=404, detail=f"House data not found for config '{config_name}'")
        return houses
    except Exception as e:
        logger.error(f"Failed to get house data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Administrative Configuration Management

@app.put("/api/admin/financial-config/house-data")
async def update_house_data(house_updates: Dict[str, Any], config_name: str = "default"):
    """Update house data in financial configuration."""
    try:
        # Update house data in database
        updated_count = await financial_config.update_house_data(config_name, house_updates)
        
        if updated_count == 0:
            raise HTTPException(status_code=404, detail=f"No house data found for config '{config_name}'")
        
        # Get updated data
        updated_houses = await financial_config.get_house_data(config_name)
        
        # Notify WebSocket subscribers of the update
        await manager.notify_config_update("house_data", updated_houses)
        
        logger.info(f"Updated house data for config '{config_name}'")
        return {"message": "House data updated successfully", "data": updated_houses}
    except Exception as e:
        logger.error(f"Failed to update house data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/financial-config/tax-rates")
async def update_tax_rates(tax_rates: Dict[str, float], config_name: str = "default"):
    """Update tax rates in financial configuration."""
    try:
        updated_count = await financial_config.update_tax_rates(config_name, tax_rates)
        
        if updated_count == 0:
            raise HTTPException(status_code=404, detail=f"Tax rates not found for config '{config_name}'")
        
        # Notify WebSocket subscribers
        await manager.notify_config_update("tax_rates", tax_rates)
        
        logger.info(f"Updated tax rates for config '{config_name}'")
        return {"message": "Tax rates updated successfully", "data": tax_rates}
    except Exception as e:
        logger.error(f"Failed to update tax rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/financial-config/backup")
async def backup_financial_config(config_name: str = "default"):
    """Create a backup of the financial configuration."""
    try:
        config = await financial_config.get_financial_config(config_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Financial config '{config_name}' not found")
        
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "config_name": config_name,
            "config_data": config
        }
        
        return backup_data
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scenario Management Endpoints

@app.post("/api/scenarios/generate")
async def generate_scenario(scenario_params: Dict[str, Any]):
    """Generate a new scenario based on dynamic parameters."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        logger.info(f"Generating scenario with params: {scenario_params}")
        
        # Create dynamic scenario in database
        scenario_id = await scenario_manager.create_dynamic_scenario(scenario_params)
        
        # Get the created scenario
        scenario = await scenario_manager.get_dynamic_scenario(scenario_id)
        
        if not scenario:
            raise HTTPException(status_code=500, detail="Failed to retrieve created scenario")
        
        logger.info(f"Created dynamic scenario: {scenario['name']} ({scenario_id})")
        return {
            "scenario": {
                "id": scenario['id'],
                "name": scenario['name'],
                "location": scenario['location'],
                "spouse1Status": scenario['spouse1_status'],
                "spouse2Status": scenario['spouse2_status'],
                "housing": scenario['housing'],
                "schoolType": scenario['school_type'],
                "projectionYears": scenario['projection_years'],
                "status": scenario['status'],
                "created_at": scenario['created_at']
            },
            "generated": True,
            "message": "Dynamic scenario created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/run")
async def run_scenario(scenario_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Run a scenario and return projection results."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenario_id = scenario_data.get('id')
        scenario_name = scenario_data.get('name', 'Unknown Scenario')
        
        if not scenario_id:
            raise HTTPException(status_code=400, detail="Scenario ID is required")
        
        logger.info(f"Running dynamic scenario: {scenario_name} ({scenario_id})")
        
        # Add background task to process the dynamic scenario
        background_tasks.add_task(process_dynamic_scenario_background, scenario_id)
        
        return {
            "message": f"Scenario '{scenario_name}' started running",
            "status": "running",
            "scenario_id": scenario_id,
            "scenario_name": scenario_name
        }
        
    except Exception as e:
        logger.error(f"Failed to run scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/compare")
async def compare_scenarios(comparison_data: Dict[str, Any]):
    """Compare multiple scenarios and return comparison results."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenarios = comparison_data.get('scenarios', [])
        if len(scenarios) < 2:
            raise HTTPException(status_code=400, detail="At least 2 scenarios required for comparison")
        
        if len(scenarios) > 4:
            raise HTTPException(status_code=400, detail="Maximum 4 scenarios allowed for comparison")
        
        # Extract scenario IDs
        scenario_ids = [s.get('id') for s in scenarios if s.get('id')]
        
        if len(scenario_ids) != len(scenarios):
            raise HTTPException(status_code=400, detail="All scenarios must have valid IDs")
        
        logger.info(f"Comparing {len(scenario_ids)} dynamic scenarios: {scenario_ids}")
        
        # Use the database comparison function
        comparison_results = await scenario_manager.compare_dynamic_scenarios(scenario_ids)
        
        if 'error' in comparison_results:
            raise HTTPException(status_code=400, detail=comparison_results['error'])
        
        logger.info(f"Generated comparison for {len(scenario_ids)} scenarios")
        return comparison_results
        
    except Exception as e:
        logger.error(f"Failed to compare scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dynamic Scenario Management Endpoints

@app.get("/api/dynamic-scenarios")
async def get_dynamic_scenarios(limit: int = 50):
    """Get all dynamic scenarios."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenarios = await scenario_manager.list_dynamic_scenarios(limit)
        logger.info(f"Retrieved {len(scenarios)} dynamic scenarios")
        return scenarios
        
    except Exception as e:
        logger.error(f"Failed to get dynamic scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dynamic-scenarios/{scenario_id}")
async def get_dynamic_scenario(scenario_id: str):
    """Get a specific dynamic scenario by ID."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenario = await scenario_manager.get_dynamic_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Dynamic scenario '{scenario_id}' not found")
        
        return scenario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dynamic scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/dynamic-scenarios/{scenario_id}")
async def update_dynamic_scenario(scenario_id: str, updates: Dict[str, Any]):
    """Update a dynamic scenario."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        success = await scenario_manager.update_dynamic_scenario(scenario_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail=f"Dynamic scenario '{scenario_id}' not found")
        
        # Get updated scenario
        updated_scenario = await scenario_manager.get_dynamic_scenario(scenario_id)
        return {
            "message": "Dynamic scenario updated successfully",
            "scenario": updated_scenario
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dynamic scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/dynamic-scenarios/{scenario_id}")
async def delete_dynamic_scenario(scenario_id: str):
    """Delete a dynamic scenario."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        success = await scenario_manager.delete_dynamic_scenario(scenario_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Dynamic scenario '{scenario_id}' not found")
        
        return {"message": "Dynamic scenario deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dynamic scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios")
async def get_scenarios():
    """Get all scenarios."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenarios = await scenario_manager.get_all_scenarios()
        
        # Enhance scenarios with line items if expense service is available
        logger.info(f"*** EXPENSE ENHANCEMENT CHECK: expense_service available = {expense_service is not None}")
        if expense_service:
            logger.info(f"*** PROCESSING {len(scenarios)} scenarios for enhancement")
            for scenario in scenarios:
                try:
                    scenario_id = scenario.get('id', 'unknown')
                    logger.info(f"*** Processing scenario {scenario_id}")
                    logger.info(f"*** user_data type: {type(scenario.get('user_data'))}")
                    
                    if isinstance(scenario.get('user_data'), str):
                        logger.info(f"*** Parsing JSON user_data for scenario {scenario_id}")
                        user_data = json.loads(scenario['user_data'])
                        if 'expenses' in user_data:
                            logger.info(f"*** ENHANCING {len(user_data['expenses'])} expenses for scenario {scenario_id}")
                            original_expense_names = [e.get('name') for e in user_data['expenses']]
                            logger.info(f"*** Original expense names: {original_expense_names}")
                            user_data['expenses'] = expense_service.enhance_expense_list(user_data['expenses'])
                            enhanced_expenses_with_line_items = [e.get('name') for e in user_data['expenses'] if 'line_items' in e]
                            logger.info(f"*** Enhanced expenses with line_items: {enhanced_expenses_with_line_items}")
                            scenario['user_data'] = json.dumps(user_data)
                        else:
                            logger.info(f"*** No expenses found in user_data for scenario {scenario_id}")
                    elif isinstance(scenario.get('user_data'), dict) and 'expenses' in scenario['user_data']:
                        logger.info(f"*** ENHANCING {len(scenario['user_data']['expenses'])} expenses for scenario {scenario_id} (dict)")
                        scenario['user_data']['expenses'] = expense_service.enhance_expense_list(scenario['user_data']['expenses'])
                    else:
                        logger.info(f"*** No valid user_data structure for scenario {scenario_id}")
                except Exception as e:
                    logger.error(f"*** Failed to enhance expenses for scenario {scenario.get('id')}: {e}")
                    import traceback
                    logger.error(f"*** Traceback: {traceback.format_exc()}")
        else:
            logger.error("*** EXPENSE SERVICE NOT AVAILABLE!")
        
        return scenarios
    except Exception as e:
        logger.error(f"Failed to get scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get a specific scenario by ID."""
    try:
        if not scenario_manager:
            raise HTTPException(status_code=500, detail="Scenario manager not initialized")
        
        scenario = await scenario_manager.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
        
        # Enhance scenario with line items if expense service is available
        if expense_service:
            try:
                if isinstance(scenario.get('user_data'), str):
                    user_data = json.loads(scenario['user_data'])
                    if 'expenses' in user_data:
                        logger.info(f"Enhancing {len(user_data['expenses'])} expenses for scenario {scenario_id}")
                        user_data['expenses'] = expense_service.enhance_expense_list(user_data['expenses'])
                        scenario['user_data'] = json.dumps(user_data)
                elif isinstance(scenario.get('user_data'), dict) and 'expenses' in scenario['user_data']:
                    logger.info(f"Enhancing {len(scenario['user_data']['expenses'])} expenses for scenario {scenario_id} (dict)")
                    scenario['user_data']['expenses'] = expense_service.enhance_expense_list(scenario['user_data']['expenses'])
            except Exception as e:
                logger.error(f"Failed to enhance expenses for scenario {scenario_id}: {e}")
        
        return scenario
    except Exception as e:
        logger.error(f"Failed to get scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Expense Service Endpoints

@app.get("/api/expenses/line-items")
async def get_all_line_items():
    """Get all available expense line items with categories and metadata."""
    try:
        if not expense_service:
            raise HTTPException(status_code=500, detail="Expense service not initialized")
        
        line_items = expense_service.get_all_available_line_items()
        return {
            "line_items": line_items,
            "categories": list(set([item['category'] for item in line_items.values()])),
            "total_categories": len(line_items)
        }
    except Exception as e:
        logger.error(f"Failed to get line items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/analyze")
async def analyze_expenses(expense_data: Dict[str, Any]):
    """Analyze expense breakdown with detailed categorization."""
    try:
        if not expense_service:
            raise HTTPException(status_code=500, detail="Expense service not initialized")
        
        expenses = expense_data.get('expenses', [])
        if not expenses:
            raise HTTPException(status_code=400, detail="No expenses provided")
        
        analysis = expense_service.analyze_expense_breakdown(expenses)
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/optimize")
async def optimize_expenses(optimization_data: Dict[str, Any]):
    """Generate expense optimization suggestions."""
    try:
        if not expense_service:
            raise HTTPException(status_code=500, detail="Expense service not initialized")
        
        expenses = optimization_data.get('expenses', [])
        target_reduction = optimization_data.get('target_reduction_percent', 10.0)
        
        if not expenses:
            raise HTTPException(status_code=400, detail="No expenses provided")
        
        suggestions = expense_service.generate_expense_optimization_suggestions(
            expenses, target_reduction
        )
        return suggestions
    except Exception as e:
        logger.error(f"Failed to generate optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/location-comparison")
async def compare_expenses_by_location(comparison_data: Dict[str, Any]):
    """Compare expenses across different locations."""
    try:
        if not expense_service:
            raise HTTPException(status_code=500, detail="Expense service not initialized")
        
        expenses = comparison_data.get('expenses', [])
        locations = comparison_data.get('locations', ['Sf', 'Sd', 'Mn'])
        
        if not expenses:
            raise HTTPException(status_code=400, detail="No expenses provided")
        
        comparison = expense_service.compare_expenses_across_locations(expenses, locations)
        return comparison
    except Exception as e:
        logger.error(f"Failed to compare expenses by location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/location-adjust")
async def adjust_expense_for_location(adjustment_data: Dict[str, Any]):
    """Adjust individual expense for specific location."""
    try:
        if not expense_service:
            raise HTTPException(status_code=500, detail="Expense service not initialized")
        
        expense = adjustment_data.get('expense', {})
        location = adjustment_data.get('location', 'Sf')
        
        if not expense:
            raise HTTPException(status_code=400, detail="No expense provided")
        
        adjusted_expense = expense_service.get_location_adjusted_expense(expense, location)
        return {
            "original": expense,
            "adjusted": adjusted_expense,
            "location": location
        }
    except Exception as e:
        logger.error(f"Failed to adjust expense for location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Life Planning Decision Engine Endpoints

@app.post("/api/life-planning/move-analysis")
async def analyze_move_timing(planning_data: Dict[str, Any]):
    """Analyze optimal timing for moving with education and family considerations."""
    try:
        # Extract data
        children_data = planning_data.get('children', [])
        current_income = planning_data.get('current_annual_income', 500000)
        current_expenses = planning_data.get('current_annual_expenses', 200000)
        analysis_years = planning_data.get('analysis_years', 10)
        
        # Convert children data to Child objects
        children = []
        for child_data in children_data:
            child = Child(
                name=child_data.get('name', 'Child'),
                current_age=child_data.get('current_age', 10),
                current_grade=child_data.get('current_grade', 5)
            )
            children.append(child)
        
        if not children:
            # Default child for testing
            children = [Child(name="Child", current_age=12, current_grade=7)]
        
        # Run analysis
        analysis = life_planning_service.analyze_move_timing_scenarios(
            children=children,
            current_annual_income=current_income,
            current_annual_expenses=current_expenses,
            analysis_years=analysis_years
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze move timing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/life-planning/location-profiles")
async def get_location_profiles():
    """Get detailed profiles of all available locations for comparison."""
    try:
        profiles = {}
        for location_key, location in life_planning_service.locations.items():
            profiles[location_key] = {
                'name': location.name,
                'display_name': location.display_name,
                'cost_multipliers': location.cost_multipliers,
                'education_costs': location.education_costs,
                'housing_cost_difference': location.housing_cost_difference,
                'moving_costs': location.moving_costs,
                'job_income_impact': location.job_income_impact,
                'quality_of_life_score': location.quality_of_life_score
            }
        
        return {
            'locations': profiles,
            'current_year': life_planning_service.current_year
        }
    except Exception as e:
        logger.error(f"Failed to get location profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/life-planning/education-cost-analysis")
async def analyze_education_costs(education_data: Dict[str, Any]):
    """Analyze education costs over time for different scenarios."""
    try:
        children_data = education_data.get('children', [])
        locations = education_data.get('locations', ['current', 'sd', 'mn'])
        education_types = education_data.get('education_types', ['public', 'private'])
        
        # Convert children data
        children = []
        for child_data in children_data:
            child = Child(
                name=child_data.get('name', 'Child'),
                current_age=child_data.get('current_age', 10),
                current_grade=child_data.get('current_grade', 5)
            )
            children.append(child)
        
        results = {}
        current_year = life_planning_service.current_year
        
        for location_key in locations:
            if location_key not in life_planning_service.locations:
                continue
                
            location = life_planning_service.locations[location_key]
            results[location_key] = {
                'display_name': location.display_name,
                'education_scenarios': {}
            }
            
            for edu_type in education_types:
                if edu_type not in location.education_costs:
                    continue
                    
                yearly_costs = []
                total_cost = 0
                
                # Calculate costs for next 15 years
                for year_offset in range(15):
                    year = current_year + year_offset
                    year_cost = 0
                    
                    for child in children:
                        child_grade = child.grade_in_year(year)
                        if 1 <= child_grade <= 12:  # K-12
                            school_level = child.school_level_in_year(year).value
                            if school_level in location.education_costs[edu_type]:
                                cost = location.education_costs[edu_type][school_level]
                                year_cost += cost
                                total_cost += cost
                    
                    yearly_costs.append({
                        'year': year,
                        'annual_cost': year_cost,
                        'children_in_school': [
                            {
                                'name': child.name,
                                'age': child.age_in_year(year),
                                'grade': child.grade_in_year(year),
                                'school_level': child.school_level_in_year(year).value
                            }
                            for child in children if 1 <= child.grade_in_year(year) <= 12
                        ]
                    })
                
                results[location_key]['education_scenarios'][edu_type] = {
                    'yearly_breakdown': yearly_costs,
                    'total_15_year_cost': total_cost,
                    'average_annual_cost': total_cost / 15 if total_cost > 0 else 0,
                    'peak_year_cost': max(yearly_costs, key=lambda x: x['annual_cost']) if yearly_costs else None
                }
        
        return {
            'analysis': results,
            'children_profiles': [
                {
                    'name': child.name,
                    'current_age': child.current_age,
                    'current_grade': child.current_grade,
                    'graduation_year': current_year + (12 - child.current_grade)
                }
                for child in children
            ],
            'summary': {
                'analysis_period': f"{current_year}-{current_year + 14}",
                'locations_compared': len(results),
                'education_types_compared': len(education_types)
            }
        }
    except Exception as e:
        logger.error(f"Failed to analyze education costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoints

@app.websocket("/ws/config-updates")
async def websocket_config_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time configuration updates."""
    logger.info("WebSocket connection attempt to /ws/config-updates")
    try:
        # Add origin checking for security (but allow localhost during development)
        origin = websocket.headers.get("origin", "")
        logger.info(f"WebSocket connection from origin: {origin}")
        
        await manager.connect(websocket, topic='config_updates')
        logger.info("WebSocket connected successfully")
        
        # Send initial connection confirmation
        await manager.send_personal_message(json.dumps({
            "type": "connection_established",
            "message": "Connected to config updates",
            "timestamp": datetime.now().isoformat()
        }), websocket)
        
        while True:
            # Keep connection alive and handle any client messages
            try:
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")
                
                # Echo back for heartbeat
                if data == "ping":
                    await manager.send_personal_message("pong", websocket)
                    logger.info("Sent pong response")
            except Exception as msg_error:
                logger.warning(f"Error receiving WebSocket message: {msg_error}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(websocket)

@app.websocket("/ws/scenario-updates")
async def websocket_scenario_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time scenario updates."""
    logger.info("WebSocket connection attempt to /ws/scenario-updates")
    try:
        origin = websocket.headers.get("origin", "")
        logger.info(f"WebSocket connection from origin: {origin}")
        
        await manager.connect(websocket, topic='scenario_updates')
        logger.info("WebSocket connected to scenario updates successfully")
        
        # Send initial connection confirmation
        await manager.send_personal_message(json.dumps({
            "type": "connection_established",
            "message": "Connected to scenario updates",
            "timestamp": datetime.now().isoformat()
        }), websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Received scenario WebSocket message: {data}")
                
                if data == "ping":
                    await manager.send_personal_message("pong", websocket)
                    logger.info("Sent pong response")
            except Exception as msg_error:
                logger.warning(f"Error receiving scenario WebSocket message: {msg_error}")
                break
                
    except WebSocketDisconnect:
        logger.info("Scenario WebSocket disconnected normally")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Scenario WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8006,
        reload=False,
        log_level="info"
    )