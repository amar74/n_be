-- Create vendors table for Super Admin vendor management
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_name VARCHAR(255) NOT NULL,
    organisation VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    email VARCHAR(255) NOT NULL UNIQUE,
    contact_number VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_vendors_email ON vendors(email);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(status);

SELECT 'Vendors table created successfully!' as message;
