from apps.products.models import Category, Item


def category_list(request):
    categories = Category.objects.exclude(parent_category__isnull=False)

    featured_list = Item.objects.all().order_by('-view_count')[:5]
    featured_image = []
    for item in featured_list:
        featured_image.append(item.image_item.filter(primary=True))
    featured_list.item_image = featured_image

    for parent in categories:
        parent.menu_bar_all = []
        parent.menu_bar = []
        parent.menu_bar_all.append(Category.objects.filter(parent_category=parent)[4:])
        parent.menu_bar.append(Category.objects.filter(parent_category=parent)[:4])
    return {
        'categories': categories,
        'featured_list': featured_list,
    }
