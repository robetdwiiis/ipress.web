from store.models import Order, CommissionLog
CommissionLog.objects.all().delete()
Order.objects.all().delete()
print("All orders and commission logs deleted.")
