# reports.py
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from decimal import Decimal
from .models import Donation, BeneficiarySupport

def monthly_donation_report():
    """
    Aggregates donation amounts (only for Paid donations) grouped by month and donation type.
    """
    report = (
        Donation.objects.filter(status='Paid')
        .annotate(month=TruncMonth('date_time'))
        .values('month', 'donation_type')
        .annotate(total_donations=Sum('amount'))
        .order_by('month', 'donation_type')
    )
    return report

def monthly_allocation_report():
    """
    Aggregates allocation amounts from BeneficiarySupport grouped by month and emergency type.
    Only records with a non-null allocation_amount are considered.
    """
    report = (
        BeneficiarySupport.objects.exclude(allocation_amount__isnull=True)
        .annotate(month=TruncMonth('date'))
        .values('month', 'emergency_type')
        .annotate(total_allocated=Sum('allocation_amount'))
        .order_by('month', 'emergency_type')
    )
    return report

def overall_monthly_summary():
    """
    Merges overall donation and allocation totals per month.
    """
    donation_summary = (
        Donation.objects.filter(status='Paid')
        .annotate(month=TruncMonth('date_time'))
        .values('month')
        .annotate(total_donations=Sum('amount'))
    )
    allocation_summary = (
        BeneficiarySupport.objects.exclude(allocation_amount__isnull=True)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total_allocated=Sum('allocation_amount'))
    )
    
    # Create a dictionary keyed by month with both donation and allocation totals.
    summary = {}
    for entry in donation_summary:
        summary[entry['month']] = {
            'donations': entry['total_donations'] or Decimal('0.00'),
            'allocations': Decimal('0.00')
        }
    for entry in allocation_summary:
        if entry['month'] in summary:
            summary[entry['month']]['allocations'] = entry['total_allocated'] or Decimal('0.00')
        else:
            summary[entry['month']] = {
                'donations': Decimal('0.00'),
                'allocations': entry['total_allocated'] or Decimal('0.00')
            }
    return summary
