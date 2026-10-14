- =====================================================
-- TRAVEL BOOKING & TRIP MANAGEMENT SYSTEM
-- =====================================================

DROP DATABASE IF EXISTS travel_booking;
CREATE DATABASE travel_booking;
USE travel_booking;

-- 1. CUSTOMERS
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. DESTINATIONS
CREATE TABLE destinations (
    destination_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    UNIQUE KEY uq_destination (destination_name, country)
);

-- 3. TOUR PACKAGES
CREATE TABLE tour_packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT NOT NULL,
    package_name VARCHAR(150) NOT NULL,
    description TEXT,
    duration_days INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id)
        ON DELETE CASCADE
);

-- 4. HOTELS
CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT NOT NULL,
    hotel_name VARCHAR(150) NOT NULL,
    address TEXT,
    rating DECIMAL(2,1),
    price_per_night DECIMAL(10,2),
    image_url VARCHAR(500),
    FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id)
        ON DELETE CASCADE,
    UNIQUE KEY uq_hotel (destination_id, hotel_name)
);

-- 5. TRANSPORT
CREATE TABLE transport (
    transport_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT,
    transport_type VARCHAR(50) NOT NULL,
    provider_name VARCHAR(100),
    source_location VARCHAR(100),
    destination_location VARCHAR(100),
    departure_time DATETIME,
    arrival_time DATETIME,
    duration_minutes INT,
    price DECIMAL(10,2),
    available_seats INT,
    FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id)
        ON DELETE SET NULL
);

-- 6. BOOKINGS
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    package_id INT,
    hotel_id INT,
    transport_id INT,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    travel_date DATE NOT NULL,
    number_of_people INT NOT NULL DEFAULT 1,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    booking_status ENUM(
        'Pending',
        'Confirmed',
        'Cancelled',
        'Completed'
    ) DEFAULT 'Pending',
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (package_id)
        REFERENCES tour_packages(package_id)
        ON DELETE SET NULL,
    FOREIGN KEY (hotel_id)
        REFERENCES hotels(hotel_id)
        ON DELETE SET NULL,
    FOREIGN KEY (transport_id)
        REFERENCES transport(transport_id)
        ON DELETE SET NULL
);

-- 7. ITINERARY
CREATE TABLE itinerary (
    itinerary_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    day_number INT NOT NULL,
    activity_date DATE,
    activity_title VARCHAR(150),
    activity_description TEXT,
    location VARCHAR(150),
    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
        ON DELETE CASCADE
);

-- 8. PAYMENTS
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_method ENUM(
        'UPI',
        'Card',
        'Net Banking',
        'Cash'
    ),
    transaction_id VARCHAR(100) UNIQUE,
    amount DECIMAL(12,2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM(
        'Pending',
        'Success',
        'Failed',
        'Refunded'
    ) DEFAULT 'Pending',
    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
        ON DELETE CASCADE
);

-- 9. CANCELLATIONS
CREATE TABLE cancellations (
    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    cancellation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    refund_amount DECIMAL(12,2),
    cancellation_status ENUM(
        'Requested',
        'Processed',
        'Rejected'
    ) DEFAULT 'Requested',
    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
        ON DELETE CASCADE
);

-- 10. REVIEWS
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    destination_id INT,
    hotel_id INT,
    package_id INT,
    rating INT,
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id)
        ON DELETE SET NULL,
    FOREIGN KEY (hotel_id)
        REFERENCES hotels(hotel_id)
        ON DELETE SET NULL,
    FOREIGN KEY (package_id)
        REFERENCES tour_packages(package_id)
        ON DELETE SET NULL
);

-- 11. TRIP HISTORY
CREATE TABLE trip_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    booking_id INT NOT NULL,
    destination_id INT,
    trip_start_date DATE,
    trip_end_date DATE,
    trip_status VARCHAR(50),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id),
    FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id)
        ON DELETE SET NULL,
    UNIQUE KEY uq_history_booking (booking_id)
);

-- =====================================================
-- SEED DATA
-- =====================================================

INSERT INTO customers
(full_name, email, phone, address, password)
VALUES
('Karthik', 'karthik@gmail.com', '9000000001', 'Shadnagar', 'DemoPass1!'),
('Shivaprasad', 'shiva@gmail.com', '9000000002', 'Hyderabad', 'DemoPass2!'),
('Benarji', 'benarji@gmail.com', '9000000003', 'Warangal', 'DemoPass3!'),
('Ganesh', 'ganesh@gmail.com', '9000000004', 'Karimnagar', 'DemoPass4!'),
('Ravi', 'ravi@gmail.com', '9000000005', 'Khammam', 'DemoPass5!'),
('Suresh', 'suresh@gmail.com', '9000000006', 'Nalgonda', 'DemoPass6!');

INSERT INTO destinations
(destination_name, country, description, image_url, latitude, longitude)
VALUES
('Goa', 'India', 'Beach capital',
 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2', 15.4909, 73.8278),
('Manali', 'India', 'Snow hills',
 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23', 32.2432, 77.1892),
('Dubai', 'UAE', 'Luxury city',
 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c', 25.2048, 55.2708),
('Kerala', 'India', 'Backwaters',
 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944', 9.9312, 76.2673),
('Bali', 'Indonesia', 'Island paradise',
 'https://images.unsplash.com/photo-1537996194471-e657df975ab4', -8.3405, 115.0920),
('Paris', 'France', 'Eiffel Tower city',
 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34', 48.8566, 2.3522);

INSERT INTO tour_packages
(destination_id, package_name, description, duration_days, price, image_url)
VALUES
(1, 'Goa Beach 3 Days', 'Beach fun', 3, 15000,
 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2'),
(2, 'Manali Snow 5 Days', 'Snow adventure', 5, 25000,
 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23'),
(3, 'Dubai Luxury 4 Days', 'Dubai tour', 4, 50000,
 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c'),
(4, 'Kerala Nature 4 Days', 'Nature tour', 4, 20000,
 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944'),
(5, 'Bali Island 6 Days', 'Island tour', 6, 40000,
 'https://images.unsplash.com/photo-1537996194471-e657df975ab4'),
(6, 'Paris Romantic 7 Days', 'Paris tour', 7, 70000,
 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34');

INSERT INTO hotels
(destination_id, hotel_name, address, rating, price_per_night, image_url)
VALUES
(1, 'Goa Beach Resort', 'Calangute Goa', 4.5, 3000,
 'https://images.unsplash.com/photo-1566073771259-6a8506099945'),
(2, 'Manali Hill View', 'Mall Road Manali', 4.2, 2500,
 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb'),
(3, 'Dubai Grand Hotel', 'Downtown Dubai', 4.8, 8000,
 'https://images.unsplash.com/photo-1564501049412-61c2a3083791'),
(4, 'Kerala Backwater Resort', 'Alleppey', 4.3, 3500,
 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7'),
(5, 'Bali Beach Villa', 'Kuta Bali', 4.6, 6000,
 'https://images.unsplash.com/photo-1582610116397-edb318620f90'),
(6, 'Paris Eiffel Hotel', 'Paris Center', 4.9, 10000,
 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85');

INSERT INTO transport
(destination_id, transport_type, provider_name, source_location,
 destination_location, departure_time, arrival_time,
 duration_minutes, price, available_seats)
VALUES
(1, 'Flight', 'IndiGo', 'Hyderabad', 'Goa',
 '2026-10-20 06:00:00', '2026-10-20 08:00:00', 120, 4500, 100),
(2, 'Bus', 'RedBus', 'Delhi', 'Manali',
 '2026-11-15 08:00:00', '2026-11-15 18:00:00', 600, 1500, 40),
(3, 'Flight', 'Emirates', 'Hyderabad', 'Dubai',
 '2026-12-05 10:00:00', '2026-12-05 13:30:00', 210, 15000, 150),
(4, 'Train', 'IRCTC', 'Hyderabad', 'Kerala',
 '2026-10-30 07:30:00', '2026-10-31 09:00:00', 1530, 2000, 200),
(5, 'Flight', 'AirAsia', 'Hyderabad', 'Bali',
 '2026-11-25 09:00:00', '2026-11-25 17:00:00', 480, 18000, 120),
(6, 'Flight', 'Air France', 'Delhi', 'Paris',
 '2026-12-20 11:00:00', '2026-12-20 18:30:00', 450, 45000, 180);

-- Six sample bookings, consistent with the displayed seed prices
INSERT INTO bookings
(customer_id, package_id, hotel_id, transport_id,
 travel_date, number_of_people, total_amount, booking_status)
VALUES
(1, 1, 1, 1, '2026-10-20', 2, 48000, 'Confirmed'),
(2, 2, 2, 2, '2026-11-15', 3, 93000, 'Confirmed'),
(3, 3, 3, 3, '2026-12-05', 2, 112000, 'Pending'),
(4, 4, 4, 4, '2026-10-30', 4, 110000, 'Confirmed'),
(5, 5, 5, 5, '2026-11-25', 2, 156000, 'Cancelled'),
(6, 6, 6, 6, '2026-12-20', 2, 310000, 'Confirmed');

INSERT INTO itinerary
(booking_id, day_number, activity_date, activity_title,
 activity_description, location)
VALUES
(1, 1, '2026-10-20', 'Arrival Goa', 'Check-in and beach', 'Goa Beach'),
(1, 2, '2026-10-21', 'Water Sports', 'Scuba diving', 'Calangute'),
(2, 1, '2026-11-15', 'Manali Arrival', 'Snow visit', 'Manali'),
(2, 2, '2026-11-16', 'Solang Valley', 'Adventure sports', 'Solang'),
(3, 1, '2026-12-05', 'Dubai Arrival', 'Burj Khalifa', 'Dubai'),
(4, 1, '2026-10-30', 'Kerala Arrival', 'Houseboat', 'Alleppey');

INSERT INTO payments
(booking_id, payment_method, transaction_id, amount, payment_status)
VALUES
(1, 'UPI', 'TXN10001', 48000, 'Success'),
(2, 'Card', 'TXN10002', 93000, 'Success'),
(3, 'Net Banking', 'TXN10003', 112000, 'Pending'),
(4, 'UPI', 'TXN10004', 110000, 'Success'),
(5, 'Card', 'TXN10005', 156000, 'Failed'),
(6, 'UPI', 'TXN10006', 310000, 'Success');

INSERT INTO cancellations
(booking_id, reason, refund_amount, cancellation_status)
VALUES
(5, 'Plan changed', 78000, 'Processed'),
(3, 'Date issue', 10000, 'Requested'),
(1, 'Health issue', 5000, 'Rejected'),
(2, 'Work emergency', 8000, 'Processed'),
(4, 'Family function', 6000, 'Requested'),
(6, 'Visa problem', 15000, 'Processed');

INSERT INTO reviews
(customer_id, destination_id, hotel_id, package_id, rating, review_text)
VALUES
(1, 1, 1, 1, 5, 'Goa super'),
(2, 2, 2, 2, 4, 'Manali amazing'),
(3, 3, 3, 3, 5, 'Dubai luxury'),
(4, 4, 4, 4, 4, 'Kerala beautiful'),
(5, 5, 5, 5, 5, 'Bali paradise'),
(6, 6, 6, 6, 5, 'Paris beautiful');

INSERT INTO trip_history
(customer_id, booking_id, destination_id, trip_start_date,
 trip_end_date, trip_status)
VALUES
(1, 1, 1, '2026-10-20', '2026-10-22', 'Upcoming'),
(2, 2, 2, '2026-11-15', '2026-11-19', 'Upcoming'),
(3, 3, 3, '2026-12-05', '2026-12-08', 'Upcoming'),
(4, 4, 4, '2026-10-30', '2026-11-02', 'Upcoming'),
(5, 5, 5, '2026-11-25', '2026-11-30', 'Cancelled'),
(6, 6, 6, '2026-12-20', '2026-12-26', 'Upcoming');

-- =====================================================
-- VERIFICATION
-- =====================================================



SELECT * FROM customers;
SELECT * FROM destinations;
SELECT * FROM tour_packages;
SELECT * FROM hotels;
SELECT * FROM transport;
SELECT * FROM bookings;
SELECT * FROM itinerary;
SELECT * FROM payments;
SELECT * FROM cancellations;
SELECT * FROM reviews;
SELECT * FROM trip_history;

