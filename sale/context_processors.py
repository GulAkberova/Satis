from .models import Basket


def extra(request):
    context = {}

    basket_count = 0
    if request.user.is_authenticated:
        basket_count = Basket.objects.filter(user=request.user).count()

    context["basket_count"] = basket_count
    return context