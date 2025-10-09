-- upgrade --
CREATE TABLE item_pan_validation_mask (
    id SERIAL PRIMARY KEY,
    mask VARCHAR(16) NOT NULL,
    item_id INT NOT NULL,
    CONSTRAINT uq_item_pan_validation_mask_item_mask UNIQUE (item_id, mask),
    CONSTRAINT fk_item_pan_validation_mask_item FOREIGN KEY (item_id) REFERENCES item (id) ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS item_pan_validation_mask;
