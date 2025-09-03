# Design System & UI Style Guide
## Long-Term Financial Planning Application

This document outlines the comprehensive design system for the modern financial planning application, establishing visual language, component guidelines, and UX principles for a cutting-edge 2025+ user experience.

---

## 🎨 Visual Foundation

### Color System

Our color system is built on HSL values for precision and consistency across light and dark themes.

#### **Primary Palette**
```css
/* Primary - Used for interactive elements, CTAs, and brand identity */
--primary: 221 83% 53%;           /* #3b82f6 - Blue */
--primary-foreground: 210 40% 98%; /* #f8fafc - Light text on primary */

/* Secondary - Supporting elements and backgrounds */
--secondary: 210 40% 96%;          /* #f1f5f9 - Light gray */
--secondary-foreground: 222 84% 5%; /* #0f172a - Dark text on secondary */
```

#### **Semantic Colors**
```css
/* Success - Positive values, growth, achievements */
--success: 142 76% 36%;            /* #10b981 - Green */

/* Warning - Alerts, cautions, attention needed */
--warning: 38 92% 50%;             /* #f59e0b - Orange */

/* Error - Errors, negative values, destructive actions */
--destructive: 0 84% 60%;          /* #ef4444 - Red */

/* Info - Information, neutral highlights */
--info: 199 89% 48%;               /* #0ea5e9 - Sky blue */
```

#### **Neutral Palette**
```css
/* Backgrounds and surfaces */
--background: 0 0% 100%;           /* #ffffff - Pure white */
--foreground: 240 10% 4%;          /* #0f172a - Near black text */
--card: 0 0% 100%;                 /* #ffffff - Card backgrounds */
--popover: 0 0% 100%;              /* #ffffff - Popup backgrounds */

/* Borders and dividers */
--border: 214 32% 91%;             /* #e2e8f0 - Light gray borders */
--input: 214 32% 91%;              /* #e2e8f0 - Input borders */

/* Muted elements */
--muted: 210 40% 96%;              /* #f1f5f9 - Subtle backgrounds */
--muted-foreground: 215 16% 47%;   /* #64748b - Muted text */

/* Accents */
--accent: 210 40% 96%;             /* #f1f5f9 - Hover states */
--accent-foreground: 222 84% 5%;   /* #0f172a - Text on accents */
```

#### **Dark Mode Adaptations**
```css
.dark {
  --background: 240 10% 4%;         /* #0f172a - Dark background */
  --foreground: 0 0% 98%;           /* #f8fafc - Light text */
  --card: 240 10% 4%;               /* #0f172a - Dark cards */
  --border: 217 33% 18%;            /* #334155 - Dark borders */
  --muted: 217 33% 18%;             /* #334155 - Dark muted */
  --muted-foreground: 215 20% 65%;  /* #94a3b8 - Light muted text */
}
```

#### **Financial Data Colors**
```css
/* Chart colors optimized for financial data */
--chart-1: 12 76% 61%;             /* #e11d48 - Red (losses) */
--chart-2: 173 58% 39%;            /* #10b981 - Green (gains) */
--chart-3: 197 37% 24%;            /* #1e40af - Blue (neutral) */
--chart-4: 43 74% 66%;             /* #f59e0b - Orange (warnings) */
--chart-5: 27 87% 67%;             /* #8b5cf6 - Purple (projections) */
```

### Typography Scale

#### **Font Stack**
```css
/* Primary: Inter - Optimized for UI and data display */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;

/* Monospace: For numerical data and code */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

#### **Type Scale**
```css
/* Display - For hero sections and major headings */
.text-display-2xl { font-size: 4.5rem; line-height: 1; }    /* 72px */
.text-display-xl  { font-size: 3.75rem; line-height: 1; }   /* 60px */
.text-display-lg  { font-size: 3rem; line-height: 1.125; }  /* 48px */

/* Headlines - For section headers */
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; }      /* 36px */
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }    /* 30px */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }         /* 24px */
.text-xl  { font-size: 1.25rem; line-height: 1.75rem; }     /* 20px */

/* Body text */
.text-lg   { font-size: 1.125rem; line-height: 1.75rem; }   /* 18px */
.text-base { font-size: 1rem; line-height: 1.5rem; }        /* 16px */
.text-sm   { font-size: 0.875rem; line-height: 1.25rem; }   /* 14px */
.text-xs   { font-size: 0.75rem; line-height: 1rem; }       /* 12px */
```

#### **Font Weights**
```css
.font-light     { font-weight: 300; }  /* Light */
.font-normal    { font-weight: 400; }  /* Regular */
.font-medium    { font-weight: 500; }  /* Medium */
.font-semibold  { font-weight: 600; }  /* Semibold */
.font-bold      { font-weight: 700; }  /* Bold */
.font-extrabold { font-weight: 800; }  /* Extra Bold */
```

### Spacing System

#### **Base Unit: 4px (0.25rem)**
Our spacing system uses a 4px base unit for consistency and visual rhythm.

```css
/* Spacing scale */
.p-0   { padding: 0; }           /* 0px */
.p-1   { padding: 0.25rem; }     /* 4px */
.p-2   { padding: 0.5rem; }      /* 8px */
.p-3   { padding: 0.75rem; }     /* 12px */
.p-4   { padding: 1rem; }        /* 16px */
.p-6   { padding: 1.5rem; }      /* 24px */
.p-8   { padding: 2rem; }        /* 32px */
.p-12  { padding: 3rem; }        /* 48px */
.p-16  { padding: 4rem; }        /* 64px */
.p-24  { padding: 6rem; }        /* 96px */
```

### Border Radius

```css
.rounded-none { border-radius: 0; }
.rounded-sm   { border-radius: 0.125rem; }  /* 2px */
.rounded      { border-radius: 0.25rem; }   /* 4px */
.rounded-md   { border-radius: 0.375rem; }  /* 6px */
.rounded-lg   { border-radius: 0.5rem; }    /* 8px */
.rounded-xl   { border-radius: 0.75rem; }   /* 12px */
.rounded-2xl  { border-radius: 1rem; }      /* 16px */
.rounded-3xl  { border-radius: 1.5rem; }    /* 24px */
.rounded-full { border-radius: 9999px; }
```

### Shadows

```css
/* Elevation system for depth and hierarchy */
.shadow-sm    { box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
.shadow       { box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }
.shadow-md    { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }
.shadow-lg    { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }
.shadow-xl    { box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
.shadow-2xl   { box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
```

---

## 🧩 Component Library

### Button Components

#### **Primary Button**
Used for main actions and CTAs.

```tsx
<Button variant="default" size="default">
  Create Scenario
</Button>
```

**Variants:**
- `default` - Primary action button
- `destructive` - Dangerous actions (delete, remove)
- `outline` - Secondary actions
- `secondary` - Supporting actions
- `ghost` - Minimal, subtle actions
- `link` - Text-only links

**Sizes:**
- `default` - Standard 36px height
- `sm` - Compact 32px height
- `lg` - Prominent 40px height
- `icon` - Square icon button

#### **Button States**
```css
/* Default state */
.button-default {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  transition: all 0.2s ease-in-out;
}

/* Hover state */
.button-default:hover {
  background: hsl(var(--primary) / 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px hsl(var(--primary) / 0.4);
}

/* Active state */
.button-default:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px hsl(var(--primary) / 0.4);
}

/* Disabled state */
.button-default:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

### Card Components

#### **Base Card**
Container for content grouping with subtle elevation.

```tsx
<Card>
  <CardHeader>
    <CardTitle>Net Worth Projection</CardTitle>
    <CardDescription>Your financial growth over time</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    {/* Actions */}
  </CardFooter>
</Card>
```

#### **Interactive Cards**
Cards with hover effects for clickable content.

```css
.card-interactive {
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
```

### Form Components

#### **Input Fields**
```tsx
<div className="form-group">
  <label htmlFor="salary">Annual Salary</label>
  <Input
    id="salary"
    type="number"
    placeholder="75000"
    className="form-input"
  />
  <FormHelp>Enter your current annual salary before taxes</FormHelp>
</div>
```

#### **Form Validation States**
```css
/* Default input */
.form-input {
  border: 1px solid hsl(var(--border));
  transition: border-color 0.2s ease-in-out;
}

/* Focus state */
.form-input:focus {
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 3px hsl(var(--primary) / 0.1);
}

/* Error state */
.form-input[aria-invalid="true"] {
  border-color: hsl(var(--destructive));
  box-shadow: 0 0 0 3px hsl(var(--destructive) / 0.1);
}

/* Success state */
.form-input[data-valid="true"] {
  border-color: hsl(var(--success));
  box-shadow: 0 0 0 3px hsl(var(--success) / 0.1);
}
```

### Data Display Components

#### **Metric Cards**
For displaying key financial metrics.

```tsx
<MetricCard
  title="Net Worth"
  value="$285,000"
  change={8.5}
  changeLabel="from last month"
  trend="up"
  icon={<DollarSign />}
/>
```

#### **Status Badges**
```css
/* Success badge */
.badge-success {
  background: hsl(var(--success) / 0.1);
  color: hsl(var(--success));
  border: 1px solid hsl(var(--success) / 0.2);
}

/* Warning badge */
.badge-warning {
  background: hsl(var(--warning) / 0.1);
  color: hsl(var(--warning));
  border: 1px solid hsl(var(--warning) / 0.2);
}

/* Error badge */
.badge-error {
  background: hsl(var(--destructive) / 0.1);
  color: hsl(var(--destructive));
  border: 1px solid hsl(var(--destructive) / 0.2);
}
```

---

## 📊 Chart Design Guidelines

### Color Usage in Charts

#### **Single Series Charts**
Use primary blue (#3b82f6) for single data series.

#### **Multi-Series Charts**
Use the financial chart palette for multiple data series:
1. **Primary** (#3b82f6) - Main metric
2. **Success** (#10b981) - Positive values/growth
3. **Warning** (#f59e0b) - Caution/neutral
4. **Info** (#0ea5e9) - Secondary metrics
5. **Purple** (#8b5cf6) - Projections/forecasts

#### **Heat Maps & Distributions**
Use sequential color scales:
- **Cool**: Blues for general data
- **Warm**: Red-orange for risk/volatility
- **Diverging**: Red-white-green for gain/loss

### Chart Typography

```css
/* Chart titles */
.chart-title {
  font-size: 1.125rem;     /* 18px */
  font-weight: 600;
  color: hsl(var(--foreground));
  margin-bottom: 0.5rem;
}

/* Axis labels */
.chart-axis-label {
  font-size: 0.75rem;      /* 12px */
  font-weight: 500;
  color: hsl(var(--muted-foreground));
}

/* Data labels */
.chart-data-label {
  font-size: 0.75rem;      /* 12px */
  font-weight: 600;
  color: hsl(var(--foreground));
}

/* Tooltips */
.chart-tooltip {
  font-size: 0.875rem;     /* 14px */
  background: hsl(var(--background));
  border: 1px solid hsl(var(--border));
  border-radius: 0.5rem;
  padding: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

### Chart Spacing & Layout

```css
/* Chart containers */
.chart-container {
  padding: 1.5rem;
  background: hsl(var(--card));
  border-radius: 0.75rem;
  border: 1px solid hsl(var(--border));
}

/* Chart margins */
.chart-margins {
  margin-top: 1rem;
  margin-right: 2rem;
  margin-bottom: 3rem;
  margin-left: 4rem;
}
```

---

## 🎭 Animation & Motion Design

### Transition Principles

#### **Duration Guidelines**
```css
/* Micro-interactions (hover, focus) */
.transition-fast { transition-duration: 150ms; }

/* UI state changes */
.transition-normal { transition-duration: 200ms; }

/* Layout changes */
.transition-slow { transition-duration: 300ms; }

/* Page transitions */
.transition-slower { transition-duration: 500ms; }
```

#### **Easing Functions**
```css
/* Standard easing */
.ease-out { transition-timing-function: cubic-bezier(0, 0, 0.2, 1); }

/* Bouncy easing for attention */
.ease-bounce { transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55); }

/* Sharp easing for quick actions */
.ease-sharp { transition-timing-function: cubic-bezier(0.4, 0, 0.6, 1); }
```

### Loading Animations

#### **Skeleton Loaders**
```css
.skeleton {
  background: linear-gradient(90deg, 
    hsl(var(--muted)) 25%, 
    hsl(var(--muted) / 0.5) 50%, 
    hsl(var(--muted)) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

#### **Progress Indicators**
```css
.progress-bar {
  height: 4px;
  background: hsl(var(--muted));
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: hsl(var(--primary));
  transition: width 0.3s ease-out;
}
```

### Chart Animations

#### **Data Enter Animations**
```css
/* Line chart draw-in */
@keyframes chart-draw {
  from { 
    stroke-dasharray: 1000;
    stroke-dashoffset: 1000;
  }
  to { 
    stroke-dashoffset: 0;
  }
}

/* Bar chart rise */
@keyframes bar-rise {
  from { 
    transform: scaleY(0);
    transform-origin: bottom;
  }
  to { 
    transform: scaleY(1);
  }
}

/* Pie chart reveal */
@keyframes pie-reveal {
  from { 
    stroke-dasharray: 0 100;
  }
  to { 
    stroke-dasharray: var(--percentage) 100;
  }
}
```

---

## 💡 UX Design Patterns

### Navigation Patterns

#### **Breadcrumb Navigation**
```tsx
<Breadcrumb>
  <BreadcrumbItem>
    <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
  </BreadcrumbItem>
  <BreadcrumbSeparator />
  <BreadcrumbItem>
    <BreadcrumbLink href="/scenarios">Scenarios</BreadcrumbLink>
  </BreadcrumbItem>
  <BreadcrumbSeparator />
  <BreadcrumbItem>
    <BreadcrumbPage>Retirement Plan</BreadcrumbPage>
  </BreadcrumbItem>
</Breadcrumb>
```

#### **Tab Navigation**
```tsx
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="projections">Projections</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">
    {/* Overview content */}
  </TabsContent>
</Tabs>
```

### Progressive Disclosure

#### **Expandable Sections**
```tsx
<Collapsible>
  <CollapsibleTrigger>
    Advanced Options
    <ChevronDown className="collapse-icon" />
  </CollapsibleTrigger>
  <CollapsibleContent>
    {/* Advanced options content */}
  </CollapsibleContent>
</Collapsible>
```

#### **Modal Dialogs**
```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Create Scenario</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Create New Scenario</DialogTitle>
      <DialogDescription>
        Build a comprehensive financial planning scenario
      </DialogDescription>
    </DialogHeader>
    {/* Dialog content */}
    <DialogFooter>
      <Button variant="outline" onClick={onCancel}>Cancel</Button>
      <Button onClick={onCreate}>Create</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Feedback Patterns

#### **Toast Notifications**
```tsx
const { toast } = useToast()

// Success notification
toast({
  title: "Scenario Created",
  description: "Your retirement scenario has been saved successfully.",
  variant: "default"
})

// Error notification
toast({
  title: "Error",
  description: "Failed to save scenario. Please try again.",
  variant: "destructive"
})
```

#### **Inline Validation**
```tsx
<FormField>
  <FormLabel>Annual Salary</FormLabel>
  <FormControl>
    <Input type="number" {...field} />
  </FormControl>
  <FormMessage />
  {field.value && field.value > 0 && (
    <FormHelp className="text-success">
      ✓ Valid salary amount
    </FormHelp>
  )}
</FormField>
```

---

## ♿ Accessibility Guidelines

### WCAG 2.2 AA Compliance

#### **Color Contrast Requirements**
- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text** (18pt+): 3:1 minimum contrast ratio
- **Interactive elements**: 3:1 for focus indicators

#### **Color Contrast Examples**
```css
/* AA compliant text combinations */
.text-primary-on-white { 
  color: #1e40af;        /* 7.15:1 ratio */
  background: #ffffff; 
}

.text-muted-on-light { 
  color: #64748b;        /* 4.51:1 ratio */
  background: #f8fafc; 
}

.text-white-on-primary { 
  color: #ffffff;        /* 8.59:1 ratio */
  background: #1e40af; 
}
```

### Keyboard Navigation

#### **Focus Management**
```css
/* Visible focus indicators */
.focus-visible {
  outline: 2px solid hsl(var(--primary));
  outline-offset: 2px;
  border-radius: 4px;
}

/* Focus within containers */
.focus-within {
  box-shadow: 0 0 0 3px hsl(var(--primary) / 0.1);
}
```

#### **Tab Order**
Logical tab sequence through:
1. Primary navigation
2. Main content actions
3. Form fields (top to bottom, left to right)
4. Secondary actions
5. Footer links

### Screen Reader Support

#### **ARIA Labels**
```tsx
<Button 
  aria-label="Create new financial scenario"
  aria-describedby="create-scenario-help"
>
  <Plus className="h-4 w-4" />
  Create
</Button>
<div id="create-scenario-help" className="sr-only">
  Opens the scenario builder to create a new financial planning scenario
</div>
```

#### **Live Regions**
```tsx
<div 
  role="status" 
  aria-live="polite" 
  aria-atomic="true"
  className="sr-only"
>
  {loadingMessage}
</div>

<div 
  role="alert" 
  aria-live="assertive"
  className="sr-only"
>
  {errorMessage}
</div>
```

### Reduced Motion Support

```css
/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 📱 Responsive Design

### Breakpoint System

```css
/* Mobile first approach */
/* xs: 0px - 479px (default, no media query) */

/* Small devices (phones) */
@media (min-width: 480px) { /* sm */ }

/* Medium devices (tablets) */
@media (min-width: 768px) { /* md */ }

/* Large devices (desktops) */
@media (min-width: 1024px) { /* lg */ }

/* Extra large devices */
@media (min-width: 1280px) { /* xl */ }

/* XXL devices */
@media (min-width: 1536px) { /* 2xl */ }
```

### Container Queries

```css
/* Container-based responsive design */
.chart-container {
  container-type: inline-size;
}

@container (min-width: 300px) {
  .chart-legend {
    display: flex;
    flex-direction: row;
  }
}

@container (min-width: 600px) {
  .chart-controls {
    position: absolute;
    top: 1rem;
    right: 1rem;
  }
}
```

### Responsive Typography

```css
/* Fluid typography */
.text-responsive-xl {
  font-size: clamp(1.5rem, 4vw, 3rem);
  line-height: 1.2;
}

.text-responsive-lg {
  font-size: clamp(1.25rem, 3vw, 2rem);
  line-height: 1.3;
}

.text-responsive-base {
  font-size: clamp(0.875rem, 2vw, 1.125rem);
  line-height: 1.5;
}
```

### Mobile Optimizations

#### **Touch Targets**
```css
/* Minimum 44px touch targets */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem;
}

/* Improved touch spacing */
.touch-list > * + * {
  margin-top: 0.5rem;
}
```

#### **Mobile Navigation**
```tsx
<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline" size="icon" className="md:hidden">
      <Menu className="h-4 w-4" />
      <span className="sr-only">Toggle menu</span>
    </Button>
  </SheetTrigger>
  <SheetContent side="left">
    <nav className="flex flex-col space-y-4">
      {/* Mobile navigation items */}
    </nav>
  </SheetContent>
</Sheet>
```

---

## 🎯 Performance Guidelines

### Critical Rendering Path

#### **Above-the-fold CSS**
```css
/* Critical styles inlined in <head> */
.hero-section {
  display: flex;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-skeleton {
  background: #f0f0f0;
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}
```

#### **Font Loading Strategy**
```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>

<!-- Display swap for better perceived performance -->
<style>
  @font-face {
    font-family: 'Inter';
    src: url('/fonts/inter-var.woff2') format('woff2');
    font-display: swap;
    font-weight: 100 900;
  }
</style>
```

### Image Optimization

```tsx
import Image from 'next/image'

<Image
  src="/chart-preview.png"
  alt="Financial projection chart preview"
  width={800}
  height={600}
  priority={isAboveFold}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

### Bundle Optimization

```tsx
// Code splitting for heavy components
const MonteCarloVisualization = dynamic(
  () => import('../components/MonteCarloVisualization'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false
  }
)

// Tree shaking for icon libraries
import { DollarSign, TrendingUp } from 'lucide-react'
```

---

## 🎨 Theme Implementation

### CSS Custom Properties

```css
:root {
  /* Color system */
  --primary: 221 83% 53%;
  --primary-foreground: 210 40% 98%;
  
  /* Border radius */
  --radius: 0.5rem;
  
  /* Font families */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Animation durations */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### Theme Provider

```tsx
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
    >
      {children}
    </ThemeProvider>
  )
}
```

### Theme Toggle Component

```tsx
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

---

## 📏 Component Specifications

### Spacing Guidelines

#### **Component Internal Spacing**
```css
/* Card padding */
.card-padding-sm { padding: 1rem; }        /* 16px */
.card-padding-md { padding: 1.5rem; }      /* 24px */
.card-padding-lg { padding: 2rem; }        /* 32px */

/* Button padding */
.btn-padding-sm { padding: 0.5rem 0.75rem; }    /* 8px 12px */
.btn-padding-md { padding: 0.75rem 1rem; }      /* 12px 16px */
.btn-padding-lg { padding: 1rem 2rem; }         /* 16px 32px */

/* Input padding */
.input-padding { padding: 0.75rem 1rem; }       /* 12px 16px */
```

#### **Component External Spacing**
```css
/* Stack spacing (vertical) */
.stack-xs > * + * { margin-top: 0.5rem; }    /* 8px */
.stack-sm > * + * { margin-top: 1rem; }      /* 16px */
.stack-md > * + * { margin-top: 1.5rem; }    /* 24px */
.stack-lg > * + * { margin-top: 2rem; }      /* 32px */

/* Cluster spacing (horizontal) */
.cluster-xs { gap: 0.5rem; }                 /* 8px */
.cluster-sm { gap: 1rem; }                   /* 16px */
.cluster-md { gap: 1.5rem; }                 /* 24px */
.cluster-lg { gap: 2rem; }                   /* 32px */
```

### Component States

#### **Interactive States**
```css
/* Default → Hover → Active → Disabled */

.component-default {
  opacity: 1;
  transform: translateY(0);
  transition: all var(--duration-normal) ease-out;
}

.component-hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.component-active {
  opacity: 0.95;
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.component-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

#### **Loading States**
```css
.component-loading {
  position: relative;
  pointer-events: none;
}

.component-loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## 🧪 Quality Assurance

### Visual Regression Testing

```typescript
// Example Playwright visual test
import { test, expect } from '@playwright/test'

test('dashboard visual regression', async ({ page }) => {
  await page.goto('/dashboard')
  await page.waitForSelector('[data-testid="dashboard-loaded"]')
  
  // Take screenshot for visual comparison
  await expect(page).toHaveScreenshot('dashboard.png', {
    fullPage: true,
    threshold: 0.3
  })
})
```

### Accessibility Testing

```typescript
// Example accessibility test with axe-core
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('scenario builder accessibility', async ({ page }) => {
  await page.goto('/scenarios/new')
  
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze()
  
  expect(accessibilityScanResults.violations).toEqual([])
})
```

### Performance Testing

```typescript
// Example Lighthouse CI configuration
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/', 'http://localhost:3000/dashboard'],
      startServerCommand: 'npm run start',
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
      },
    },
  },
}
```

---

## 📖 Documentation Standards

### Component Documentation

```tsx
/**
 * MetricCard - Displays a financial metric with trend indicator
 * 
 * @param title - The metric title (e.g., "Net Worth")
 * @param value - The formatted value (e.g., "$285,000")
 * @param change - The percentage change (-1.0 to 1.0)
 * @param changeLabel - Context for the change (e.g., "from last month")
 * @param trend - Visual trend indicator ("up" | "down" | "neutral")
 * @param icon - Icon component to display
 * @param className - Additional CSS classes
 * 
 * @example
 * <MetricCard
 *   title="Net Worth"
 *   value="$285,000"
 *   change={0.085}
 *   changeLabel="from last month"
 *   trend="up"
 *   icon={<DollarSign />}
 * />
 */
export interface MetricCardProps {
  title: string
  value: string
  change: number
  changeLabel: string
  trend: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
  className?: string
}
```

### Style Guide Updates

This design system is a living document that should be updated as the application evolves. When making changes:

1. **Document rationale** for design decisions
2. **Update examples** to reflect current implementation
3. **Test across themes** (light/dark mode)
4. **Verify accessibility** compliance
5. **Update component library** documentation

---

## 🎯 Summary

This design system establishes a comprehensive foundation for building a cutting-edge financial planning application that meets 2025+ standards for:

- **Visual Appeal**: Modern, clean aesthetic with sophisticated color usage
- **User Experience**: Intuitive navigation and progressive disclosure
- **Accessibility**: WCAG 2.2 AA compliance with comprehensive support
- **Performance**: Optimized components and efficient rendering
- **Maintainability**: Consistent patterns and reusable components
- **Scalability**: Flexible system that grows with application needs

By following these guidelines, the application will provide a premium user experience that rivals the best financial planning tools in the industry while maintaining technical excellence and accessibility standards.

---

*Last updated: January 2025*
*Version: 2.0.0*