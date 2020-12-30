from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from DungeonFinder.games.models import Campaign
from DungeonFinder.messaging.forms import MessageForm
from DungeonFinder.messaging.models import Message


@require_POST
@login_required
def create_message(request, pk):
    campaign = get_object_or_404(Campaign.objects.request_joined_qs(request), pk=pk)
    form = MessageForm(data=request.POST)
    form.full_clean()
    if form.is_valid():
        message = form.save(commit=False)
        message.campaign = campaign
        message.author = request.user
        message.save()
        return JsonResponse({'last_id': message.id})
    else:
        return JsonResponse(form.errors, status=400)


@require_POST
@login_required
def edit_message(request, pk):
    message = get_object_or_404(Message.objects.request_editable_qs(request), pk=pk)
    form = MessageForm(data=request.POST, instance=message)
    form.full_clean()
    if form.is_valid():
        form.save()
        return HttpResponse('OK')
    else:
        return HttpResponse(form.errors, status=400)


@require_POST
@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message.objects.request_editable_qs(request), pk=pk)
    message.delete()
    return HttpResponse('OK')


@login_required
def message_feed(request, pk):
    messages = Message.objects.request_qs(request).filter(campaign=pk)
    if last_id := request.GET.get('last_id', 0):
        messages = messages.filter(id__gt=last_id)
    data = []
    if messages.exists():
        data = [message.get_list_data() for message in messages.select_related('author')]
    return JsonResponse(data, safe=False)
