from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import Product
from math import ceil

def index(request):
    products = list(Product.objects.all())
    catprods = Product.objects.values('category', 'id')
    cats = sorted(list({items['category'] for items in catprods if items['category']}))

    allProds = []
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4)) if n > 0 else 1
        allProds.append([prod, range(1, nSlides), nSlides, cat])

    featured_products = products[:4] if len(products) >= 4 else products

    params = {
        'allProds': allProds,
        'products': products,
        'categories': cats,
        'featured_products': featured_products,
        'total_products': len(products)
    }
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        # Return success flag in template
        return render(request, 'shop/contact.html', {'thank': True, 'name': name})
    return render(request, 'shop/contact.html')

def tracker(request):
    order_id = request.GET.get('orderId', '')
    email = request.GET.get('email', '')
    tracked = bool(order_id and email)
    return render(request, 'shop/tracker.html', {'order_id': order_id, 'email': email, 'tracked': tracked})

def search(request):
    query = request.GET.get('search', '').strip()
    results = []
    if query:
        results = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(desc__icontains=query) |
            Q(category__icontains=query) |
            Q(subcategory__icontains=query)
        )
    return render(request, 'shop/search.html', {'query': query, 'products': results, 'count': len(results)})

def productview(request, myid=None):
    if myid is None:
        myid = request.GET.get('id')
    
    if myid:
        try:
            product = Product.objects.get(id=myid)
            related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
            return render(request, 'shop/prodView.html', {'product': product, 'related': related})
        except Product.DoesNotExist:
            pass
            
    # Default to first product if none specified
    product = Product.objects.first()
    related = Product.objects.exclude(id=product.id)[:4] if product else []
    return render(request, 'shop/prodView.html', {'product': product, 'related': related})

def checkout(request):
    if request.method == "POST":
        # Simulate order confirmation
        order_id = "NEXUS-" + str(abs(hash(request.POST.get('name', 'guest'))))[:6]
        return render(request, 'shop/checkout.html', {'thank': True, 'order_id': order_id})
    return render(request, 'shop/checkout.html')


# ==============================================================================
# OPERATIONS & INVENTORY CONTROL VIEWS
# ==============================================================================

def admin_dashboard(request):
    """
    Executive E-Commerce Operations & Inventory Control Center
    """
    # Check for category / search filter in dashboard
    category_filter = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    products_qs = Product.objects.all().order_by('-id')

    if category_filter and category_filter.lower() != 'all':
        products_qs = products_qs.filter(category__iexact=category_filter)

    if search_query:
        products_qs = products_qs.filter(
            Q(product_name__icontains=search_query) |
            Q(desc__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(subcategory__icontains=search_query)
        )

    products = list(products_qs)
    all_products = list(Product.objects.all())
    
    # Metrics
    total_products = len(all_products)
    total_valuation = sum(p.price for p in all_products)
    avg_price = round(total_valuation / total_products, 2) if total_products > 0 else 0
    
    # Categories & counts
    all_categories = sorted(list({p.category for p in all_products if p.category}))
    category_counts = []
    for cat in all_categories:
        count = sum(1 for p in all_products if p.category == cat)
        category_counts.append({'name': cat, 'count': count})
        
    subcategories = sorted(list({p.subcategory for p in all_products if p.subcategory}))

    # Available preset sample images in media/shop/images
    preset_images = [
        {'name': 'Laptop & Tech', 'path': 'shop/images/Laptop.jpg'},
        {'name': 'Audio & Headphones', 'path': 'shop/images/headphone.jpg'},
        {'name': 'Optics & Camera', 'path': 'shop/images/camera.jpg'},
        {'name': 'Luxury Chrono & Watch', 'path': 'shop/images/watch.jpg'},
        {'name': 'Footwear & Streetwear', 'path': 'shop/images/shoes.jpg'},
        {'name': 'Cosmetics & Fragrance', 'path': 'shop/images/Perfume.jpg'},
    ]

    context = {
        'products': products,
        'all_products_count': total_products,
        'filtered_count': len(products),
        'total_valuation': total_valuation,
        'avg_price': avg_price,
        'categories': all_categories,
        'category_counts': category_counts,
        'subcategories': subcategories,
        'preset_images': preset_images,
        'selected_category': category_filter or 'all',
        'search_query': search_query,
        'user_is_staff': request.user.is_authenticated and request.user.is_staff,
    }
    return render(request, 'shop/admin_dashboard.html', context)


def admin_add_product(request):
    """
    Handle adding a new product/inventory item
    """
    if request.method == "POST":
        product_name = request.POST.get('product_name', '').strip()
        custom_category = request.POST.get('custom_category', '').strip()
        category = custom_category if custom_category else request.POST.get('category', '').strip()
        subcategory = request.POST.get('subcategory', '').strip()
        price_str = request.POST.get('price', '0').strip()
        desc = request.POST.get('desc', '').strip()
        pub_date = request.POST.get('pub_date', '').strip()
        preset_image = request.POST.get('preset_image', '').strip()

        try:
            price = int(float(price_str)) if price_str else 0
        except ValueError:
            price = 0

        if not pub_date:
            from django.utils import timezone
            pub_date = timezone.now().date()

        # Image Handling: uploaded file takes precedence, then preset_image, fallback to default
        image = request.FILES.get('image')
        if not image and preset_image:
            image = preset_image
        elif not image:
            image = "shop/images/Laptop.jpg"

        product = Product.objects.create(
            product_name=product_name if product_name else "Untitled Product",
            category=category if category else "General",
            subcategory=subcategory if subcategory else "Standard",
            price=price,
            desc=desc if desc else "Crafted with precision engineering and premium materials.",
            pub_date=pub_date,
            image=image
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"Product '{product.product_name}' created successfully!",
                'product_id': product.id
            })

        return redirect('/shop/admin-dashboard/?status=added')

    return redirect('/shop/admin-dashboard/')


def admin_edit_product(request, product_id):
    """
    Handle updating an existing inventory item
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_name = request.POST.get('product_name', '').strip()
        custom_category = request.POST.get('custom_category', '').strip()
        category = custom_category if custom_category else request.POST.get('category', '').strip()
        subcategory = request.POST.get('subcategory', '').strip()
        price_str = request.POST.get('price', '').strip()
        desc = request.POST.get('desc', '').strip()
        pub_date = request.POST.get('pub_date', '').strip()
        preset_image = request.POST.get('preset_image', '').strip()

        if product_name:
            product.product_name = product_name
        if category:
            product.category = category
        if subcategory:
            product.subcategory = subcategory
        if price_str:
            try:
                product.price = int(float(price_str))
            except ValueError:
                pass
        if desc:
            product.desc = desc
        if pub_date:
            product.pub_date = pub_date

        if 'image' in request.FILES:
            product.image = request.FILES['image']
        elif preset_image:
            product.image = preset_image

        product.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"Product '{product.product_name}' updated successfully!",
                'product_id': product.id
            })

        return redirect('/shop/admin-dashboard/?status=updated')

    # GET request returns product JSON for modal population
    return JsonResponse({
        'id': product.id,
        'product_name': product.product_name,
        'category': product.category,
        'subcategory': product.subcategory,
        'price': product.price,
        'desc': product.desc,
        'pub_date': str(product.pub_date),
        'image': str(product.image),
    })


def admin_delete_product(request, product_id):
    """
    Handle deleting an inventory item
    """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        name = product.product_name
        product.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"Product '{name}' removed from inventory.",
            })

        return redirect('/shop/admin-dashboard/?status=deleted')

    return redirect('/shop/admin-dashboard/')


def admin_quick_update(request):
    """
    Quick inline price or detail adjustments
    """
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        value = request.POST.get('value')

        product = get_object_or_404(Product, id=product_id)

        if action == 'price' and value is not None:
            try:
                product.price = max(0, int(float(value)))
                product.save()
                return JsonResponse({'success': True, 'new_price': product.price})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid price value'}, status=400)

        elif action == 'duplicate':
            # Create SKU clone
            new_prod = Product.objects.create(
                product_name=f"{product.product_name} (Copy)",
                category=product.category,
                subcategory=product.subcategory,
                price=product.price,
                desc=product.desc,
                pub_date=product.pub_date,
                image=product.image
            )
            return JsonResponse({'success': True, 'new_id': new_prod.id, 'message': 'Product duplicated'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)