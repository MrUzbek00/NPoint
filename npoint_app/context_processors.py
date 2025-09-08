from django.db.models import Sum
from .models import UserProfile, JSONData

def humanize_number(value):
    """Format numbers as 1.2K, 3.4M, etc."""
    if value is None:
        return "0"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M".rstrip("0").rstrip(".")
    if value >= 1_000:
        return f"{value/1_000:.1f}K".rstrip("0").rstrip(".")
    return str(value)

def site_stats(request):
    total_users = UserProfile.objects.count()
    total_jsons = JSONData.objects.count()
    total_api_calls = JSONData.objects.aggregate(total=Sum("access_count"))["total"] or 0
    
    return {
        "total_users": humanize_number(total_users),
        "total_jsons": humanize_number(total_jsons),
        "total_api_calls": humanize_number(total_api_calls),
    }