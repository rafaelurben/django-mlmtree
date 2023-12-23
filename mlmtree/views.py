from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from .models import Tree, Person
from .decorators import require_object, require_objects

# Create your views here.


@login_required(login_url=reverse_lazy('mlmtree:login'))
def home(request):
    trees = {}

    # Get trees that are visible for the current user
    for identity in request.user.mlmtree_identities.select_related('tree').all():
        if identity.tree_id in trees:
            trees[identity.tree_id]["identities"].append(identity)
        else:
            trees[identity.tree_id] = {
                "tree": identity.tree, "identities": [identity]}

    # Display all trees for admins
    if request.user.is_superuser:
        for tree in Tree.objects.all():
            if tree.pk not in trees:
                trees[tree.pk] = {"tree": tree, "identities": []}

    return render(request, 'mlmtree/app/home.html', {
        "entries": trees.values(),
        "headertitle": "MLMTree | Home",
        "headerurl": reverse('mlmtree:home'),
    })


@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_object(Tree)
def tree_view(request, tree: Tree):
    if request.user.is_superuser or Person.objects.filter(tree=tree, user=request.user).exists():
        return render(request, 'mlmtree/app/tree_view.html', {
            "tree": tree,
            "headertitle": tree.title,
            "headerurl": f"#{tree.top_id}",
        })
    return render(request, 'mlmtree/error.html', {
        "title": "403 - Zutritt verweigert!",
        "text": "Du hast keinen Zugriff auf diesen Baum!",
    }, status=403)

# API Views


API_404 = JsonResponse({
    "error": "not-found",
}, status=404)


@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_objects([("tree_id", Tree, "tree"), ("person_id", Person, "person")], custom_response=API_404)
def api_person_get(request, tree: Tree, person: Person):
    if person.tree_id != tree.pk:
        return JsonResponse({
            "error": "tree-does-not-match-person",
        }, status=404)

    if not (request.user.has_perm('mlmtree.view_person') or Person.objects.filter(tree=tree, user=request.user).exists()):
        return JsonResponse({
            "error": "permission-denied",
        }, status=403)

    return JsonResponse(person.json(urlpattern=tree.urlpattern, loggedinuser=request.user))


@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_objects([("tree_id", Tree, "tree"), ("person_id", Person, "person")], custom_response=API_404)
def api_person_get_teamcount(request, tree: Tree, person: Person):
    if person.tree_id != tree.pk:
        return JsonResponse({
            "error": "tree-does-not-match-person",
        }, status=404)

    if not (request.user.has_perm('mlmtree.view_person') or Person.objects.filter(tree=tree, user=request.user).exists()):
        return JsonResponse({
            "error": "permission-denied",
        }, status=403)

    return JsonResponse({"count": person.get_team_count(), "id": person.id})


@csrf_exempt
@require_POST
@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_objects([("tree_id", Tree, "tree"), ("person_id", Person, "parent")], custom_response=API_404)
def api_person_createchild(request, tree: Tree, parent: Person):
    if parent.tree_id != tree.pk:
        return JsonResponse({
            "error": "tree-does-not-match-person",
        }, status=404)

    permissions = parent.get_user_permissions(request.user)

    if not permissions['add']:
        return JsonResponse({
            "error": "permission-denied",
        }, status=403)

    if not request.POST.get('name', None):
        return JsonResponse({
            "error": "name-is-required",
        }, status=400)

    try:
        person = Person.objects.create(
            tree=tree,
            parent=parent,

            name=request.POST.get('name'),
            userid=request.POST.get('userid'),
            email=request.POST.get('email'),
            info=request.POST.get('info'),
        )

        return JsonResponse({
            "id": person.id,
        })
    except (AttributeError, ValueError):
        ...

    return JsonResponse({
        "error": "error",
    }, status=400)


@csrf_exempt
@require_POST
@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_objects([("tree_id", Tree, "tree"), ("person_id", Person, "person")], custom_response=API_404)
def api_person_update(request, tree: Tree, person: Person):
    if person.tree_id != tree.pk:
        return JsonResponse({
            "error": "tree-does-not-match-person",
        }, status=404)

    permissions = person.get_user_permissions(request.user)

    if not permissions['change']:
        return JsonResponse({
            "error": "permission-denied",
        }, status=403)

    if not request.POST.get('name', None):
        return JsonResponse({
            "error": "name-is-required",
        }, status=400)

    try:
        person.name = request.POST.get('name')
        person.userid = request.POST.get('userid')
        person.email = request.POST.get('email')
        person.info = request.POST.get('info')
        person.save()

        return JsonResponse({
            "id": person.id,
        })
    except (AttributeError, ValueError):
        ...

    return JsonResponse({
        "error": "error",
    }, status=400)


@csrf_exempt
@require_POST
@login_required(login_url=reverse_lazy('mlmtree:login'))
@require_objects([("tree_id", Tree, "tree"), ("person_id", Person, "person")], custom_response=API_404)
def api_person_delete(request, tree: Tree, person: Person):
    if person.tree_id != tree.pk:
        return JsonResponse({
            "error": "tree-does-not-match-person",
        }, status=404)

    permissions = person.get_user_permissions(request.user)

    if not permissions['remove']:
        return JsonResponse({
            "error": "permission-denied",
        }, status=403)

    person.delete()

    return JsonResponse({
        "success": True,
    })


def api_error404(request):
    return API_404

# Error view


def error404(request):
    return render(request, 'mlmtree/error.html', status=404)
