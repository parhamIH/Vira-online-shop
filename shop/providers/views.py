from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from shop.products.models import Product, ProductPackage
from shop.providers.permissions import provider_required

@login_required
@provider_required
def provider_panel(request):
    if not hasattr(request.user, 'provider_profile'):
        return render(request, 'frontend/403.html', status=403)

    provider = request.user.provider_profile

    products = Product.objects.filter(product_packages__provider=provider).distinct()
    packages = ProductPackage.objects.filter(provider=provider)

    total_sales = packages.aggregate(total=Sum('sold_count'))['total'] or 0

    return render(request, 'frontend/templateAdmin/index.html', {
        'provider': provider,
        'products': products,
        'packages': packages,
        'total_sales': total_sales,
    })

def register_provider (request):
    if request.method == "POST":
        ...
    else:
        ...

    return render(request,'frontend/templateAdmin/register-provider.html',context=None)