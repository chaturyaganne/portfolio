-- Property-level aggregates pre-aggregate facts to avoid join fanout.
DROP VIEW IF EXISTS mart_property_summary;
CREATE VIEW mart_property_summary AS
WITH lease_totals AS (
 SELECT property_id,COUNT(*) AS lease_count,SUM(monthly_rent_cents) AS monthly_rent_cents
 FROM leases GROUP BY property_id
), payment_totals AS (
 SELECT l.property_id,COUNT(*) AS payment_count,SUM(p.amount_cents) AS payment_amount_cents
 FROM payments p JOIN leases l ON l.lease_id=p.lease_id GROUP BY l.property_id
)
SELECT d.property_id,d.city,d.state,d.unit_count,COALESCE(l.lease_count,0) AS lease_count,
 COALESCE(l.monthly_rent_cents,0) AS monthly_rent_cents,COALESCE(p.payment_count,0) AS payment_count,
 COALESCE(p.payment_amount_cents,0) AS payment_amount_cents
FROM properties d LEFT JOIN lease_totals l ON l.property_id=d.property_id
LEFT JOIN payment_totals p ON p.property_id=d.property_id;
DROP VIEW IF EXISTS mart_property_day;
CREATE VIEW mart_property_day AS
SELECT l.property_id,p.paid_at AS activity_date,COUNT(*) AS payment_count,
 SUM(p.amount_cents) AS payment_amount_cents,COUNT(DISTINCT p.lease_id) AS distinct_leases
FROM payments p JOIN leases l ON l.lease_id=p.lease_id
GROUP BY l.property_id,p.paid_at;
-- These are curated operational aggregates, not point-in-time training features or underwriting decisions.
