-- Create staff planning tables for multi-tenant workforce management

-- Main staff plans table
CREATE TABLE IF NOT EXISTS staff_plans (
    id SERIAL PRIMARY KEY,
    
    -- Project Details
    project_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    project_start_date DATE NOT NULL,
    
    -- Financial Parameters
    duration_months INTEGER DEFAULT 12,
    overhead_rate FLOAT DEFAULT 25.0,
    profit_margin FLOAT DEFAULT 15.0,
    annual_escalation_rate FLOAT DEFAULT 3.0,
    
    -- Cost Summary
    total_labor_cost FLOAT DEFAULT 0.0,
    total_overhead FLOAT DEFAULT 0.0,
    total_cost FLOAT DEFAULT 0.0,
    total_profit FLOAT DEFAULT 0.0,
    total_price FLOAT DEFAULT 0.0,
    
    -- Multi-year breakdown
    yearly_breakdown JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    
    -- Multi-tenancy
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Audit
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff allocations table
CREATE TABLE IF NOT EXISTS staff_allocations (
    id SERIAL PRIMARY KEY,
    
    -- Plan reference
    staff_plan_id INTEGER NOT NULL REFERENCES staff_plans(id) ON DELETE CASCADE,
    
    -- Resource/Employee details
    resource_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    resource_name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    level VARCHAR(50),
    
    -- Allocation details
    start_month INTEGER DEFAULT 1,
    end_month INTEGER DEFAULT 12,
    hours_per_week FLOAT DEFAULT 40.0,
    allocation_percentage FLOAT DEFAULT 100.0,
    
    -- Cost details
    hourly_rate FLOAT NOT NULL,
    monthly_cost FLOAT DEFAULT 0.0,
    total_cost FLOAT DEFAULT 0.0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'planned',
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resource utilization tracking
CREATE TABLE IF NOT EXISTS resource_utilization (
    id SERIAL PRIMARY KEY,
    resource_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Utilization metrics
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    total_allocated_hours FLOAT DEFAULT 0.0,
    utilization_percentage FLOAT DEFAULT 0.0,
    
    -- Status indicators
    is_overallocated BOOLEAN DEFAULT FALSE,
    is_underutilized BOOLEAN DEFAULT FALSE,
    
    -- Audit
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(resource_id, month, year)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_staff_plans_org_id ON staff_plans(org_id);
CREATE INDEX IF NOT EXISTS idx_staff_plans_status ON staff_plans(status);
CREATE INDEX IF NOT EXISTS idx_staff_plans_project_id ON staff_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_staff_allocations_plan_id ON staff_allocations(staff_plan_id);
CREATE INDEX IF NOT EXISTS idx_staff_allocations_resource_id ON staff_allocations(resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_utilization_resource_id ON resource_utilization(resource_id);

SELECT 'Staff planning tables created successfully' as status;

