-- Create opportunity tabs tables
CREATE TABLE IF NOT EXISTS opportunity_stakeholders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES opportunities(id),
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    contact_number VARCHAR(50),
    influence_level VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opportunity_drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES opportunities(id),
    category VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opportunity_competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES opportunities(id),
    name VARCHAR(255) NOT NULL,
    strength VARCHAR(100),
    weakness VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opportunity_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES opportunities(id),
    strategy_type VARCHAR(100) NOT NULL,
    description TEXT,
    priority VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_opportunity_stakeholders_opportunity_id ON opportunity_stakeholders(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_drivers_opportunity_id ON opportunity_drivers(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_competitors_opportunity_id ON opportunity_competitors(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_strategies_opportunity_id ON opportunity_strategies(opportunity_id);