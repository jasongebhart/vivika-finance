# Long-Term Financial Planning & Projection Application - Modern Frontend

A cutting-edge, visually stunning, and highly intuitive financial planning application built with Next.js 14, TypeScript, and modern web technologies. This application provides comprehensive financial modeling, scenario analysis, and Monte Carlo simulations for long-term financial planning.

## 🚀 Features

### 🏠 **Interactive Dashboard**
- Real-time financial metrics with animated cards
- Net worth projection charts with interactive tooltips
- Quick actions for scenario creation and analysis
- Recent activity tracking
- Dark/light mode with smooth transitions

### 📊 **Advanced Scenario Management**
- Multi-step scenario builder with guided workflows
- Support for multiple scenario types (retirement, relocation, education, major purchases)
- Drag-and-drop scenario comparison
- Version history and scenario cloning
- Real-time validation and error handling

### 📈 **Sophisticated Data Visualization**
- **Recharts Integration**: Interactive line, area, and bar charts
- **Plotly.js**: Advanced 3D visualizations and scientific charts
- **D3.js**: Custom Monte Carlo probability distributions
- **Responsive Design**: Charts adapt to all screen sizes
- **Real-time Updates**: WebSocket-driven live data updates

### 🎯 **Monte Carlo Simulations**
- Portfolio evolution paths with confidence intervals
- 3D probability surface visualizations
- Success probability analysis over time
- Interactive distribution charts
- Customizable simulation parameters

### 🏢 **Cost of Living Analysis**
- Interactive city comparison tools
- Real-time cost-of-living data integration
- Impact analysis on financial projections
- Geographic data visualization

### 🎓 **Education & Major Expense Planning**
- Total cost of ownership calculators
- Education expense projections
- Vehicle ownership analysis
- Integration with overall financial scenarios

## 🛠 Tech Stack

### **Core Framework**
- **Next.js 14+**: React framework with App Router, SSR/SSG, and Turbopack
- **React 18+**: Latest React features with concurrent rendering
- **TypeScript 5+**: Type-safe development with strict configuration

### **Styling & UI**
- **Tailwind CSS 4**: Utility-first CSS with dark mode support
- **Headless UI**: Accessible, unstyled UI components
- **Radix UI**: Low-level UI primitives for complex components
- **Framer Motion**: Advanced animations and micro-interactions
- **Lucide React**: Modern, customizable icons

### **State Management & Data**
- **Zustand**: Lightweight, performant state management
- **TanStack Query**: Powerful data synchronization and caching
- **React Hook Form + Zod**: Type-safe form handling and validation
- **WebSocket**: Real-time simulation progress updates

### **Data Visualization**
- **Recharts**: React-native charting library
- **Plotly.js**: Scientific and 3D visualizations
- **D3.js**: Custom interactive visualizations
- **React Plotly.js**: React wrapper for Plotly

### **Development Tools**
- **ESLint + Prettier**: Code quality and formatting
- **Husky**: Git hooks for quality gates
- **Conventional Commits**: Standardized commit messages
- **Playwright**: End-to-end testing
- **Vitest**: Fast unit testing

## 📋 Prerequisites

- **Node.js 18+** (Latest LTS recommended)
- **npm 9+** or **pnpm 8+** or **yarn 3+**
- **Python 3.9+** (for backend API)
- **Git** for version control

## 🚀 Quick Start

### 1. **Clone and Install**

```bash
# Clone the repository
git clone <repository-url>
cd vivikafinance/frontend-modern

# Install dependencies
npm install
# or
pnpm install
# or
yarn install
```

### 2. **Environment Setup**

Create a `.env.local` file in the root directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Optional: Analytics and monitoring
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### 3. **Start the Backend**

Make sure the Python backend is running:

```bash
# From the project root
cd ../
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. **Start the Development Server**

```bash
npm run dev
# or
pnpm dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗 Development Scripts

```bash
# Development
npm run dev          # Start development server with Turbopack
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking

# Testing
npm run test         # Run unit tests with Vitest
npm run test:e2e     # Run end-to-end tests with Playwright
```

## 📁 Project Structure

```
frontend-modern/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css        # Global styles and CSS variables
│   │   ├── layout.tsx         # Root layout with providers
│   │   ├── page.tsx           # Home page
│   │   └── providers.tsx      # App providers (Query, Theme)
│   ├── components/
│   │   ├── ui/                # Base UI components (Button, Card, etc.)
│   │   ├── charts/            # Chart components
│   │   └── features/          # Feature-specific components
│   │       ├── dashboard/     # Dashboard components
│   │       ├── scenario-builder/ # Scenario creation
│   │       └── scenario-list/ # Scenario management
│   ├── hooks/                 # Custom React hooks
│   │   ├── use-scenarios.ts   # Scenario management hooks
│   │   └── use-toast.ts       # Toast notifications
│   ├── lib/                   # Utilities and configurations
│   │   ├── api.ts            # API client with interceptors
│   │   └── utils.ts          # Common utility functions
│   ├── stores/               # Zustand stores
│   │   └── app-store.ts      # Global application state
│   └── types/                # TypeScript type definitions
│       └── index.ts          # Shared types and interfaces
├── public/                   # Static assets
├── tailwind.config.js       # Tailwind CSS configuration
├── next.config.ts           # Next.js configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies and scripts
```

## 🎨 Design System

### **Color Palette**
The application uses a semantic color system that automatically adapts to light and dark modes:

- **Primary**: Blue (#3b82f6) - Interactive elements, links
- **Success**: Green (#10b981) - Positive values, success states  
- **Warning**: Orange (#f59e0b) - Alerts, cautions
- **Error**: Red (#ef4444) - Errors, negative values
- **Neutral**: Gray scales - Text, borders, backgrounds

### **Typography**
- **Font**: Inter (primary), system fonts fallback
- **Scale**: Fluid typography using clamp() functions
- **Hierarchy**: h1-h6 with consistent spacing and weights

### **Spacing & Layout**
- **Grid System**: CSS Grid with container queries
- **Spacing Scale**: 4px base unit (0.25rem increments)
- **Breakpoints**: Mobile-first responsive design
  - `sm`: 640px
  - `md`: 768px  
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px

### **Components**
All components follow:
- **Accessibility**: WCAG 2.2 AA compliance
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Motion**: Respects `prefers-reduced-motion`

## 🔌 API Integration

### **Backend Communication**
The frontend communicates with the Python backend through:

```typescript
// RESTful API
const scenarios = await apiClient.getScenarios()
const projection = await apiClient.runProjection(scenarioId)

// WebSocket for real-time updates
const ws = new WebSocketClient()
ws.connect(scenarioId, (data) => {
  // Handle real-time simulation progress
})
```

### **Error Handling**
- **Network Failures**: Automatic retry with exponential backoff
- **User Feedback**: Toast notifications for all operations
- **Offline Support**: Graceful degradation when API unavailable
- **Loading States**: Skeleton screens and progress indicators

### **Data Caching**
- **Query Caching**: TanStack Query with 5-minute stale time
- **Background Updates**: Automatic data synchronization
- **Optimistic Updates**: Immediate UI feedback
- **Invalidation**: Smart cache invalidation on mutations

## 🚀 Deployment

### **Build for Production**

```bash
# Create optimized build
npm run build

# Test production build locally
npm run start
```

### **Environment Variables**

For production deployment, set these environment variables:

```env
# Required
NEXT_PUBLIC_API_URL=https://api.yourfinanceplanner.com
NEXT_PUBLIC_WS_URL=wss://api.yourfinanceplanner.com

# Optional
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### **Deployment Platforms**

The application is optimized for deployment on:

- **Vercel** (Recommended): Zero-config deployment
- **Netlify**: Static site generation support
- **AWS Amplify**: Full-stack deployment
- **Docker**: Containerized deployment

## 🛡 Security

### **Data Protection**
- **HTTPS**: All communications encrypted
- **CSP Headers**: Content Security Policy implementation
- **XSS Protection**: Input sanitization and validation
- **CSRF Protection**: Token-based protection

### **API Security**
- **Authentication**: JWT tokens with refresh rotation
- **Authorization**: Role-based access control
- **Rate Limiting**: Request throttling
- **Input Validation**: Zod schema validation

## 🆘 Troubleshooting

### **Common Issues**

#### **Build Errors**
```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Type checking
npm run type-check
```

#### **API Connection Issues**
```bash
# Check backend status
curl http://localhost:8000/api/health

# Verify environment variables
echo $NEXT_PUBLIC_API_URL
```

## 📚 Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **TypeScript**: https://www.typescriptlang.org/docs
- **React Query**: https://tanstack.com/query/latest
- **Recharts**: https://recharts.org/en-US
- **Plotly.js**: https://plotly.com/javascript

## 📝 License

This project is licensed under the MIT License.

---

## 🚀 Ready to Transform Financial Planning?

This modern frontend represents the cutting edge of financial planning applications, combining sophisticated data visualization, intuitive user experience, and robust technical architecture. 

**Get started today and experience the future of financial planning!**

```bash
npm install && npm run dev
```
