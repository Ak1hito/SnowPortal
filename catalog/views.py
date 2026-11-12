from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Snowboard, Category, Resort, UserProfile
from .forms import RegisterForm, ProfileForm
import requests
from django.core.cache import cache
from django.http import JsonResponse
from .models import Favorite
from django.shortcuts import render, redirect, get_object_or_404


def weather_api(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    if not lat or not lon:
        return JsonResponse({'error': 'no coords'}, status=400)
    weather = get_weather(lat, lon)
    if weather:
        return JsonResponse(weather)
    return JsonResponse({'error': 'unavailable'}, status=503)


def get_weather(lat, lon):
    cache_key = f'weather_{lat}_{lon}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric&lang=ru'
        response = requests.get(url, timeout=5)
        data = response.json()
        result = {
            'temp': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'wind': round(data['wind']['speed']),
            'icon': data['weather'][0]['icon'],
        }
        cache.set(cache_key, result, 60 * 30)
        return result
    except:
        return None


def index(request):
    return render(request, 'catalog/index.html')


def resorts(request):
    all_resorts = Resort.objects.select_related('country').all()
    resorts_data = [{'resort': resort, 'weather': None} for resort in all_resorts]
    return render(request, 'catalog/resorts.html', {'resorts_data': resorts_data})


def selector(request):
    results = []
    form_data = {}
    categories = Category.objects.all()
    snowboards = Snowboard.objects.select_related('brand').prefetch_related('categories').all()

    # Данные профиля, если пользователь залогинен
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            pass

    # Параметры из GET или из профиля
    weight = request.GET.get('weight')
    height = request.GET.get('height')
    style_param = request.GET.get('style')   # может быть строка "freeride,park" или None
    flex_values = request.GET.get('flex', '').split(',') if request.GET.get('flex') else []
    stiffness_pref = request.GET.get('stiffness')

    # Заполняем из профиля, если в GET не указано
    if not weight and profile and profile.weight:
        weight = str(profile.weight)
    if not height and profile and profile.height:
        height = str(profile.height)

    # Разбираем стиль в список slug-ов
    style_slugs = style_param.split(',') if style_param else []

    weight = int(weight) if weight else None
    height = int(height) if height else None
    stiffness_pref = int(stiffness_pref) if stiffness_pref else None

    # Фильтрация по стилю и прогибу (до расчёта совместимости)
    if style_slugs:
        snowboards = snowboards.filter(categories__slug__in=style_slugs).distinct()
    if flex_values:
        snowboards = snowboards.filter(flex__in=flex_values)

    form_data = {
        'weight': weight,
        'height': height,
        'styles': style_slugs,
        'flexes': flex_values,
        'stiffness': stiffness_pref,
    }

    # Если вес задан — включаем расчёт совместимости
    if weight is not None:
        for board in snowboards:
            scores = {'weight': 0, 'height': 0, 'style': 0, 'stiffness': 0}

            # --- Вес (40 баллов) ---
            min_w = float(board.min_weight)
            max_w = float(board.max_weight)
            mid_w = (min_w + max_w) / 2
            range_w = max_w - min_w

            if min_w <= weight <= max_w:
                distance_from_mid = abs(weight - mid_w)
                if range_w > 0:
                    fit = 1 - (distance_from_mid / (range_w / 2))
                else:
                    fit = 1
                scores['weight'] = int(20 + fit * 20)
            elif weight < min_w:
                diff = min_w - weight
                scores['weight'] = max(0, 15 - int(diff * 3))
            else:
                diff = weight - max_w
                scores['weight'] = max(0, 15 - int(diff * 3))

            # --- Рост (30 баллов) ---
            if height:
                primary_style = style_slugs[0] if style_slugs else 'all-mountain'
                style_coeff = {
                    'park': 0.85,
                    'freestyle': 0.87,
                    'all-mountain': 0.88,
                    'freeride': 0.92,
                    'powder': 0.95,
                }.get(primary_style, 0.88)

                recommended_length = height * style_coeff
                diff = abs(board.length - recommended_length)
                if diff <= 2:
                    scores['height'] = 30
                elif diff <= 5:
                    scores['height'] = 25
                elif diff <= 10:
                    scores['height'] = 18
                elif diff <= 15:
                    scores['height'] = 10
                elif diff <= 20:
                    scores['height'] = 5
                else:
                    scores['height'] = 0
            else:
                scores['height'] = 15

            # --- Стиль (20 баллов) ---
            board_slugs = [cat.slug for cat in board.categories.all()]
            if style_slugs:
                matches = sum(1 for s in style_slugs if s in board_slugs)
                if matches == len(style_slugs):
                    scores['style'] = 20
                elif matches > 0:
                    scores['style'] = int(20 * matches / len(style_slugs))
                else:
                    if 'all-mountain' in board_slugs:
                        scores['style'] = 5
                    else:
                        scores['style'] = 0
            else:
                scores['style'] = 10

            # --- Жёсткость (10 баллов) ---
            if stiffness_pref and board.stiffness:
                diff = abs(board.stiffness - stiffness_pref)
                if diff == 0:
                    scores['stiffness'] = 10
                elif diff == 1:
                    scores['stiffness'] = 8
                elif diff == 2:
                    scores['stiffness'] = 5
                elif diff == 3:
                    scores['stiffness'] = 2
                else:
                    scores['stiffness'] = 0
            else:
                scores['stiffness'] = 5

            total_score = sum(scores.values())
            results.append({
                'board': board,
                'score': total_score,
                'score_components': scores,
            })

        results.sort(key=lambda x: x['score'], reverse=True)
    else:
        # Без веса — просто список досок
        results = [{'board': board} for board in snowboards]
    
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('snowboard_id', flat=True)

    context = {
        'results': results,
        'form_data': form_data,
        'categories': categories,
        'favorite_ids': favorite_ids,   # <-- вот это
    }
    return render(request, 'catalog/selector.html', {
        'results': results,
        'form_data': form_data,
        'categories': categories,
    })


# ---------- АВТОРИЗАЦИЯ И ПРОФИЛЬ ----------

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'catalog/register.html', {'form': form})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'catalog/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'catalog/profile_edit.html', {'form': form})

@login_required
def toggle_favorite(request, snowboard_id):
    board = get_object_or_404(Snowboard, pk=snowboard_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, snowboard=board)
    if not created:
        fav.delete()
        status = 'removed'
    else:
        status = 'added'
    return JsonResponse({'status': status})

@login_required
def favorites(request):
    favs = Favorite.objects.filter(user=request.user).select_related('snowboard__brand')
    return render(request, 'catalog/favorites.html', {'favorites': favs})