from account.models import Notification, Favourite_products
from cart.models import Cart
from shopApp.models import Comment
from utils import get_cart_info


def user_data(request):
    """
    Context processor to provide common user data for templates.
    This eliminates the need to duplicate this code in multiple views.
    """
    if not request.user.is_authenticated:
        return {}
        
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications_count = notifications.filter(is_read=False).count()
    
    # Get user's comments
    comments = Comment.objects.filter(user=request.user)
    comments_count = len(comments)
    
    # Get user's cart information
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    cart_info = get_cart_info(cart)
    
    # Get all carts for the user
    carts = Cart.objects.filter(user=request.user)
    all_carts_count = len(carts)
    
    # Count user's favorite products
    fav_products = Favourite_products.objects.filter(user=request.user)
    favourite_products_count = fav_products.count()
    
    # برای اشکال‌زدایی، مقادیر را چاپ کنیم
    print(f"User: {request.user.username}, Favorites query: {fav_products}, Count: {favourite_products_count}")
    
    # Categorize carts by status
    carts_pending = []
    carts_confirmed = []
    carts_shipped = []
    carts_delivered = []
    carts_canceled = []
    
    for cart_item in carts:
        if cart_item.status == "pending":
            carts_pending.append(cart_item)
        elif cart_item.status == "confirmed":
            carts_confirmed.append(cart_item)
        elif cart_item.status == "shipped":
            carts_shipped.append(cart_item)
        elif cart_item.status == "delivered":
            carts_delivered.append(cart_item)
        elif cart_item.status == "canceled":
            carts_canceled.append(cart_item)
    
    return {
        # User basic information
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        
        # Notifications
        'notifications': notifications,
        'notifications_count': notifications_count,
        
        # Comments
        'comments': comments,
        'comments_count': comments_count,
        
        # Cart information
        'cart_items': cart_info['cart_items'],
        'cart_count': sum(item.count for item in cart_info['cart_items']),
        'cart_total': cart_info['cart_total'],
        
        # All carts and their status counts
        'carts': carts,
        'all_carts_count': all_carts_count,
        'carts_pending': carts_pending,
        'carts_confirmed': carts_confirmed,
        'carts_shipped': carts_shipped,
        'carts_delivered': carts_delivered,
        'carts_canceled': carts_canceled,
        'carts_pending_count': len(carts_pending),
        'carts_confirmed_count': len(carts_confirmed),
        'carts_shipped_count': len(carts_shipped),
        'carts_delivered_count': len(carts_delivered),
        'carts_canceled_count': len(carts_canceled),
        
        # Favorites
        'favourite_products_count': favourite_products_count,
    } 