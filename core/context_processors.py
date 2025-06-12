from datetime import datetime
from .models import CompanyInfo

def current_year(request):
    return {"current_year": datetime.now().year}





def company_info(request):
    try:
        company = CompanyInfo.objects.first()
        return {
            'company_info': company
        }
    except Exception:
        return {
            'company_info': None
        }