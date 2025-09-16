from .descriptor import Descriptor


class ChannelType(Descriptor):
    SEND_FEEDBACK_LINK = "send_feedback_link"
    SEND_COURIER_ASSIGNED_NOTIFICATION = "send_courier_assigned_notification"
    SEND_CONFIRM_PHONE_OTP = "send_confirm_phone_otp"
    SEND_POST_CONTROL_OTP = "send_post_control_otp"
    SEND_EMAIL_OTP = "send_email_otp"
    SEND_EMAIL_MAGIC_LINK = "send_email_magic_link"
    SEND_EMAIL_VERIFICATION_OTP = "send_email_verification_otp"
    CALL_REQUEST = 'send_call_request'
