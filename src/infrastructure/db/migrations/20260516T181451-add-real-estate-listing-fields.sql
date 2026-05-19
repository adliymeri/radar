-- Migration: Add new fields and rename location to district in real_estate_listings
-- Date: 2026-05-16

-- Rename location to district
ALTER TABLE real_estate_listings RENAME COLUMN location TO district;

-- Add new columns
ALTER TABLE real_estate_listings
    ADD COLUMN property_type VARCHAR(50) NOT NULL DEFAULT '',
    ADD COLUMN listing_type VARCHAR(50) NOT NULL DEFAULT '',
    ADD COLUMN city VARCHAR(100) NOT NULL DEFAULT '',
    ADD COLUMN condition VARCHAR(50),
    ADD COLUMN bedrooms INT,
    ADD COLUMN bathrooms INT,
    ADD COLUMN floor INT,
    ADD COLUMN parking BOOLEAN,
    ADD COLUMN elevator BOOLEAN,
    ADD COLUMN furnished BOOLEAN,
    ADD COLUMN balcony BOOLEAN;

-- Add constraints for enum values
ALTER TABLE real_estate_listings
    ADD CONSTRAINT real_estate_property_type_check
    CHECK (property_type IN ('Apartment', 'House', 'Villa', 'Land', 'Commercial', 'Studio'));

ALTER TABLE real_estate_listings
    ADD CONSTRAINT real_estate_listing_type_check
    CHECK (listing_type IN ('Sale', 'Rent'));

ALTER TABLE real_estate_listings
    ADD CONSTRAINT real_estate_condition_check
    CHECK (condition IN ('New Construction', 'Old Construction'));

-- Add indexes
CREATE INDEX idx_real_estate_property_type ON real_estate_listings(property_type);
CREATE INDEX idx_real_estate_listing_type ON real_estate_listings(listing_type);
CREATE INDEX idx_real_estate_city ON real_estate_listings(city);

-- Replace old location index with district index
DROP INDEX IF EXISTS idx_real_estate_listings_address;
CREATE INDEX idx_real_estate_district ON real_estate_listings(district);

-- Track migration
INSERT INTO migrations (filename) VALUES ('20260516T181451-add-real-estate-listing-fields.sql');