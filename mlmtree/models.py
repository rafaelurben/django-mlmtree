from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Create your models here.


class Tree(models.Model):
    "A tree"

    id = models.SlugField(
        verbose_name=_("Slug"),
        max_length=25,
        primary_key=True,
    )

    title = models.CharField(
        verbose_name=_("Titel"),
        max_length=50,
    )
    description = models.TextField(
        verbose_name=_("Beschreibung"),
    )

    top = models.ForeignKey(
        to='Person',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )

    urlpattern = models.URLField(
        verbose_name=_("URL-Vorlage"),
        blank=True,
        default='',
        help_text=_("Platzhalter: ${EMAIL}, ${USERID}"),
    )

    people: models.Manager

    def __str__(self):
        return f'{self.title} ({self.pk})'

    objects = models.Manager()

    def json(self):
        return {
            "id": self.pk,
            "title": self.title,
            "description": self.description,
            "top_id": getattr(self, "top_id"),
        }

    class Meta:
        verbose_name = _("Baum")
        verbose_name_plural = _("Bäume")


class Person(models.Model):
    "A person in a tree"

    tree = models.ForeignKey(
        to='Tree',
        verbose_name=_("Baum"),
        on_delete=models.CASCADE,
        related_name='people',
    )
    parent = models.ForeignKey(
        to='self',
        verbose_name=_("Sponsor"),
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
    )

    children: models.Manager

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=50,
    )
    email = models.EmailField(
        verbose_name=_("E-Mail"),
        blank=True,
        default='',
    )
    userid = models.CharField(
        verbose_name=_("Benutzeridentifikation"),
        max_length=255,
        blank=True,
        default='',
    )
    info = models.TextField(
        verbose_name=_("Info"),
        blank=True,
        default='',
    )

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_("Benutzer"),
        related_name='mlmtree_identities',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.name} ({self.pk})'

    objects = models.Manager()

    def relation_to_user(self, user: User) -> int:
        """Get the level difference from this person upwards to the next one the user is managing.
        Returns None if there's no one there."""

        current_person = self
        depth = 0
        while getattr(current_person, "user_id") != user.pk:
            depth += 1
            if getattr(current_person, "parent_id") is None:
                return None
            current_person = current_person.parent
        return depth

    def get_url(self, urlpattern: str) -> str:
        "Generatre a URL from the given pattern"

        if ("${EMAIL}" in urlpattern and self.email == "") or ("${USERID}" in urlpattern and self.userid == ""):
            return ""

        return urlpattern.replace("${EMAIL}", self.email).replace("${USERID}", self.userid)

    # Permissions

    def get_user_permissions(self, user: User):
        "Get the permissions for a specific user"

        relation = self.relation_to_user(user)
        has_children = self.children.exists()

        return {
            "view": True,
            "add": user.has_perm('mlmtree.add_person') or relation is not None,
            "change": user.has_perm('mlmtree.change_person') or relation is not None,
            "remove": (user.has_perm('mlmtree.remove_person') or (relation is not None and not has_children)) and self.parent_id is not None and self.user_id is None,
        }

    # Utils

    def json(self, urlpattern: str = "", loggedinuser: User = None, details: bool = True) -> dict:
        data = {
            "id": self.pk,
            "name": self.name,
            "userid": self.userid,
            "email": self.email,
            "info": self.info,

            "url": self.get_url(urlpattern),

            "has_user_connected": "own" if getattr(self, "user_id") == getattr(loggedinuser, "pk", "-") else getattr(self, "user_id") is not None,
            "childcount": self.get_child_count(),
        }

        if details:
            data["children"] = list(
                p.json(
                    urlpattern=urlpattern,
                    loggedinuser=loggedinuser,
                    details=False,
                ) for p in self.children.all())
            data["permissions"] = self.get_user_permissions(
                loggedinuser)

            if self.parent:
                data["parent"] = self.parent.json(
                    urlpattern=urlpattern,
                    loggedinuser=loggedinuser,
                    details=False,
                )
        return data

    def get_child_count(self):
        "Get the count of direct children"

        return Person.objects.filter(parent=self).count()

    def get_team_count(self):
        "Get the total team count"

        count = self.get_child_count()
        if count > 0:
            for child in self.children.all():
                count += child.get_team_count()
        return count

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Personen")
