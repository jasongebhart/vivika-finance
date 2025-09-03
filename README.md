# Long-Term Financial Planning & Projection Application

A sophisticated financial planning application built with FastAPI (Python backend) and React (frontend), designed for comprehensive long-term financial modeling, Monte Carlo simulations, and scenario analysis.

## 🎯 Overview

This application provides advanced financial planning capabilities including:
- **Scenario Modeling**: Create and compare different financial scenarios
- **Monte Carlo Simulations**: Probabilistic analysis of retirement outcomes
- **Cost-of-Living Analysis**: Compare financial impact of city relocations
- **Education Planning**: Project and plan for education expenses
- **Vehicle Ownership Analysis**: Total cost of ownership calculations
- **Real-time Updates**: WebSocket-powered simulation progress tracking

## ✨ Features

### 🏗️ Scenario Builder
- Multi-step wizard for creating comprehensive financial scenarios
- Support for retirement, relocation, education, and major purchase scenarios
- Dynamic form fields based on scenario type
- Integration with React Hook Form for advanced validation

### 📊 Monte Carlo Simulations
- Sophisticated probability modeling with configurable parameters
- Interactive D3.js visualizations with probability bands
- Real-time progress updates via WebSocket connections
- Statistical analysis with confidence intervals and percentiles
- Withdrawal strategy analysis for retirement planning

### 📈 Financial Projections
- Comprehensive yearly projections with multiple visualization modes
- Interactive charts for net worth, cash flow, tax analysis, and retirement planning
- Scenario comparison capabilities
- Goal achievement probability analysis

### 🗺️ Cost-of-Living Comparison
- Interactive city comparison with detailed cost breakdowns
- Long-term financial impact analysis (10-year and retirement)  
- Visual cost index indicators and mapping
- Integration with external data services

### 🎓 Education Expense Planning
- Inflation-adjusted education cost projections
- Multiple institution types and savings strategies
- Timeline visualization with savings milestones
- 529 plan and other tax-advantaged account recommendations

### 🚗 Vehicle Ownership Analysis
- Comprehensive total cost of ownership calculations
- Comparison across different vehicle types and regions
- Depreciation modeling and financing cost analysis
- Annual cost projections and cost-per-mile calculations

## 🛠️ Technology Stack

### Backend (FastAPI)
- **FastAPI**: Modern async web framework for high-performance APIs
- **Pydantic**: Data validation and serialization with type hints
- **SQLite**: Lightweight database for scenario and projection storage
- **AsyncIO**: Asynchronous support for compute-intensive operations
- **WebSockets**: Real-time communication for simulation updates
- **HTTPX**: Async HTTP client for external data integration

### Frontend (React)
- **React 18**: Modern UI framework with hooks and concurrent features
- **Styled Components**: CSS-in-JS for dynamic styling and theming
- **D3.js**: Advanced data visualizations and interactive charts
- **Plotly.js**: Statistical charts and scientific plotting
- **React Hook Form**: Sophisticated form handling and validation
- **React Select**: Enhanced select components for city/option selection

### Financial Modeling
- **Monte Carlo Engine**: Probabilistic simulation with configurable parameters
- **Scenario Management**: CRUD operations for financial scenarios
- **External Data Integration**: APIs for cost-of-living, education, and market data
- **Projection Calculations**: Deterministic and stochastic financial modeling

## 📁 Project Structure

```
vivikafinance/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── scenarios.db               # SQLite database (created at runtime)
│
├── models/                    # Pydantic data models
│   └── financial_models.py    # Comprehensive financial data structures
│
├── services/                  # Core business logic services
│   ├── scenario_manager.py    # Scenario CRUD and projection calculations
│   ├── monte_carlo_engine.py  # Monte Carlo simulation engine
│   └── external_data_service.py # External API integration
│
├── tests/                     # Comprehensive test suite
│   ├── conftest.py           # Pytest configuration and fixtures
│   ├── test_scenario_manager.py
│   ├── test_monte_carlo_engine.py
│   ├── test_external_data_service.py
│   └── test_main_api.py
│
└── frontend-modern/          # Next.js React application
    ├── package.json          # Node.js dependencies
    ├── public/               # Static assets
    ├── src/
    │   ├── app/              # Next.js App Router
    │   │   ├── page.tsx      # Home page
    │   │   ├── layout.tsx    # Root layout
    │   │   ├── scenarios/    # Scenario management pages
    │   │   ├── forecasting/  # Financial forecasting
    │   │   └── admin/        # Admin configuration
    │   ├── components/       # Reusable React components
    │   │   ├── ui/           # UI components (shadcn/ui)
    │   │   └── features/     # Feature-specific components
    │   ├── hooks/            # Custom React hooks
    │   ├── lib/              # Utility libraries
    │   └── types/            # TypeScript type definitions
    └── next.config.ts        # Next.js configuration
```

## 🚀 Installation & Setup

### 📋 Quick Start Options

**Option 1: Production Deployment (Recommended for regular use)**
```bash
# Automated deployment to separate directory
python deploy.py "C:\FinancePlanner" --include-data
cd "C:\FinancePlanner"
start_production.bat  # Windows
# ./start_production.sh  # Unix/Mac
```

**Option 2: Full Stack Development (Recommended for development)**
```powershell
# Quick development startup
.\start-dev.ps1

# Full featured startup with checks
.\start-full-stack.ps1

# Complete production-ready setup
.\launch-complete.ps1

# Or manually:
python main.py  # Backend (Port 8006)
cd frontend-modern && npm run dev  # Frontend (Port 3000)
```

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide**

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone and navigate to the directory**
   ```bash
   cd G:\jason\git\DataAndTools\vivikafinance
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8006`

### Frontend Setup (Next.js)

1. **Navigate to frontend directory**
   ```bash
   cd frontend-modern
   ```

2. **Install Node dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The application will open at `http://localhost:3000`

### Production Build

1. **Build the React application**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve through FastAPI**
   The FastAPI app is configured to serve the built React app from the `/` route.

## 📥 Importing Private Data

### Secure Data Import
Your financial scenarios can be imported securely from JSON files:

```bash
# Show example JSON structure
python import_scenarios.py --example

# Validate your data format
python import_scenarios.py --validate my_scenarios.json

# Import your private scenarios
python import_scenarios.py my_scenarios.json
```

### Data Security
- ✅ All private data files are excluded from git (`.gitignore`)
- ✅ Database files are not tracked in version control
- ✅ Personal financial information stays completely local
- ✅ Production deployment separates data from source code

📖 **See [IMPORT_GUIDE.md](IMPORT_GUIDE.md) for detailed import instructions**

## 🔧 API Endpoints

### Core Scenario Management
- `GET /api/health` - API health check
- `POST /api/scenarios` - Create new financial scenario
- `GET /api/scenarios` - List all scenarios
- `GET /api/scenarios/{id}` - Get specific scenario
- `POST /api/scenarios/{id}/project` - Run financial projection
- `POST /api/scenarios/compare` - Compare multiple scenarios

### Data Import/Export
- `POST /api/scenarios/import` - Import scenarios from JSON
- `GET /api/export/scenarios` - Export all scenarios to JSON

### Monte Carlo Simulations
- `POST /api/monte-carlo/{scenario_id}` - Run Monte Carlo simulation
- `POST /api/withdrawal-strategies/{scenario_id}` - Analyze withdrawal strategies
- `WS /ws/simulation/{scenario_id}` - Real-time simulation updates

### Cost-of-Living Analysis
- `GET /api/city-comparison/{current}/{target}` - Compare cities
- `GET /api/city-data/{city_name}` - Get city cost data

### Specialized Analysis
- `POST /api/education-projection` - Project education expenses
- `POST /api/vehicle-analysis` - Analyze vehicle ownership costs
- `POST /api/goals/analyze` - Analyze financial goal feasibility

### External Data
- `GET /api/external-data/inflation` - Current inflation data
- `GET /api/external-data/market` - Current market data

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=services --cov=models

# Run specific test categories
python -m pytest -m "not slow"  # Skip slow tests
python -m pytest -m monte_carlo  # Run only Monte Carlo tests
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### Test Categories
- **Unit Tests**: Individual component and service testing
- **Integration Tests**: End-to-end scenario testing
- **Performance Tests**: Monte Carlo simulation benchmarks
- **API Tests**: FastAPI endpoint testing

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///scenarios.db

# External APIs (when implementing real integrations)
NUMBEO_API_KEY=your-numbeo-api-key
BLS_API_KEY=your-bls-api-key
FRED_API_KEY=your-fred-api-key

# Application Settings
MONTE_CARLO_MAX_SIMULATIONS=10000
CACHE_DURATION_HOURS=24
```

### Application Configuration
- **Simulation Parameters**: Configurable via API and UI
- **Cache Settings**: External data caching duration
- **WebSocket Settings**: Connection timeout and retry logic
- **Visualization Settings**: Chart themes and display options

## 🏗️ Core Components

### Scenario Builder
Multi-step wizard supporting:
- Basic information and scenario type selection
- Comprehensive financial profile input
- Scenario-specific configuration
- Financial assumptions and parameters

### Monte Carlo Visualization
Advanced D3.js visualizations including:
- Probability bands over time
- Distribution histograms
- Interactive confidence intervals
- Withdrawal strategy comparisons

### Projection Charts
Comprehensive financial projections with:
- Net worth tracking over time
- Income vs. expense analysis
- Tax burden calculations
- Retirement planning visualizations

## 🎨 Key Features

### Real-time Updates
- WebSocket integration for live simulation progress
- Automatic reconnection with exponential backoff
- Progress bars and status indicators
- Error handling and recovery

### Interactive Visualizations
- D3.js-powered probability charts
- Plotly.js statistical visualizations
- Responsive design for all screen sizes
- Export capabilities for charts and data

### Advanced Financial Modeling
- Monte Carlo simulations with configurable parameters
- Inflation-adjusted projections
- Tax-aware calculations
- Multi-scenario comparisons

## 🔐 Security Considerations

- **Input Validation**: Comprehensive Pydantic model validation
- **Data Sanitization**: Protection against injection attacks  
- **CORS Configuration**: Properly configured cross-origin requests
- **Environment Variables**: Secure credential management
- **Rate Limiting**: Protection against abuse (implement as needed)

## 🚀 Deployment

### Development
```bash
# Backend
python main.py

# Frontend
cd frontend && npm start
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Run with production WSGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker
docker build -t financial-planner .
docker run -p 8000:8000 financial-planner
```

## 📊 Performance

### Benchmarks
- **Monte Carlo Simulations**: 1000 simulations in ~2-5 seconds
- **Scenario Projections**: 30-year projections in <100ms
- **API Response Times**: <200ms for most endpoints
- **WebSocket Latency**: <50ms for real-time updates

### Optimization Features
- **Async Processing**: Non-blocking simulation execution
- **Caching**: External data cached for 24 hours
- **Database Indexing**: Optimized queries for scenario retrieval
- **Lazy Loading**: Components loaded on demand

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with comprehensive tests
4. Run the test suite (`pytest` and `npm test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Maintain test coverage above 80%
- Update documentation for new features
- Add type hints for all Python functions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or feature requests:

1. **Check Documentation**: Review this README and API documentation
2. **Search Issues**: Check existing GitHub issues
3. **Create Issue**: Provide detailed information and reproduction steps
4. **Discussions**: Use GitHub Discussions for general questions

## 🙏 Acknowledgments

- **FastAPI**: For the excellent async web framework
- **React Community**: For the robust frontend ecosystem
- **D3.js**: For powerful data visualization capabilities
- **Plotly**: For scientific and statistical charting
- **Financial Modeling**: Inspired by modern portfolio theory and Monte Carlo methods

---

**Built for comprehensive long-term financial planning with sophisticated modeling and visualization capabilities.**