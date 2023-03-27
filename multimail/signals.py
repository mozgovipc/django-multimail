from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.db.models.signals import post_save
from django.utils import timezone as now
from multimail.settings import MM
from multimail.models import EmailAddress

### HANDLERS ###

def email_address_handler(sender, **kwargs):
    """Ensures that there is a multimail version of the email address on the
    django user object and that email is set to primary."""
    user = kwargs['instance']
    if not user.email:
        return
    if kwargs.get('raw', False): # don't create email entry when
                                 # loading fixtures etc.
        return
    try:
        if MM.SEND_EMAIL_ON_USER_SAVE_SIGNAL:
            if user.email:
                addr = EmailAddress.objects.filter(user=user,
                    email__iexact=user.email)
                if addr:
                    addr = addr[0]
                else:
                    addr = EmailAddress(user=user, email=user.email) 
                    addr.save()
        else:
            try:
                addr = EmailAddress.objects.get(user=user,email=user.email)
                # Provides that an address that has been just verified
                # without use of django-multimail, is still considered
                # verified in conditions of django-multimail
                if MM.AUTOVERIFY_ACTIVE_ACCOUNTS and \
                   user.is_active and not addr.verified_at:
                    addr.verified_at = now()
            except EmailAddress.DoesNotExist:
                addr = EmailAddress()
                addr.user = user
                addr.email = user.email
            addr.save(verify=False)
        addr._set_primary_flags() # do this for every save in case things
                                  # get out of sync
    except Exception:
        msg = """An attempt to create EmailAddress object for user %s, email
%s has failed. This may indicate that an EmailAddress object for that email
already exists in the database. This situation can occur if, for example, a
user is manually created through the admin panel or the shell with an email
address that is the same as an existing EmailAddress objects.""" % (
user.username, user.email)
        subj = "Failed attempt to create Multimail email address."
        if MM.EMAIL_ADMINS:
            mail_admins(subj, msg)


def user_deactivation_handler(sender, **kwargs):
    """Ensures that an administratively deactivated user does not have any
    lingering unverified email addresses."""
    created = kwargs['created']
    user = kwargs['instance']
    if not created and not user.is_active:
        for email in user.email_addresses.all():
            if not email.is_verified():
                email.delete()


def setup_signals(user_model):
    post_save.connect(email_address_handler, sender=user_model)
    if MM.USER_DEACTIVATION_HANDLER_ON:
        post_save.connect(user_deactivation_handler, sender=user_model)

setup_signals(get_user_model())
