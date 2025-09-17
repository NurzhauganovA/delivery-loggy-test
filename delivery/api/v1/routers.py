import fastapi

from .endpoints import(
    area,
    biometry,
    country,
    deliverygraph,
    direction,
    external_service_history,
    feedback,
    firebase,
    group,
    history,
    item,
    category,
    monitoring,
    order,
    otp,
    partner,
    permission,
    place,
    postcontrol,
    profile,
    public_api_token,
    register,
    status,
    token,
    transport,
    user,
    verification,
    ws_monitoring,
    external,
    statistics,
)
from ..modules.delivery_point import v1 as delivery_point
from ..modules.call_request import routes as call_request
from ..modules.city import v1 as city
from ..modules.shipment_point import v1 as shipment_point
from ..modules.monitoring import routes as monitoring_module
from ..modules.order import routes as order_module
from ..modules.partner_settings import routes as partner_setting
from ..modules.order_chain import v1 as order_chain


api_router = fastapi.APIRouter(prefix='/v1')
api_router.include_router(city.router, tags=['city'])
api_router.include_router(country.router, tags=['country'])
api_router.include_router(firebase.router, tags=['device'])
api_router.include_router(group.router, tags=['group'])
api_router.include_router(item.router, tags=['item'])
api_router.include_router(call_request.router, tags=['call_request'])
api_router.include_router(category.router, tags=['category'])
api_router.include_router(ws_monitoring.router, tags=['ws_monitoring'])
api_router.include_router(monitoring.router, tags=['monitoring'])
api_router.include_router(otp.router, tags=['otp'])
api_router.include_router(order.router, tags=['order'])
api_router.include_router(partner.router, tags=['partner'])
api_router.include_router(permission.router, tags=['permission'])
api_router.include_router(postcontrol.router, tags=['postcontrol'])
api_router.include_router(place.router, tags=['place'])
api_router.include_router(profile.router, tags=['profile'])
api_router.include_router(register.router, tags=['register'])
api_router.include_router(token.router, tags=['token'])
api_router.include_router(transport.router, tags=['transport'])
api_router.include_router(user.router, tags=['user'])
api_router.include_router(verification.router, tags=['verification'])
api_router.include_router(status.router, tags=['status'])
api_router.include_router(deliverygraph.router, tags=['deliverygraph'])
api_router.include_router(biometry.router, tags=['biometry'])
api_router.include_router(area.router, tags=['area'])
api_router.include_router(history.router, tags=['history'])
api_router.include_router(public_api_token.router, tags=['publicapitoken'])
api_router.include_router(direction.router, tags=['direction'])
api_router.include_router(
    external_service_history.router,
    tags=['external_service_history'],
)
api_router.include_router(feedback.router, tags=['feedback'])
api_router.include_router(external.router, tags=['external'])
api_router.include_router(delivery_point.router, tags=['delivery_point'])
api_router.include_router(shipment_point.router, tags=['shipment_point'])
api_router.include_router(monitoring_module.router, tags=['monitoring_new'])
api_router.include_router(order_module.router, tags=['order_group'])
api_router.include_router(partner_setting.router, tags=['partner_settings'])
api_router.include_router(statistics.router, tags=['statistics'])
api_router.include_router(order_chain.router, tags=['order_chain'])
