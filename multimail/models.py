import hashlib
from random import random
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from multimail.settings import MM
from multimail.util import build_context_dict

USER_MODEL_STRING = settings.AUTH_USER_MODEL


class EmailAddress(models.Model):
    """An e-mail address for a Django User. Users may have more than one
    e-mail address. The address that is on the user object itself as the
    email property is considered to be the primary address, for which there
    should also be an EmailAddress object associated with the user.
    """
    user = models.ForeignKey(USER_MODEL_STRING, related_name='email_addresses', on_delete=models.CASCADE)
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verif_key = models.CharField(max_length=40)
    verified_at = models.DateTimeField(default=None, null=True, blank=True)
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    remote_host = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    def __unicode__(self):
        return self.email

    def is_verified(self):
        """Is this e-mail address verified? Verification is indicated by
        existence of a verified_at timestamp which is the time the user
        followed the e-mail verification link."""
        return bool(self.verified_at)

    def _set_primary_flags(self):
        """Set this email's is_primary to True and all others for this
        user to False."""
        for email in self.user.email_addresses.all():
            if email == self:
                if not email.is_primary:
                    email.is_primary = True
                    email.save()
            else:
                if email.is_primary:
                    email.is_primary = False
                    email.save()

    def set_primary(self):
        """Set this e-mail address to the primary address by setting the
        email property on the user."""
        self.user.email = self.email
        self.user.save()
        self._set_primary_flags()

    def save(self, verify=True, request=None, *args, **kwargs):
        """Save this EmailAddress object."""
        if not self.verif_key:
            salt = hashlib.sha1(str(random()).encode('utf-8')).hexdigest()[:5]
            self.verif_key = hashlib.sha1((salt + self.email).encode('utf-8')).hexdigest()
        if verify and not self.pk:
            verify = True
        else:
            verify = False
        super(EmailAddress,self).save(*args, **kwargs)
        if verify:
            self.send_verification(request=request)

    def delete(self):
        """Delete this EmailAddress object."""
        user = self.user
        super(EmailAddress, self).delete()
        addrs = user.email_addresses.all()
        if addrs:
            addrs[0].set_primary()
        else:
            if MM.DELETE_PRIMARY:
                user.email = ''
                user.save()


    def send_verification(self, request=None):
        """Send email verification link for this EmailAddress object.
        Raises smtplib.SMTPException, and NoRouteToHost.
        """
        html_template = get_template(MM.VERIFICATION_EMAIL_HTML_TEMPLATE)
        text_template = get_template(MM.VERIFICATION_EMAIL_TEXT_TEMPLATE)
        from multimail.util import get_site
        site = get_site(request)
        d = build_context_dict(site, self)
        if request:
            context = RequestContext(request, d)
        else:
            context = Context(d)
        msg = EmailMultiAlternatives(MM.VERIFICATION_EMAIL_SUBJECT % d,
            text_template.render(context),MM.FROM_EMAIL_ADDRESS,
            [self.email])
        msg.attach_alternative(html_template.render(context), 'text/html')
        msg.send(fail_silently=False)
        if MM.USE_MESSAGES:
            message = MM.VERIFICATION_LINK_SENT_MESSAGE % d
            if request is not None:
                messages.success(request, message,
                    fail_silently=not MM.USE_MESSAGES)
            else:
                try:
                    self.user.message_set.create(message=message)
                except AttributeError:
                    pass # user.message_set is deprecated and has been
                         # fully removed as of Django 1.4. Thus, display
                         # of this message without passing in a view is
                         # supported only in 1.3

    class InactiveAccount(Exception):
        """Raised when an account is required to be active.

        .. todo:: is InactiveAccount being used?
        """
        pass

    class AlreadyVerified(Exception):
        """Raised when a verfication request is made for an e-mail address
        that is already verified."""
        pass

    class Meta:
        app_label = 'multimail'
