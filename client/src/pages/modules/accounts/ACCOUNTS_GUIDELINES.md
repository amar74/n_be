# Accounts Module Guidelines

## Overview
This document serves as the single source of truth for the Accounts module structure, design decisions, and component usage to prevent hallucinations and redundancy.

## Structure Decisions

### Folder Structure
Following the CreateOrganizationPage pattern:
```
/client/src/pages/modules/accounts/
├── AccountsPage.tsx                    # Main page component
├── AccountsPage.types.ts               # TypeScript interfaces
├── AccountsPage.constants.ts           # Constants and static data
├── useAccountsPage.ts                  # Main hook with business logic
├── ACCOUNTS_GUIDELINES.md              # This documentation
├── index.ts                           # Exports
└── components/
    ├── AccountsHeader/                # Breadcrumbs + title + CTAs
    ├── AccountsStats/                 # Info cards section
    ├── AccountsList/                  # Accounts grid/list
    ├── AccountCard/                   # Individual account card
    └── CreateAccountModal/            # Create account form modal (TODO)
```

## Figma Design References

### Layout Structure
- **Background**: `#f5f3f2` (matches HomePage)
- **Content positioning**: Accounts content renders inside HomePage's Outlet
- **Sidebar**: 260px width, handled by HomePage layout
- **Main content**: No left margin needed (HomePage handles sidebar spacing)

### Header Section
- **Breadcrumbs**: "Dashboard > Accounts" with chevron separator
- **Title**: "My Accounts" in orange `#ed8a09`, 40px font-semibold
- **Subtitle**: "Manage client accounts and relationship data" in gray `#a7a7a7`
- **CTAs**: 4 buttons on right - All Accounts, Actions, Client Survey, Create Account

### Stats Cards
- **Layout**: 5 cards in horizontal row, 301px width each, 97px height
- **Background**: `bg-neutral-50` with `border-[#6c6c6c]`
- **Icons**: Gray circles `bg-[#f3f3f3]`, 56px size
- **Cards**: Total Accounts, AI Health Score, High Risk, Growing, Total Value

### Account Cards
- **Layout**: 3-column grid, 527px width each
- **Background**: White cards with `rounded-[28px]`
- **Risk indicators**: Colored badges and bottom borders
- **Colors**: Green (#5f936f), Orange (#cd812a), Red (#ff7b7b)

## CTA/Button Variants

### Primary Buttons (shadcn/ui)
1. **Create Account Button**
   - Style: `bg-[#0f0901]` black filled
   - Size: `h-[46px] w-[175px]`
   - Shape: `rounded-[100px]`
   - Text: White, 14px font-medium

2. **Client Survey Button**
   - Style: `border border-black` outline
   - Size: `h-[46px] w-[175px]`
   - Shape: `rounded-[100px]`
   - Text: Black, 14px font-medium

### Dropdown Buttons
1. **All Accounts Dropdown**
   - Style: `bg-white border-[#525151]`
   - Size: `h-[46px] w-[205px]`
   - Shape: `rounded-[24px]`

2. **Actions Dropdown**
   - Style: `bg-white border-[#525151]`
   - Size: `h-[46px] w-[161px]`
   - Shape: `rounded-[24px]`

## Color Scheme
- **Primary Orange**: `#ed8a09`
- **Button Black**: `#0f0901`
- **Background**: `#f5f3f2`
- **Card Background**: `bg-neutral-50`
- **Border Gray**: `#6c6c6c`
- **Text Gray**: `#a7a7a7`
- **Risk Colors**:
  - Low: `#5f936f` (green)
  - Medium: `#cd812a` (orange)
  - High: `#ff7b7b` (red)

## Component Usage Rules

### AccountsHeader
- Handles breadcrumbs, title, and all CTA buttons
- Props: `onCreateAccount`, `onExport`
- No inline button definitions - uses shadcn/ui Button component

### AccountsStats
- Displays 5 stat cards in horizontal layout
- Props: `stats` (AccountStatsData), `onStatClick`
- Cards are clickable for filtering functionality

### AccountsList
- Renders up to 3 AccountCard components in a row
- Props: `accounts`, `isLoading`, `onAccountClick`
- Handles loading and empty states

### AccountCard
- Individual account display with risk-based styling
- Props: `account` (AccountData), `onClick`
- Risk level determines badge colors and bottom border

## Data Flow

### useAccountsPage Hook
- Main business logic and state management
- Integrates with existing `useAccounts` hook
- Handles filtering, search, and navigation
- Returns data and action handlers for components

### State Management
- Local state for UI interactions (filters, modals)
- API integration through existing hooks
- Mock data for development/testing

## Integration Points

### Routing
- Route: `/module/accounts` (existing)
- Parent: HomePage with sidebar layout
- Navigation: Uses React Router's `useNavigate`

### API Integration
- Uses existing `useAccounts` hook
- Fallback to mock data during development
- Compatible with current API structure

## TODO Items
1. Implement CreateAccountModal component
2. Add search/filter functionality to header
3. Integrate with real API data
4. Add loading states and error handling
5. Implement account detail navigation
6. Add export functionality

## Data Management

### Mock Data
- **Location**: `AccountsPage.constants.ts` - following established patterns
- **Purpose**: Development and testing  
- **Structure**: Typed array of `AccountData` objects with varied risk levels and client types
- **Pattern**: Imported into hook, properly typed to avoid TypeScript inference issues
- **Future**: Replace with real API integration via `useAccounts` hook

### Pattern Adherence
- **Constants**: All static data moved to `.constants.ts` file
- **Types**: Proper TypeScript typing to prevent inference issues
- **Import Structure**: Clean imports following CreateOrganizationPage pattern
- **Data Variety**: Mock data includes different tiers (Tire 1/2/3) and risk levels

## Development Notes
- Follow existing codebase patterns
- Use shadcn/ui components consistently
- Maintain TypeScript strict typing
- Keep components modular and reusable
- Test with both mock and real data
