from django.shortcuts import render
from .models import Shop, Dish, Orders, Comments, DishPreference
from customer.models import Customer
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q


# Create your views here.


def show_dish(request):
    template_name = 'dish/dish_list.html'
    
    # 获取所有窗口
    shop_with_dish_list = Shop.objects.all()
    
    # 获取筛选参数
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    taste = request.GET.get('taste')
    is_spicy = request.GET.get('is_spicy')
    sort_by = request.GET.get('sort_by', 'dish_id')  # 默认按ID排序
    shop_id = request.GET.get('shop_id')  # 新增：获取窗口ID
    
    # 基础查询
    dish_list = Dish.objects.all()
    dish_list = dish_list.order_by('?')
    # 应用筛选条件
    if shop_id:  # 新增：按窗口筛选
        dish_list = dish_list.filter(shop_id=shop_id)
    if min_price:
        dish_list = dish_list.filter(dish_price__gte=float(min_price))
    if max_price:
        dish_list = dish_list.filter(dish_price__lte=float(max_price))
    if taste:
        dish_list = dish_list.filter(taste=taste)
    if is_spicy:
        dish_list = dish_list.filter(is_spicy=is_spicy == 'true')
    # if sort_by == 'random':  # 添加随机排序选项
        
        
    # 排序
    if sort_by == 'price_asc':
        dish_list = dish_list.order_by('dish_price')
    elif sort_by == 'price_desc':
        dish_list = dish_list.order_by('-dish_price')
    elif sort_by == 'calories_asc':
        dish_list = dish_list.order_by('calories')
    elif sort_by == 'calories_desc':
        dish_list = dish_list.order_by('-calories')
    
    # 获取用户的收藏和拉黑列表
    favorite_dishes = []
    blocked_dishes = []
    
    if request.session.get('is_login', None):
        user = Customer.objects.get(customer_id=request.session['user_id'])
        preferences = DishPreference.objects.filter(customer=user)
        
        favorite_dishes = [p.dish.dish_id for p in preferences if p.preference_type == 'favorite']
        blocked_dishes = [p.dish.dish_id for p in preferences if p.preference_type == 'blocked']
    
    context = {
        'shop_with_dish_list': shop_with_dish_list,
        'dish_list': dish_list,
        'favorite_dishes': favorite_dishes,
        'blocked_dishes': blocked_dishes,
        'taste_choices': Dish.taste_choices,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'taste': taste,
            'is_spicy': is_spicy,
            'sort_by': sort_by,
            'shop_id': shop_id,  # 新增：将当前选中的窗口ID添加到上下文中
        }
    }

    return render(request, template_name, context)


def show_order(request):
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户~")
        return redirect('/customer/login/')

    template_name = 'dish/my_order.html'

    user_id = request.session['user_id']

    context = {
        'order_list': Orders.objects.filter(customer_id=user_id),
    }
    return render(request, template_name, context)


def get_order(request, dish_id):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    user_id = request.session['user_id']

    try:
        user = Customer.objects.filter(customer_id=user_id).first()
        order = Orders.objects.create(dish=dish, customer=user)
        order.order_price = order.dish.dish_price
        order.order_status = 0
        order.save()
        messages.success(request, '下单成功，订单号为 (Order ID-{}). 请支付 {} 元'.format(order.order_id, order.order_price))
        return redirect("dish:show_order")

    except ObjectDoesNotExist:
        messages.warning(request, "你还没有订单哦~")
        return redirect("dish:show_order")


def dish_comments(request, dish_id):
    """View to display comments for a specific dish and allow users to add comments"""
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户~")
        return redirect('/customer/login/')
    
    dish = get_object_or_404(Dish, dish_id=dish_id)
    user_id = request.session['user_id']
    
    # Get all comments for this dish
    dish_orders = Orders.objects.filter(dish=dish)
    comments = Comments.objects.filter(order__in=dish_orders).order_by('-comment_time')
    
    # Get user's orders for this dish that they can comment on
    user_orders = Orders.objects.filter(dish=dish, customer_id=user_id)
    
    context = {
        'dish': dish,
        'comments': comments,
        'user_orders': user_orders,
    }
    
    return render(request, 'dish/dish_comment.html', context)


def add_comment(request, dish_id):
    """View to handle comment submission"""
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户~")
        return redirect('/customer/login/')
    
    if request.method == 'POST':
        dish = get_object_or_404(Dish, dish_id=dish_id)
        user_id = request.session['user_id']
        
        # Get form data
        order_id = request.POST.get('order_id')
        rating = request.POST.get('rating')
        comment_text = request.POST.get('comment')
        
        try:
            # Verify the order belongs to the user
            order = Orders.objects.get(order_id=order_id, customer_id=user_id, dish=dish)
            
            # Create the comment
            comment = Comments.objects.create(
                order=order,
                comment_score=rating,
                comment_detail=comment_text
            )
            
            # Update order status to reviewed
            order.order_status = 3  # 已评价
            order.save()
            
            messages.success(request, "评论发表成功！感谢您的反馈。")
        except Orders.DoesNotExist:
            messages.error(request, "无效的订单，请确认您已购买该菜品。")
        except Exception as e:
            messages.error(request, f"添加评论时出错: {str(e)}")
    
    return redirect('dish:dish_comments', dish_id=dish_id)


@require_POST
def toggle_preference(request, dish_id, preference_type):
    """处理收藏/拉黑菜品的请求"""
    print(f"[DEBUG] 收到请求: dish_id={dish_id}, preference_type={preference_type}")
    print(f"[DEBUG] 请求方法: {request.method}")
    print(f"[DEBUG] 请求头: {request.headers}")
    
    if not request.session.get('is_login', None):
        print("[DEBUG] 用户未登录")
        return JsonResponse({'status': 'error', 'message': '请先登录'})
    
    if preference_type not in ['favorite', 'blocked']:
        print(f"[DEBUG] 无效的偏好类型: {preference_type}")
        return JsonResponse({'status': 'error', 'message': '无效的偏好类型'})
    
    try:
        dish = get_object_or_404(Dish, dish_id=dish_id)
        user = Customer.objects.get(customer_id=request.session['user_id'])
        print(f"[DEBUG] 用户: {user.customer_name}, 菜品: {dish.dish_name}")
        
        # 检查是否已经存在该偏好
        preference = DishPreference.objects.filter(
            customer=user,
            dish=dish,
            preference_type=preference_type
        ).first()
        
        if preference:
            # 如果存在，则删除（取消收藏/拉黑）
            preference.delete()
            action = 'removed'
            print(f"[DEBUG] 删除偏好: {preference_type}")
        else:
            # 如果不存在，则创建（添加收藏/拉黑）
            DishPreference.objects.create(
                customer=user,
                dish=dish,
                preference_type=preference_type
            )
            action = 'added'
            print(f"[DEBUG] 添加偏好: {preference_type}")
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'message': f'成功{"取消" if action == "removed" else ""}{"收藏" if preference_type == "favorite" else "拉黑"}'
        })
        
    except Exception as e:
        print(f"[DEBUG] 发生错误: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'操作失败：{str(e)}'
        })

def show_preferences(request, preference_type):
    """显示用户的收藏或拉黑列表"""
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户~")
        return redirect('/customer/login/')
    
    if preference_type not in ['favorite', 'blocked']:
        messages.error(request, "无效的偏好类型")
        return redirect('dish:show_dish')
    
    user = Customer.objects.get(customer_id=request.session['user_id'])
    preferences = DishPreference.objects.filter(
        customer=user,
        preference_type=preference_type
    ).select_related('dish', 'dish__shop')
    
    title = "我的收藏" if preference_type == 'favorite' else "拉黑列表"
    
    context = {
        'preferences': preferences,
        'title': title,
        'preference_type': preference_type
    }
    
    return render(request, 'dish/preference_list.html', context)
