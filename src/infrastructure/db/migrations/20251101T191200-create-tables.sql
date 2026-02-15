-- Enable extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================
-- SELLERS
-- ==============================
CREATE TABLE sellers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    details JSONB NOT NULL, -- {name, mobile_phone, telegram_handle, chat_id, email}
    payment JSONB DEFAULT '{}'::jsonb, -- {status, plan, last_paid_at, expires_at, payment_method}
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- GENERIC LISTINGS
-- (Base table for all listing types)
-- ==============================
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES sellers(id) ON DELETE CASCADE ON UPDATE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'car', 'real_estate', 'other'
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- CAR LISTINGS
-- ==============================
CREATE TABLE car_listings (
    listing_id UUID PRIMARY KEY REFERENCES listings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INT,
    price NUMERIC,
    location TEXT,
    mileage INT,
    color TEXT,
    transmission TEXT,
    fuel_type TEXT,
    drivetrain TEXT,
    photos JSONB DEFAULT '[]'::jsonb,
    link TEXT,
    description TEXT
);

-- ==============================
-- REAL ESTATE LISTINGS
-- ==============================
CREATE TABLE real_estate_listings (
    listing_id UUID PRIMARY KEY REFERENCES listings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    address TEXT NOT NULL,
    area NUMERIC,
    rooms INT,
    price NUMERIC,
    location TEXT,
    photos JSONB DEFAULT '[]'::jsonb,
    link TEXT,
    description TEXT
);

-- ==============================
-- BUYERS
-- ==============================
CREATE TABLE buyers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    details JSONB NOT NULL, -- {name, mobile_phone, telegram_handle, chat_id, email}
    payment JSONB DEFAULT '{}'::jsonb, -- {status, plan, last_paid_at, expires_at, payment_method}
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- BUYER REQUESTS
-- ==============================
CREATE TABLE buyer_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE ON UPDATE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'car', 'real_estate', etc.
    details JSONB NOT NULL, -- type-specific search filters
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'matched', 'fulfilled', 'cancelled'
    matched_listing_id UUID REFERENCES listings(id) ON DELETE SET NULL ON UPDATE CASCADE,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- INDEXES
-- ==============================

-- Sellers
CREATE INDEX idx_sellers_id ON sellers(id); 
CREATE INDEX idx_sellers_name ON sellers ((details->>'name'));
CREATE INDEX idx_sellers_telegram_handle ON sellers ((details->>'telegram_handle'));
CREATE INDEX idx_sellers_chat_id ON sellers ((details->>'chat_id'));

-- Listings
CREATE INDEX idx_listings_id ON listings(id);
CREATE INDEX idx_listings_type ON listings(type);
CREATE INDEX idx_listings_seller_id ON listings(seller_id);
ALTER TABLE listings ADD CONSTRAINT listings_type_check CHECK (type IN ('car', 'real_estate'));

-- Cars
CREATE INDEX idx_car_listings_make_model ON car_listings(make, model);
CREATE INDEX idx_car_listings_price ON car_listings(price);

-- Real Estate
CREATE INDEX idx_real_estate_listings_address ON real_estate_listings(address);
CREATE INDEX idx_real_estate_listings_price ON real_estate_listings(price);

-- Buyers
CREATE INDEX idx_buyers_name ON buyers ((details->>'name'));
CREATE INDEX idx_buyers_chat_id ON buyers ((details->>'chat_id'));

-- Buyer Requests
CREATE INDEX idx_buyer_requests_buyer_id ON buyer_requests(buyer_id);
CREATE INDEX idx_buyer_requests_status ON buyer_requests(status);
CREATE INDEX idx_buyer_requests_type ON buyer_requests(type);
CREATE INDEX idx_buyer_requests_details_gin ON buyer_requests USING GIN (details);
CREATE INDEX idx_buyer_requests_matched_listing_id ON buyer_requests(matched_listing_id);
ALTER TABLE buyer_requests ADD CONSTRAINT buyer_requests_type_check CHECK (type IN ('car', 'real_estate'));
ALTER TABLE buyer_requests
ADD CONSTRAINT buyer_requests_status_check CHECK (status IN ('pending', 'matched', 'fulfilled', 'cancelled'));