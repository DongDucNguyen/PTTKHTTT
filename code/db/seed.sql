-- Dữ liệu mẫu cho abc_fashion_v2. Mật khẩu mẫu ở dạng bản rõ "abc12345";
-- UserDAO.check_login chấp nhận bản rõ và băm lại ngay lần đăng nhập đầu (mục 13 #15).
-- Sổ kho khớp tồn: với mọi biến thể, Σ quantity_change = on_hand.

BEGIN;

-- ---------------------------------------------------------------- tài khoản
INSERT INTO "tblUser"("id","email","password","status","created_at") VALUES
 (1,'admin@abc.vn','abc12345','active','2026-08-01 08:00'),
 (2,'manager@abc.vn','abc12345','active','2026-08-01 08:00'),
 (3,'merch@abc.vn','abc12345','active','2026-08-01 08:00'),
 (4,'marketing@abc.vn','abc12345','active','2026-08-01 08:00'),
 (5,'cs@abc.vn','abc12345','active','2026-08-01 08:00'),
 (6,'warehouse@abc.vn','abc12345','active','2026-08-01 08:00'),
 (7,'sales@abc.vn','abc12345','active','2026-08-01 08:00'),
 (8,'supplier@vaidep.vn','abc12345','active','2026-08-01 08:00'),
 (9,'supplier@denimviet.vn','abc12345','active','2026-08-01 08:00'),
 (10,'an.nguyen@gmail.com','abc12345','active','2026-08-10 09:00'),
 (11,'binh.tran@gmail.com','abc12345','active','2026-08-12 10:00'),
 (12,'khoa.le@gmail.com','abc12345','suspended','2026-08-20 11:00');

INSERT INTO "tblStaffMember"("id","code","full_name","role","userId") VALUES
 (1,'ADM01','Phạm Quản Trị','administrator',1),
 (2,'MGR01','Lê Quản Lý','manager',2),
 (3,'MER01','Vũ Merchandiser','merchandiser',3),
 (4,'MKT01','Đỗ Marketing','marketing',4),
 (5,'CS01','Hoàng Chăm Sóc','customer_service',5),
 (6,'WH01','Bùi Thủ Kho','warehouse',6),
 (7,'SAL01','Ngô Bán Hàng','sales',7);

INSERT INTO "tblSupplier"("id","name","email","phone","userId") VALUES
 (1,'Công ty May Vải Đẹp','supplier@vaidep.vn','02437654321',8),
 (2,'Denim Việt','supplier@denimviet.vn','02838765432',9);

INSERT INTO "tblCustomer"("id","full_name","phone","marketing_consent","preferred_colours","userId") VALUES
 (1,'Nguyễn Văn An','0901234567',true,'Đen,Trắng',10),
 (2,'Trần Thị Bình','0912345678',false,'Đỏ',11),
 (3,'Lê Minh Khoa','0923456789',false,NULL,12);

-- ---------------------------------------------------------------- danh mục
INSERT INTO "tblStockLocation"("id","name","address") VALUES
 (1,'Kho Hà Nội','12 Phạm Hùng, Cầu Giấy, Hà Nội'),
 (2,'Kho TP.HCM','45 Quang Trung, Gò Vấp, TP.HCM');

INSERT INTO "tblCategory"("id","name","parentId") VALUES
 (1,'Nữ',NULL),(2,'Nam',NULL),
 (3,'Áo nữ',1),(4,'Váy',1),(5,'Áo nam',2),(6,'Quần nam',2);

INSERT INTO "tblCollection"("id","name","season","year") VALUES
 (1,'Xuân Hè 2026','spring_summer',2026),
 (2,'Thu Đông 2026','autumn_winter',2026);

INSERT INTO "tblStyle"("id","code","name","description","brand","fit_type","care_instructions","features","model_info",
                       "status","categoryId","supplierId","collectionId") VALUES
 (1,'ST-W001','Áo sơ mi lụa nữ','Áo sơ mi lụa tơ tằm, cổ đức, tay dài, mặc đi làm hoặc dạo phố.','ABC Basic','regular',
  'Giặt tay nước lạnh, không vắt mạnh, phơi trong bóng râm.','Cổ đức; cúc ngọc trai; vải không nhăn',
  'Người mẫu cao 168 cm, mặc cỡ S','active',3,1,1),
 (2,'ST-W002','Váy liền midi hoa','Váy midi hoạ tiết hoa nhí, eo chun, dáng xoè nhẹ.','ABC Studio','relaxed',
  'Giặt máy chế độ nhẹ, nhiệt độ ≤ 30°C.','Eo chun; có lót; túi hai bên',
  'Người mẫu cao 165 cm, mặc cỡ M','active',4,1,1),
 (3,'ST-M001','Áo thun cotton nam','Áo thun cổ tròn 100% cotton compact, thấm hút mồ hôi.','ABC Basic','slim',
  'Giặt máy, lộn trái khi giặt, không dùng chất tẩy.','Cổ bo rib; chống co rút',
  'Người mẫu cao 178 cm, mặc cỡ M','active',5,1,1),
 (4,'ST-M002','Quần jeans nam slim','Quần jeans xanh wash nhẹ, co giãn 2 chiều.','Denim Việt','slim',
  'Giặt lộn trái, nước lạnh, hạn chế sấy.','Co giãn; 5 túi; khoá kéo YKK',
  'Người mẫu cao 180 cm, mặc cỡ 30','active',6,2,2);

INSERT INTO "tblProductVariant"("id","sku","size_label","colour","price","status","styleId") VALUES
 (1,'W001-WHT-S','S','Trắng',450000,'active',1),
 (2,'W001-WHT-M','M','Trắng',450000,'active',1),
 (3,'W002-RED-M','M','Đỏ',690000,'active',2),
 (4,'W002-BLU-M','M','Xanh',690000,'active',2),
 (5,'M001-BLK-M','M','Đen',250000,'active',3),
 (6,'M001-BLK-L','L','Đen',250000,'active',3),
 (7,'M002-BLU-30','30','Xanh',590000,'active',4),
 (8,'M002-BLU-32','32','Xanh',590000,'active',4);

INSERT INTO "tblProductMedia"("id","url","media_type","colour","sort_order","styleId") VALUES
 (1,'media/st-w001-1.png','image','Trắng',1,1),
 (2,'media/st-w002-1.png','image','Đỏ',1,2),
 (3,'media/st-w002-2.png','image','Xanh',2,2),
 (4,'media/st-m001-1.png','image','Đen',1,3),
 (5,'media/st-m002-1.png','image','Xanh',1,4);

INSERT INTO "tblMaterialComponent"("id","material","percent","styleId") VALUES
 (1,'Lụa tơ tằm',100,1),
 (2,'Viscose',70,2),(3,'Polyester',30,2),
 (4,'Cotton',95,3),(5,'Spandex',5,3),
 (6,'Cotton',98,4),(7,'Elastane',2,4);

INSERT INTO "tblSizeChartEntry"("id","size_label","measure","value_cm","styleId") VALUES
 (1,'S','chest',86,1),(2,'S','length',62,1),(3,'M','chest',90,1),(4,'M','length',64,1),
 (5,'M','chest',88,2),(6,'M','waist',70,2),(7,'M','length',110,2),
 (8,'M','chest',96,3),(9,'M','length',68,3),(10,'L','chest',102,3),(11,'L','length',70,3),
 (12,'30','waist',76,4),(13,'30','inseam',78,4),(14,'32','waist',81,4),(15,'32','inseam',80,4);

-- ---------------------------------------------------------------- tồn kho (mỗi biến thể một dòng, một kho)
INSERT INTO "tblStockLevel"("id","on_hand","reserved","reorder_point","available","productVariantId","stockLocationId") VALUES
 (1,20,0,5,20,1,1),
 (2,15,0,5,15,2,1),
 (3,10,0,3,10,3,2),
 (4,2,0,3,2,4,2),
 (5,49,0,10,49,5,1),
 (6,30,0,10,30,6,2),
 (7,12,0,5,12,7,2),
 (8,1,0,5,1,8,1);

-- ---------------------------------------------------------------- dữ liệu khách
INSERT INTO "tblAddress"("id","recipient_name","phone","street","ward","district","city","is_default","customerId") VALUES
 (1,'Nguyễn Văn An','0901234567','18 Hoàng Quốc Việt','Nghĩa Đô','Cầu Giấy','Hà Nội',true,1),
 (2,'Nguyễn Văn An','0901234567','99 Lê Lợi','Bến Nghé','Quận 1','TP.HCM',false,1),
 (3,'Trần Thị Bình','0912345678','7 Trần Hưng Đạo','Phan Chu Trinh','Hoàn Kiếm','Hà Nội',true,2);

INSERT INTO "tblPaymentMethod"("id","provider","method_type","masked_number","is_default","customerId") VALUES
 (1,'Visa','card','**** 4242',true,1),
 (2,'Visa','card','**** 0002',false,1),     -- thẻ sandbox luôn bị từ chối (UC08 E2)
 (3,'MoMo','e_wallet','**** 8888',true,2);

INSERT INTO "tblSavedSize"("id","size_label","customerId","categoryId") VALUES
 (1,'M',1,5),(2,'30',1,6),(3,'M',2,4);

INSERT INTO "tblCart"("id","updated_at","subtotal","customerId") VALUES
 (1,'2026-10-20 10:00',0,1),(2,'2026-10-05 09:00',0,2),(3,'2026-08-20 11:00',0,3);

-- ---------------------------------------------------------------- khuyến mãi
INSERT INTO "tblPromotion"("id","name","promo_type","discount_type","discount_value","min_order_value",
                           "starts_at","ends_at","status") VALUES
 (1,'Xuân Hè giảm 10%','seasonal','percent',10,300000,'2026-10-01','2026-12-31 23:59','active'),
 (2,'Flash sale áo thun','flash_sale','fixed_amount',50000,0,'2026-10-25','2026-11-30 23:59','active'),
 (3,'Thanh lý hè 2025','clearance','percent',30,0,'2025-06-01','2025-08-31 23:59','ended');

INSERT INTO "tblPromotionStyle"("id","promotionId","styleId") VALUES
 (1,1,1),(2,1,2),(3,2,3),(4,3,4);

INSERT INTO "tblVoucher"("id","code","usage_limit","used_count","promotionId") VALUES
 (1,'XUANHE10',100,0,1),
 (2,'HETLUOT',1,1,1),
 (3,'THANHLY30',50,5,3);

-- ---------------------------------------------------------------- đơn hàng mẫu
INSERT INTO "tblOrder"("id","order_no","status","placed_at","subtotal","discount","shipping_fee","grand_total",
                       "delivery_service","note","cancel_reason","ship_recipient","ship_phone","ship_address","customerId") VALUES
 (1,'ORD-260901-001','completed','2026-09-01 14:20',950000,0,0,950000,'standard',NULL,NULL,
  'Nguyễn Văn An','0901234567','18 Hoàng Quốc Việt, Nghĩa Đô, Cầu Giấy, Hà Nội',1),
 (2,'ORD-261005-001','delivered','2026-10-05 09:10',1140000,0,0,1140000,'express','Giao giờ hành chính',NULL,
  'Trần Thị Bình','0912345678','7 Trần Hưng Đạo, Phan Chu Trinh, Hoàn Kiếm, Hà Nội',2),
 (3,'ORD-261020-001','confirmed','2026-10-20 10:05',590000,0,0,590000,'standard',NULL,NULL,
  'Nguyễn Văn An','0901234567','18 Hoàng Quốc Việt, Nghĩa Đô, Cầu Giấy, Hà Nội',1);

INSERT INTO "tblOrderItem"("id","quantity","unit_price","discount","line_total","orderId","productVariantId") VALUES
 (1,1,450000,0,450000,1,1),
 (2,2,250000,0,500000,1,5),
 (3,1,690000,0,690000,2,3),
 (4,1,450000,0,450000,2,2),
 (5,1,590000,0,590000,3,7);

INSERT INTO "tblPayment"("id","kind","method","amount","status","transaction_ref","created_at","orderId","paymentMethodId") VALUES
 (1,'charge','card',950000,'succeeded','SBX-0A1B2C3D4E5F','2026-09-01 14:21',1,1),
 (2,'refund','card',250000,'succeeded','SBX-R-9F8E7D6C5B','2026-09-09 10:00',1,1),
 (3,'charge','cod',1140000,'succeeded','COD-ORD-261005-001','2026-10-08 16:00',2,NULL),
 (4,'charge','card',590000,'succeeded','SBX-1122334455AA','2026-10-20 10:06',3,1);

INSERT INTO "tblReturnRequest"("id","return_no","return_type","reason_code","reason_detail","desired_resolution","status",
                               "requested_at","decided_at","decision_note","orderId","staffMemberId") VALUES
 (1,'RET-260905-001','return','too_small','Áo hơi chật ở vai','refund','closed',
  '2026-09-05 08:30','2026-09-05 15:00','Đồng ý nhận lại',1,5);

INSERT INTO "tblReturnItem"("id","quantity","inspection_result","inspection_note","returnRequestId","orderItemId") VALUES
 (1,1,'passed','Hàng còn nguyên tem',1,2);

INSERT INTO "tblShipment"("id","direction","carrier","service_level","tracking_no","fee","status","delivered_at",
                          "orderId","stockLocationId","returnRequestId") VALUES
 (1,'outbound','GHN-SANDBOX','standard','GHN00000001',0,'delivered','2026-09-03 11:00',1,1,NULL),
 (2,'return','GHN-SANDBOX','standard','GHN00000002',0,'delivered','2026-09-07 15:00',1,1,1),
 (3,'outbound','GHN-SANDBOX','express','GHN00000003',0,'delivered','2026-10-08 15:30',2,2,NULL),
 (4,'outbound','GHN-SANDBOX','express','GHN00000004',0,'delivered','2026-10-08 16:00',2,1,NULL),
 (5,'outbound',NULL,'standard',NULL,0,'requested',NULL,3,2,NULL);

INSERT INTO "tblShipmentRecord"("id","quantity","shipmentId","orderItemId") VALUES
 (1,1,1,1),(2,2,1,2),(3,1,2,2),(4,1,3,3),(5,1,4,4),(6,1,5,5);

INSERT INTO "tblShipmentEvent"("id","status","occurred_at","note","shipmentId") VALUES
 (1,'picked_up','2026-09-01 18:00','Đã lấy hàng tại Kho Hà Nội',1),
 (2,'in_transit','2026-09-02 08:00','Đang vận chuyển',1),
 (3,'delivered','2026-09-03 11:00','Giao thành công',1),
 (4,'picked_up','2026-09-06 09:00','Đã lấy hàng trả từ khách',2),
 (5,'delivered','2026-09-07 15:00','Đã về Kho Hà Nội',2),
 (6,'picked_up','2026-10-06 17:00','Đã lấy hàng tại Kho TP.HCM',3),
 (7,'delivered','2026-10-08 15:30','Giao thành công',3),
 (8,'picked_up','2026-10-06 18:00','Đã lấy hàng tại Kho Hà Nội',4),
 (9,'delivered','2026-10-08 16:00','Giao thành công',4);

INSERT INTO "tblReview"("id","rating","body","size_purchased","fit_vote","status","moderation_note","created_at",
                        "orderItemId","staffMemberId") VALUES
 (1,5,'Lụa mát, form đẹp, mặc đi làm rất ổn.','S','true_to_size','approved',NULL,'2026-09-04 20:00',1,NULL),
 (2,4,'Áo đẹp, vải dày dặn nhưng hơi chật, nên lấy lên một cỡ.','M','runs_small','approved',NULL,'2026-09-04 20:05',2,NULL),
 (3,3,'Váy đẹp nhưng giao hơi lâu. Ai cần pass lại liên hệ 0987654321.','M','true_to_size','pending',
  'Chứa số điện thoại','2026-10-09 21:00',3,NULL);

-- Sổ kho: tồn đầu kỳ (adjustment) + bán + trả, khớp tblStockLevel.on_hand
INSERT INTO "tblStockMovement"("id","quantity_change","reason","reference","note","created_at",
                               "productVariantId","stockLocationId","staffMemberId") VALUES
 (1,21,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',1,1,6),
 (2,16,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',2,1,6),
 (3,11,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',3,2,6),
 (4,2,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',4,2,6),
 (5,50,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',5,1,6),
 (6,30,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',6,2,6),
 (7,13,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',7,2,6),
 (8,1,'adjustment','OPENING','Tồn đầu kỳ','2026-08-15 08:00',8,1,6),
 (9,-1,'sale','ORD-260901-001',NULL,'2026-09-01 14:21',1,1,NULL),
 (10,-2,'sale','ORD-260901-001',NULL,'2026-09-01 14:21',5,1,NULL),
 (11,1,'return','RET-260905-001','Kiểm tra đạt','2026-09-08 09:00',5,1,6),
 (12,-1,'sale','ORD-261005-001',NULL,'2026-10-05 09:10',3,2,NULL),
 (13,-1,'sale','ORD-261005-001',NULL,'2026-10-05 09:10',2,1,NULL),
 (14,-1,'sale','ORD-261020-001',NULL,'2026-10-20 10:06',7,2,NULL);

-- ---------------------------------------------------------------- nhập hàng
INSERT INTO "tblRestockRequest"("id","request_no","status","created_at","expected_date","supplier_note","confirm_at",
                                "supplierId","stockLocationId","staffMemberId") VALUES
 (1,'RST-261025-001','sent','2026-10-25 09:00',NULL,NULL,NULL,2,1,6),
 (2,'RST-261026-001','draft','2026-10-26 14:00',NULL,NULL,NULL,1,2,6);

INSERT INTO "tblRestockItem"("id","quantity","restockRequestId","productVariantId") VALUES
 (1,20,1,8),(2,10,2,4);

-- ---------------------------------------------------------------- thông báo, nhật ký, trợ lý
INSERT INTO "tblNotification"("id","channel","event_type","message","status","sent_at","customerId") VALUES
 (1,'email','order_confirmed','Đơn ORD-260901-001 đã được xác nhận.','sent','2026-09-01 14:21',1),
 (2,'email','order_delivered','Đơn ORD-260901-001 đã giao thành công.','sent','2026-09-03 11:00',1),
 (3,'email','refund_completed','Đã hoàn 250.000 đ cho yêu cầu RET-260905-001.','sent','2026-09-09 10:00',1),
 (4,'sms','order_confirmed','Đơn ORD-261005-001 đã được xác nhận.','sent','2026-10-05 09:10',2),
 (5,'email','order_confirmed','Đơn ORD-261020-001 đã được xác nhận.','sent','2026-10-20 10:06',1);

INSERT INTO "tblAuditLogEntry"("id","entity","action","changes","created_at","staffMemberId") VALUES
 (1,'tblStockLevel#4','adjust_stock','Tồn đầu kỳ W002-BLU-M: +2','2026-08-15 08:00',6),
 (2,'tblUser#12','suspend_account','status: active -> suspended','2026-10-01 09:00',1),
 (3,'tblStyle#4','update','status: draft -> active','2026-08-15 10:00',2);

INSERT INTO "tblAssistantTurn"("id","question","answer","mode","model_name","latency_ms","created_at","customerId","styleId") VALUES
 (1,'Áo này chất liệu gì?','Áo sơ mi lụa nữ làm từ: Lụa tơ tằm 100%.','basic','basic-template',12,'2026-10-20 09:50',1,1);

COMMIT;

-- Đưa các identity về sau giá trị lớn nhất đã chèn
DO $$
DECLARE r record;
BEGIN
    FOR r IN SELECT table_name FROM information_schema.columns
             WHERE table_schema = 'public' AND column_name = 'id' AND is_identity = 'YES' LOOP
        EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, ''id''), coalesce((SELECT max("id") FROM %I), 0) + 1, false)',
                       '"' || r.table_name || '"', r.table_name);
    END LOOP;
END $$;
