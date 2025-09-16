-- upgrade --
ALTER TABLE "profile_courier" ALTER COLUMN "at_work" SET DEFAULT False;
update "profile_courier" set at_work = False;
ALTER TABLE "profile_courier" ALTER COLUMN "at_work" SET NOT NULL;
-- downgrade --
ALTER TABLE "profile_courier" ALTER COLUMN "at_work" DROP NOT NULL;
ALTER TABLE "profile_courier" ALTER COLUMN "at_work" DROP DEFAULT;
