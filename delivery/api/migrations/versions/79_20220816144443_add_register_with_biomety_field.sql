-- upgrade --
ALTER TABLE "profile_courier" ADD "register_with_biometry" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "profile_courier" DROP COLUMN "register_with_biometry";
