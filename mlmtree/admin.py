from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Tree, Person

# Register your models here.

# Tree admin


class TreeAdminPeopleInline(admin.TabularInline):
    model = Person
    extra = 0

    fields = ('name', 'userid', 'email', 'info', 'parent', 'user',)
    autocomplete_fields = ('parent', 'user',)


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'urlpattern')
    autocomplete_fields = ('top',)
    ordering = ('title', 'pk', )

    inlines = (TreeAdminPeopleInline,)

    def get_fields(self, request, obj=None):
        return ('id', 'title', 'description', 'urlpattern') if obj is None else ('id', 'title', 'description', 'urlpattern', 'top',)

    def get_readonly_fields(self, request, obj=None):
        return ('id',) if obj is not None else ()

# Person admin

class PersonAdminChildrenInline(admin.TabularInline):
    model = Person
    extra = 0
    fk_name = 'parent'
    verbose_name = "Kind"
    verbose_name_plural = "Kinder"

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'userid', 'email', 'info', 'tree', 'parent', 'user',)
    list_filter = ('tree',)
    search_fields = ('name', 'userid', 'email', 'info',)

    ordering = ('name', 'pk', )

    inlines = [PersonAdminChildrenInline]

    fieldsets = [
        (_("Positionierung"), {
            'fields': ('tree', 'parent'),
        }),
        (_("Daten"), {
            'fields': ('name', 'userid', 'email', 'info',),
        }),
        (_("Verknüpfung"), {
            'fields': ('user',),
        })
    ]
    readonly_fields = ('tree',)

    def has_add_permission(self, request):
        return False
