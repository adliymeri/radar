ALTER TABLE car_listings DROP COLUMN color;
ALTER TABLE car_listings ADD COLUMN color JSONB DEFAULT '[]'::jsonb;

CREATE INDEX idx_car_listings_color ON car_listings USING GIN (color);

INSERT INTO migrations (filename) VALUES ('20260215T000001-alter-car-listings-color.sql');