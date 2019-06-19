from django.core.files.base import ContentFile
from requests import request, HTTPError
from social.exceptions import AuthException, AuthAlreadyAssociated


def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            msg = 'This {0} account is already in use.'.format(provider)
            raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'new_association': False}


def complete_login(backend, user, response, details, is_new=False, *args, **kwargs):
    if not user:
        raise AuthException(backend, "The user doesn't exist")

    if is_new and backend.name == "facebook":
        url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
        try:
            response = request('GET', url, params={'type': 'large'})
            response.raise_for_status()
        except HTTPError:
            pass
        user.photo.save(u'{}.jpg'.format(user.uid), ContentFile(response.content))
        user.save(update_fields=["photo"])
