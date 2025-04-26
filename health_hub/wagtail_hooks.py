from wagtail.users.views.users import IndexView
from wagtail.users.forms import UserCreationForm, UserEditForm
from wagtail.users.models import UserProfile
from wagtail import hooks

@hooks.register('construct_user_queryset')
def custom_user_ordering(request, queryset):
    # Wagtail が last_name を使おうとするのを上書き
    return queryset.order_by('username')  # または 'email' でもOK
