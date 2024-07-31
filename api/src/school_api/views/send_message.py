import logging

from school_api.models import TestSessionSchool
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from school_api.forms import MessageForm
import requests


def send_message(request):
    user_fullname = 'User Fullname'
    user_id: str = request.GET.get('user_id')
    if not user_id.isdigit():
        messages.error(request, 'Invalid user id')
        return redirect(reverse('admin:school_api_testsessionschool_changelist'))
    context = {'user_id': request.GET.get('user_id'),
               'fullname': user_fullname}
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['text']
            user_id = form.cleaned_data['user_id']
            log_message = f'Sending message to user {user_id} with message: {message}'
            logging.info(log_message)
            url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={user_id}&text={message}'
            try:
                response = requests.get(url)
                response.raise_for_status()
                messages.success(request, 'Your message was sent successfully!')

            except Exception as e:
                logging.error(f'Failed to send the message to user {user_id}: {e}')
                messages.error(request, 'Something went wrong! %s' % e)

            return redirect(reverse('admin:school_api_testsessionschool_changelist'))

    return render(request, 'school_api/send_message.html', context=context)
