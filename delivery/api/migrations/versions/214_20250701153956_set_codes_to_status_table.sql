-- upgrade --
UPDATE status
SET code = 'new'
WHERE id = 1;

UPDATE status
SET code = 'accepted_by_courier_service'
WHERE id = 29;

UPDATE status
SET code = 'courier_assigned'
WHERE id = 2;

UPDATE status
SET code = 'in_way'
WHERE id = 3;

UPDATE status
SET code = 'send_otp'
WHERE id = 25;

UPDATE status
SET code = 'verify_otp'
WHERE id = 20;

UPDATE status
SET code = 'photo_capturing'
WHERE id = 16;

UPDATE status
SET code = 'post_control'
WHERE id = 12;

UPDATE status
SET code = 'delivered'
WHERE id = 7;

UPDATE status
SET code = 'card_returned_to_bank'
WHERE id = 35;
-- downgrade --
UPDATE status
SET code = null
WHERE id = 1;

UPDATE status
SET code = null
WHERE id = 29;

UPDATE status
SET code = null
WHERE id = 2;

UPDATE status
SET code = null
WHERE id = 3;

UPDATE status
SET code = null
WHERE id = 25;

UPDATE status
SET code = null
WHERE id = 20;

UPDATE status
SET code = null
WHERE id = 16;

UPDATE status
SET code = null
WHERE id = 12;

UPDATE status
SET code = null
WHERE id = 7;

UPDATE status
SET code = null
WHERE id = 35;
