from django.conf import settings

def app_information(request):
    return {
        "business_name": settings.BUSINESS_NAME,
        "business_logo": settings.BUSINESS_LOGO,
        "contact_email": settings.CONTACT_EMAIL,
    }