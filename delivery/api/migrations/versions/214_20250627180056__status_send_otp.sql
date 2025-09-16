-- upgrade --
UPDATE "status" set "code"='send_otp' WHERE "slug"='u-klienta';
-- downgrade --
UPDATE "status" set "code"=null WHERE "slug"='u-klienta';
