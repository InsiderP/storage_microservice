-- Create metadata table
CREATE TABLE IF NOT EXISTS metadata (
    device_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    last_maintenance TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on device_id
CREATE INDEX IF NOT EXISTS idx_metadata_device_id ON metadata(device_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_metadata_updated_at
    BEFORE UPDATE ON metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 