import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect

from . import forms as product_forms, models as product_models


# Create your views here.


def view_product(request, product_id):
    item = product_models.Item.objects.get(pk=product_id)
    item.rating = item.product_feedback_to_product.aggregate(avg=Avg('item_rating'), count=Count('item_rating'))
    if item.user != request.user:
        item.view_count += 1
        item.save()
    try:
        primary_image = item.image_item.get(primary=True)
    except:
        primary_image = item.image_item.first()
    return render(request, 'view_product.html', {
        'item': item,
        'item_images': item.image_item.all(),
        'primary_image': primary_image
    })


def parent_categories(request, category_slug):
    parent_category = product_models.Category.objects.get(slug=category_slug, parent_category__isnull=True)
    child = product_models.Category.objects.filter(parent_category_id=parent_category.id)
    items = product_models.Item.objects.filter(categories__id__in=child.values_list('id')).distinct()
    return render(request, 'category_list.html', {
        'items': items
    })


def child_categories(request, category_slug, subcategory_slug):
    child_category = product_models.Category.objects.filter(slug=subcategory_slug, parent_category__isnull=False)
    items = product_models.Item.objects.filter(categories=child_category)
    return render(request, 'category_list.html', {
        'items': items
    })


# USER PRODUCTS
@login_required
def add_product(request):
    if request.POST and request.user.is_authenticated:
        product_form = product_forms.AddProductForm(request.POST)
        if product_form.is_valid():
            form = product_form.save(commit=False)
            # NOTE: VARIABLES FROM FORM, SHOULD MAKE ANOTHER VARIABLES JUST FOR THE SAVE
            # THIS IS VERY IMPORTANT!!
            form.user = request.user
            form.save()
            return redirect('image_upload', product_id=form.id)
    elif request.user.profile.approved_as_seller:
        product_form = product_forms.AddProductForm(instance=request.user)
    else:
        return redirect('register_as_seller')
    return render(request, 'user/add_products.html', {
        'product_form': product_form
    })


@login_required
def update_product(request, product_id):
    product = product_models.Item.objects.get(pk=product_id)
    if request.POST and request.user == product.user:
        product_form = product_forms.EditProductForm(request.POST, instance=product)
        if product_form.is_valid():
            form = product_form.save(commit=False)
            # NOTE: VARIABLES FROM FORM, SHOULD MAKE ANOTHER VARIABLES JUST FOR THE SAVE
            # THIS IS VERY IMPORTANT!!
            form.user = request.user
            form.save()
            return redirect('image_upload', product_id=form.id)
    elif request.user == product.user:
        product_form = product_forms.EditProductForm(instance=product)
    else:
        return redirect('register_as_seller')

    return render(request, 'user/update_product.html', {
        'product_id': product_id,
        'product_form': product_form,
    })


@login_required
def image_upload(request, product_id):
    item = product_models.Item.objects.get(id=product_id)
    try:
        item_image = product_models.ItemImage.objects.filter(item=item)
        item_image_len = item_image.count()
    except:
        pass
    if request.POST and request.user.is_authenticated and request.user.profile.approved_as_seller and item_image_len < 8:
        image_form = product_forms.ImageForm(request.POST, request.FILES)
        if image_form.is_valid() and request.user == item.user:
            form = image_form.save(commit=False)
            form.item = item
            form.save()
            data = {
                'is_valid': True,
                'updated_at': datetime.datetime.now().strftime('%B %d, %Y, %I:%M:%S %p'),
                'url': '/' + form.image.url,
                'image_id': form.id,
                'total_image_num': item_image_len
            }
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    elif request.POST and request.user.is_authenticated and request.user.profile.approved_as_seller and item_image_len >= 8:
        return JsonResponse({'is_valid': False, 'total_image_num': item_image_len})
    return render(request, 'user/image_upload.html', {
        'item': item,
        'item_image': item_image
    })


@login_required
def image_delete(request, image_id):
    if request.POST and request.user.is_authenticated and request.user.profile.approved_as_seller:
        product_models.ItemImage.objects.get(pk=image_id).delete()
        data = {'success': True}
        return JsonResponse(data)


@login_required
def image_set_primary(request, image_id):
    if request.POST and request.user.is_authenticated and request.user.profile.approved_as_seller:
        this_image = product_models.ItemImage.objects.get(pk=image_id)
        other_images = product_models.ItemImage.objects.filter(item=this_image.item).exclude(pk=image_id)
        for image in other_images:
            image.primary = False
            image.save(update_fields=['primary'])
        this_image.primary = True
        this_image.save(update_fields=['primary'])
        data = {'success': True}
        return JsonResponse(data)


@login_required
def list_product(request):
    product_list = request.user.product.all()
    paginator = Paginator(product_list, 5)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    itemImage = []
    for item in products:
        primary_photo = item.image_item.filter(primary=True)
        if primary_photo:
            itemImage.append(primary_photo)
        else:
            itemImage.append(item.image_item.all())

    products.item_image = itemImage
    if not request.user.company.name and request.user.profile.approved_as_seller:  # DISABLED FOR DEVELOPMENT
        return redirect('user_company')
    elif not request.user.profile.approved_as_seller:
        return redirect('register_as_seller')
    else:
        return render(request, 'user/list_products.html', {
            'product_list': products
        })


@login_required
def delete_product(request, product_id):
    product = product_models.Item.objects.get(pk=product_id).delete()
    if request.POST and request.user.is_authenticated and request.user.profile.approved_as_seller:
        product.save()

    return redirect('list_product')


@login_required
def post_product_feedback(request, product_id):
    product = product_models.Item.objects.get(id=product_id)
    if request.POST and request.user.is_authenticated:
        feedbackForm = product_forms.FeedBackForm(request.POST)
        feedbackForm.save(commit=False)
        feedbackForm.from_user = request.user
        feedbackForm.to_item = product
        feedbackForm.save()
        data = {
            'rating': product.product_feedback_to_product.aggregate(avg=Avg('item_rating'), count=Count('item_rating'))
        }
    else:
        data = 'Not Authorized'
    return JsonResponse(data)
