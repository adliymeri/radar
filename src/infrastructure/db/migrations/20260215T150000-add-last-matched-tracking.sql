ALTER TABLE listings ADD COLUMN last_matched_at TIMESTAMPTZ;

-- Index for efficient incremental queries
CREATE INDEX idx_listings_created_at ON listings(created_at);
CREATE INDEX idx_listings_updated_at ON listings(updated_at);
CREATE INDEX idx_listings_last_matched_at ON listings(last_matched_at);

-- Add location index to car_listings
CREATE INDEX idx_car_listings_location ON car_listings(location);

-- Add composite indexes for common filters
CREATE INDEX idx_car_listings_year_price ON car_listings(year, price);
CREATE INDEX idx_car_listings_mileage ON car_listings(mileage);

INSERT INTO migrations (filename) VALUES ('20260215T150000-add-last-matched-tracking.sql');