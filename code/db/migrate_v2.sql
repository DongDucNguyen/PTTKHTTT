-- Áp các sửa của mục 13 (HUONG_DAN_CODE.md) lên CSDL abc_fashion_v2 đã tạo từ báo cáo (pgAdmin).
-- Chạy một lần:  psql -d abc_fashion_v2 -f migrate_v2.sql
-- Mọi lệnh đều IF EXISTS / IF NOT EXISTS nên chạy lại không sao.

BEGIN;

-- #1 tblReview còn hai cột cũ có CHECK
ALTER TABLE "tblReview" DROP COLUMN IF EXISTS "verified_purchase";
ALTER TABLE "tblReview" DROP COLUMN IF EXISTS "origin";

-- #4 chụp địa chỉ giao hàng vào đơn
ALTER TABLE "tblOrder" ADD COLUMN IF NOT EXISTS "ship_recipient" varchar(255);
ALTER TABLE "tblOrder" ADD COLUMN IF NOT EXISTS "ship_phone"     varchar(20);
ALTER TABLE "tblOrder" ADD COLUMN IF NOT EXISTS "ship_address"   varchar(500);

-- #5 COD / chuyển khoản không có phương thức liên kết
ALTER TABLE "tblPayment" ALTER COLUMN "paymentMethodId" DROP NOT NULL;

-- Bổ sung: biến thể thay thế cho dòng đổi hàng
ALTER TABLE "tblReturnItem" ADD COLUMN IF NOT EXISTS "replacementVariantId" integer
    REFERENCES "tblProductVariant"("id") ON DELETE RESTRICT;

-- SavedSizeDAO.save_saved_size dùng ON CONFLICT ("customerId","categoryId")
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint c
        WHERE c.conrelid = '"tblSavedSize"'::regclass AND c.contype IN ('u', 'p')
          AND (SELECT array_agg(a.attname::text ORDER BY a.attname::text) FROM pg_attribute a
               WHERE a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)) = ARRAY['categoryId', 'customerId']) THEN
        ALTER TABLE "tblSavedSize" ADD CONSTRAINT "uq_tblSavedSize_customer_category" UNIQUE ("customerId", "categoryId");
    END IF;
END $$;

COMMIT;
