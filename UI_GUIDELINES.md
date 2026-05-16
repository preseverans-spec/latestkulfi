# New Indian Kulfi UI/UX Component Library

This document outlines the standard UI/UX design system implemented across the New Indian Kulfi platform. Adhering to these guidelines ensures a consistent, high-fidelity, and production-ready SaaS aesthetic across all modules.

## Core Principles
1. **Typography**: The primary font family is **Inter**. Weights are carefully used: `font-bold` for headings and emphasis, `font-semibold` for secondary elements, and normal weight for data.
2. **Colors**: The design relies on a strict set of variables defined in `base.html`:
   - Primary: `#FF6B35` (Professional Orange)
   - Secondary: `#2E2E2E` (Slate Dark)
   - Text Main: `var(--text-main)` (`#1F2937`)
   - Text Sub: `var(--text-sub)` (`#6B7280`)
3. **Layout**: Uses a sidebar-wrapper structure. Content is constrained to `max-width: 1400px` within `.main-content`.

## Common Components

### 1. The Standard Card
All major content blocks (forms, tables, telemetry) should be wrapped in the standard card.

```html
<div class="card border-0 shadow-sm mb-5">
    <!-- Optional Header -->
    <div class="p-4 border-bottom bg-white d-flex justify-content-between align-items-center">
        <h3 class="text-xs font-bold text-uppercase text-sub mb-0">Card Title</h3>
    </div>
    
    <!-- Body -->
    <div class="card-body p-4">
        Content goes here
    </div>
</div>
```

### 2. Telemetry Matrix (Metrics Dashboard)
Use this pattern for displaying key performance indicators (KPIs) at the top of reporting pages.

```html
<div class="row g-4 mb-5">
    <div class="col-md-3">
        <!-- Colored Border Indicator -->
        <div class="card h-100" style="border-left: 4px solid var(--primary);">
            <div class="text-xs font-semibold text-sub text-uppercase mb-2">Metric Title</div>
            <div class="text-xl font-semibold text-primary">₹Value</div>
            <div class="text-xs text-sub mt-1">Short description</div>
        </div>
    </div>
    <!-- Alternative: Colored Background Box (Inside a card or directly) -->
    <div class="col-md-3">
        <div class="p-3 bg-success bg-opacity-10 rounded-4 border border-success border-opacity-10">
            <div class="text-xs text-success fw-bold text-uppercase mb-1">Metric Title</div>
            <div class="text-lg font-bold text-success">Value</div>
        </div>
    </div>
</div>
```

### 3. Data Tables
Tables should be clean, borderless internally except for rows, and utilize a specific header style.

```html
<div class="card p-0 overflow-hidden border-0 shadow-sm">
    <div class="table-responsive">
        <table class="table mb-0 align-middle">
            <thead class="bg-light">
                <tr>
                    <th class="px-4">Primary Column</th>
                    <th class="text-center">Center Column</th>
                    <th class="text-end px-4">Right Column</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="px-4">
                        <div class="font-bold text-main">Main Text</div>
                        <div class="text-xs text-sub">Subtext</div>
                    </td>
                    <td class="text-center">
                        <span class="badge bg-light text-sub border fw-bold">Status</span>
                    </td>
                    <td class="text-end px-4 font-bold text-main">₹Value</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

### 4. Form Inputs
Inputs use a consistent, clean style without harsh borders. Avoid default browser outlines.

```html
<label class="form-label text-xs font-bold text-uppercase opacity-75">Input Label</label>
<div class="input-group shadow-sm rounded-3 overflow-hidden">
    <!-- Optional Icon -->
    <span class="input-group-text bg-white border-end-0"><i class="fas fa-icon text-primary"></i></span>
    <input type="text" class="form-control border-0 bg-light px-3 py-2">
</div>
<div class="text-xs text-sub mt-2">Helper text...</div>
```

### 5. Buttons
Buttons follow a strict hierarchy and should include icons where applicable.

```html
<!-- Primary Action -->
<button class="btn btn-primary font-bold shadow-sm">
    <i class="fas fa-check me-2"></i> PRIMARY ACTION
</button>

<!-- Secondary / Cancel -->
<button class="btn btn-secondary">
    <i class="fas fa-times me-2"></i> SECONDARY
</button>

<!-- Small Action Icons in Tables -->
<button class="btn btn-sm btn-outline-primary shadow-sm" title="Action">
    <i class="fas fa-edit"></i>
</button>
```

### 6. Badges and Status Pills
Use badges to represent states, types, or compact numeric data.

```html
<!-- Subtle text badge -->
<span class="badge bg-light text-sub border fw-bold px-3">LABEL</span>

<!-- Success state -->
<span class="badge bg-success bg-opacity-10 text-success border-0 px-3 py-2 font-bold">SUCCESS</span>

<!-- Warning / Highlight state -->
<span class="badge bg-warning bg-opacity-10 text-warning border-0 px-3 py-2 font-bold">WARNING</span>
```

### 7. Filter Bars
Use filter bars at the top of list views to group search and date controls.

```html
<div class="card mb-5">
    <div class="p-4 bg-light bg-opacity-50">
        <form class="row g-3 align-items-end">
            <div class="col-md-5">
                <label class="text-xs font-bold text-sub text-uppercase mb-2 d-block">Search</label>
                <!-- Form Inputs... -->
            </div>
            <div class="col-md-3 d-flex gap-2">
                <button type="submit" class="btn btn-primary flex-grow-1">Filter</button>
                <a href="#" class="btn btn-secondary"><i class="fas fa-rotate-left"></i></a>
            </div>
        </form>
    </div>
</div>
```

## Best Practices
- **Never use raw text**: Always wrap text in a tag with either `text-main` or `text-sub` class.
- **Spacing**: Use Bootstrap 5 spacing utilities (e.g., `mb-4`, `p-4`, `g-4`) to maintain consistent whitespace. Default padding inside cards should be `p-4`.
- **Icons**: FontAwesome icons are standard. Ensure consistent sizing (`fa-lg`, `fa-sm`) relative to the text they accompany.
- **Responsive**: Always test complex rows and tables on smaller viewports. Use `.table-responsive` generously.
