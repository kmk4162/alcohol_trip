from django.shortcuts import render, redirect
from .forms import ReviewForm, CommentForm
from .models import Restaurant, Review, Comment, Search
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.db.models import Q, Count
from django.core.paginator import Paginator  

# limit to 8 cards
def index(request):
    restaurants = Restaurant.objects.all().order_by("-like_count")[:8]
    search = Search.objects.all().order_by("-count")[:5]
    context = {
        "restaurants": restaurants,
        "search": search,
    }
    return render(request, "bars/index.html", context)


def detail(request, restaurant_pk):
    restaurant = Restaurant.objects.get(pk=restaurant_pk)
    reviews = Review.objects.filter(restaurant_id=restaurant_pk)
    comment_form = CommentForm
    print(restaurant.hours)
    context = {
        "restaurant_hours": restaurant.hours,
        "restaurant": restaurant,
        "reviews": reviews,
        "comment_form": comment_form,
    }
    return render(request, "bars/detail.html", context)


@login_required
def review(request, pk):
    if request.method == "POST":
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.restaurant_id = pk
            review.save()
            return redirect("bars:detail", pk)
    else:
        review_form = ReviewForm()
    context = {
        "review_form": review_form,
    }
    return render(request, "bars/review.html", context)
    

def update(request, restaurant_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.restaurant_id = restaurant_pk
            review.save()
            return redirect("bars:detail", restaurant_pk)
    else:
        review_form = ReviewForm(instance=review)
    context = {
        "review_form": review_form,
    }
    return render(request, "bars/update.html", context)


def delete(request, restaurant_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user == review.user:
        review.delete()
        return redirect("bars:detail", restaurant_pk)
    # else:
    #     return HttpResponseForbidden


def comment_create(request, restaurant_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.review = review
        comment.user = request.user
        comment.save()
    # print(comment.review)
    # print(review_pk)
    return redirect("bars:detail", restaurant_pk)


def comment_delete(request, restaurant_pk, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    comment.delete()
    return redirect("bars:detail", restaurant_pk)

@login_required
def restaurant_like(request, pk):
    restaurant = Restaurant.objects.get(pk=pk)
    if restaurant.like_users.filter(pk=request.user.pk).exists():
        restaurant.like_users.remove(request.user)
        is_liked = False
    else:
        restaurant.like_users.add(request.user)
        is_liked = True
    likeCount = restaurant.like_users.count()
    restaurant.like_count = likeCount
    restaurant.save()
    context = {
        'isLiked' : is_liked,
        'likeCount' : restaurant.like_users.count(),
    }
    return JsonResponse(context)


def review_like(request, restaurant_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user in review.like_usersreview.all():
        review.like_usersreview.remove(request.user)
        is_liked = False
    else:
        review.like_usersreview.add(request.user)
        is_liked = True
    likeReviewCount = review.like_usersreview.count()
    review.like_usersreview.count = likeReviewCount
    review.save()
    context = {
        'isLiked' : is_liked,
        'likeReviewCount' : review.like_usersreview.count(),
    }
    return JsonResponse(context)

def search(request):
    searched = request.GET.get('searched')
    if not searched=="":
        if Search.objects.filter(keyword=searched).exists():
            search = Search.objects.get(keyword=searched)
            search.count += 1
            search.save()
        else:
            Search.objects.create(keyword=searched, count=1)
    restaurants = Restaurant.objects.filter(
        Q(name__contains=searched)|
        Q(category__contains=searched)|
        Q(address__contains=searched)
        ).distinct().order_by('-name')
    restaurants_count = restaurants.count()
    # ?????? ????????????
    page = request.GET.get("page", "1")
    # ?????????
    paginator = Paginator(restaurants, 16)
    page_obj = paginator.get_page(page)
    context = {
        "searched": searched,
        "restaurants_count": restaurants_count,
        "restaurants": page_obj,
    }
    return render(request, 'bars/search.html', context)

def category(request, category):
    category_table = {
        "beer": "??????,??????",
        "izakaya": "????????????",
        "pojangmacha": "????????????",
        "restaurant": "????????????",
        "bar": "???(BAR)",
    }
    k_category = category_table.get(category)
    restaurants = Restaurant.objects.filter(category=k_category)
    # ?????? ????????????
    page = request.GET.get("page", "1")
    # ?????????
    paginator = Paginator(restaurants, 8)
    page_obj = paginator.get_page(page)
    print(restaurants)
    context = {
        "k_category": k_category,
        "restaurants": restaurants,
        "restaurants": page_obj,
    }
    return render(request, "bars/category.html", context)

def region(request, region):
    region_table = {
        "seoul": "??????",
        "gyeonggi": "??????",
        "incheon": "??????",
        "chungbuk": "??????",
        "chungnam": "??????",
        "jeonnam": "??????",
        "jeonbuk": "??????",
        "gangwon": "??????",
        "gyeongnam": "??????",
        "gyeongbuk": "??????",
        "jeju": "??????",
    }
    k_region = region_table.get(region)
    restaurants = Restaurant.objects.filter(address__contains=k_region)
    # ?????? ????????????
    page = request.GET.get("page", "1")
    # ?????????
    paginator = Paginator(restaurants, 8)
    page_obj = paginator.get_page(page)
    context = {
        "k_region": k_region,
        "restaurants": restaurants,
        "restaurants": page_obj,
    }
    return render(request, 'bars/region.html', context)