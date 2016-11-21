from __future__ import division, print_function, unicode_literals

import vanilla

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render

from .models import Photo, PhotoExifItem


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "Just an empty landing page."}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'index.html', context=context_dict)


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('photo-list'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

        # The request is not a HTTP POST, so display the login form.
        # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', {})

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))


class PhotoMixin(object):
    """
    Add user to the context
    """
    def get_context_data(self, *args, **kwargs):
        context = super(PhotoMixin, self).get_context_data(*args, **kwargs)

        if hasattr(self, "request") and self.request.user and self.request.user.is_authenticated():
            context.update({
                'username': self.request.user.username,
            })
        return context

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        else:
            return super(PhotoMixin, self).dispatch(request, *args, **kwargs)


class PhotoListView(PhotoMixin, vanilla.ListView):
    model = Photo
    template_name = 'waldo/photo/list_photo.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PhotoListView, self).get_context_data(*args, **kwargs)
        context.update({
            'photos': self.get_queryset(),
        })
        return context

