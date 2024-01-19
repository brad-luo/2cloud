from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .forms import ProductForm
from .models import Product


@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})


@login_required
def product_upload(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('product_list')  # Redirect to a product list page or any other page
    else:
        form = ProductForm()

    return render(request, 'product_upload.html', {'form': form})

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_edit.html', {'form': form, 'product': product})

@login_required
@csrf_exempt
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'DELETE':
        product.delete()
        return JsonResponse({'deleted': True}, status=200)


@login_required
def product_list(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'product_list.html', {'products': products})


@login_required
def product_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        products = Product.objects.filter(user=request.user).filter(Q(name__icontains=search_query) |
                                                                    Q(code__icontains=search_query) |
                                                                    Q(color=search_query) |
                                                                    Q(size=search_query))

        product_list = [{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'code': product.code,
            'color': product.color,
            'size': product.size,
            'image': product.image.url if product.image else None,
        } for product in products]

        return JsonResponse(product_list, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
