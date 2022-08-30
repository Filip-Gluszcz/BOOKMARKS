from actions.utils import create_action
from common.decorators import ajax_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import ImageCreateForm
from .models import Image
import redis

rds = redis.StrictRedis(host=settings.REDIS_HOST, 
                        port=settings.REDIS_PORT, 
                        db=settings.REDIS_DB)

@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)

        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 
                         'dodał obraz', 
                          new_image)
            messages.success(request, 'Obraz został dodany')
            return redirect(new_image.get_absolute_url())
    
    else: form = ImageCreateForm(data=request.GET)

    return render(request, 
                 'images/image/create.html', 
                {'form': form, 
                 'section': 'images'})


@login_required
def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = rds.incr(f'image:{image.id}:views')
    rds.zincrby('image_ranking', 1, image.id)
    return render(request, 
                 'images/image/detail.html', 
                {'section': 'images', 
                 'image': image,
                 'total_views': total_views})



@login_required
def image_ranking(request):
    image_ranking = rds.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                  'most_viewed': most_viewed})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like': 
                image.users_like.add(request.user)
                create_action(request.user, 'polubił', image)
            else: image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass

    return JsonResponse({'status': 'ok'})


@login_required
def image_list(request):
    images_list = Image.objects.all()
    paginator = Paginator(images_list, 8)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger: images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax(): return HttpResponse('')
        images = paginator(paginator.num_pages)
        
    if request.is_ajax(): return render(request, 
                                       'images/image/list_ajax.html', 
                                      {'section': 'images', 
                                       'images': images})

    return render(request, 
                 'images/image/list.html', 
                {'section': 'images', 
                 'images': images})


