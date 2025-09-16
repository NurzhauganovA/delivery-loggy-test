-- upgrade --
DELETE FROM "profile_sorter" WHERE TRUE;
ALTER TABLE "profile_sorter" ADD "shipment_point_id" INT NOT NULL;
ALTER TABLE "profile_sorter" ADD CONSTRAINT "fk_profile__partner__c9ace6ca" FOREIGN KEY ("shipment_point_id") REFERENCES "partner_shipment_point" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "profile_sorter" DROP CONSTRAINT "fk_profile__partner__c9ace6ca";
ALTER TABLE "profile_sorter" DROP COLUMN "shipment_point_id";
