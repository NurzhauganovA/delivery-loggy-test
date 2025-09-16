-- upgrade --
update
    "order" o
set shipment_point_id=sp.sp_id
from (select distinct on (oa.order_id) sp.id sp_id,
                                       sp.latitude,
                                       sp.longitude,
                                       sp.name,
                                       sp.partner_id,
                                       oa.order_id
      from "partner_shipment_point" sp
               left join (select oa.type, oa.order_id, p.latitude, p.longitude
                          from "order.addresses" oa
                                   left join place p on p.id = oa.place_id) oa
                         on sp.latitude = oa.latitude and sp.longitude = oa.longitude) sp
where o.id = sp.order_id returning o.id, o.shipment_point_id, o.type, sp.order_id sp_o_id, sp.sp_id;;
insert into "delivery_point"
    (address, latitude, longitude)
    (select
        distinct on (p.latitude, p.longitude)
         p.address,
                                                  p.latitude,
                                                  p.longitude
     from "order.addresses" oa
              left join place p on p.id = oa.place_id
     where oa.type = 'delivery_point') returning id, address, latitude, longitude;;
update "order" o
set delivery_point_id=dp.id
from (select id, order_id
      from "delivery_point" dp
               left join (select distinct on (oa.order_id) oa.order_id order_id,
                                                           p.latitude  latitude,
                                                           p.longitude longitude
                          from "order.addresses" oa
                                   left join place p on p.id = oa.place_id
                          where oa.type = 'delivery_point') oa
                         on oa.latitude = dp.latitude and oa.longitude = dp.longitude) dp
where dp.order_id = o.id;
-- downgrade --
select '1';