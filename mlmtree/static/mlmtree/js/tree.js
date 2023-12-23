// (c) 2021 Rafael Urben
// https://github.com/rafaelurben

function _loading_start() {
    $('#content').addClass('loading');
    $('#spinner').removeClass('d-none');
}

function _loading_end() {
    $('#content').removeClass('loading');
    $('#spinner').addClass('d-none');
}

window.addEventListener('load', () => {
    _loading_start();
})

function _mlmtree_pcard_update($card, person) {
    $card.attr("href", `#${person.id}`);
    $card.find(".mlmtree-pcardname").text(person.name);
    $card.find(".mlmtree-pcarduserid").text(person.userid);
    $card.find(".mlmtree-pcardinfo").text(person.info);

    if (person.has_user_connected) {
        if (person.has_user_connected === "own") {
            $card.find(".mlmtree-badges").append($('<span class="badge bg-secondary ms-1 px-1" data-bs-toggle="tooltip" data-bs-placement="top" title="Diese Identität ist mit deinem Account verknüpft"><i class="fa-fw fas fa-user text-warning"></i></span>'))
        } else {
            $card.find(".mlmtree-badges").append($('<span class="badge bg-secondary ms-1 px-1" data-bs-toggle="tooltip" data-bs-placement="top" title="Diese Identität ist mit einem Account verknüpft"><i class="fa-fw fas fa-user"></i></span>'))
        }
    }
    if (person.childcount) {
        $card.find(".mlmtree-badges").append($(`<span class="badge bg-info ms-1" data-bs-toggle="tooltip" data-bs-placement="top" title="Anzahl der direkten 'Kinder' - Klicken um die gesamte Teamgrösse zu berechnen." onclick="mlmtree_get_teamcount(${person.id}, this); return false;">${person.childcount}</span>`))
    }
    if (person.url) {
        $card.find(".mlmtree-badges").append($(`<a class="badge bg-primary ms-1" data-bs-toggle="tooltip" data-bs-placement="top" title="${person.url}" href="${person.url}" target="_blank"><i class="fas fa-link"></i></a>`))
    }
    if (person.email) {
        $card.find(".mlmtree-badges").append($(`<a class="badge bg-primary ms-1" data-bs-toggle="tooltip" data-bs-placement="top" title="${person.email}" href="mailto:${person.email}"><i class="fas fa-envelope"></i></a>`))
    }
}

function _bs_enable_tooltips() {
    // Reset old tooltips
    $('.tooltip').remove();
    // Enable tooltips everywhere
    var $elements = $('[data-bs-toggle="tooltip"]')
    $elements.each(function (index, value) {
        new bootstrap.Tooltip(value);
    })
}

// MLMTree: Load a person

const toast_error = new bootstrap.Toast(document.getElementById('toast-error'));
const toast_success = new bootstrap.Toast(document.getElementById('toast-success'));


function mlmtree_loadperson(pid) {
    const $pmain = $("#person-main");
    const $pparent = $("#person-parent");
    const $pinfo = $("#person-actions");
    const $pchildren = $("#person-children");
    const $pcardtemplate = $("#personcardtemplate");
    
    _loading_start();

    $.get(
        url = `${window.mlmtree_api_url_base}t/${window.mlmtree_tree_id}/p/${pid}/get`,
        success = function (data) {
            console.log(data);

            // Clear old data
            $pchildren.empty();

            $pmain.children('div').remove();
            $pmain.removeAttr("href");
            var $card = $($pcardtemplate[0].content.firstElementChild.firstElementChild.cloneNode(true));
            $pmain.append($card);

            $pparent.children('div').remove();
            $pparent.removeAttr("href");
            var $card = $($pcardtemplate[0].content.firstElementChild.firstElementChild.cloneNode(true));
            $pparent.append($card);

            $pinfo.children('div').remove();

            // Add new data
            _mlmtree_pcard_update($pmain, data);

            if (data.hasOwnProperty("parent")) {
                _mlmtree_pcard_update($pparent, data.parent);
            }

            $pinfo.append($("<div></div>"));
            $pinfocontainer = $pinfo.children('div');
            if (data.permissions.add) {
                $pinfocontainer.append($(`<a type="button" class="btn btn-dark w-100" data-bs-toggle="modal" data-bs-target="#addChildFormModal" data-bs-personname="${data.name}" data-bs-personid="${data.id}"><i class="fas fa-plus me-2"></i>Kind erstellen</a>`))
            }
            if (data.permissions.change) {
                $pinfocontainer.append($(`<a type="button" class="btn btn-dark w-100 mt-2" data-bs-toggle="modal" data-bs-target="#editPersonFormModal" data-bs-personinfo="${data.info}" data-bs-personuserid="${data.userid}" data-bs-personemail="${data.email}" data-bs-personname="${data.name}" data-bs-personid="${data.id}"><i class="fas fa-edit me-2"></i>Person bearbeiten</a>`))
            }
            if (data.permissions.remove) {
                parentid = data.parent ? data.parent.id : $("#menubartitle").attr("href").substr(1);
                $pinfocontainer.append($(`<a type="button" class="btn btn-danger w-100 mt-2" data-bs-toggle="modal" data-bs-target="#deletePersonFormModal" data-bs-personname="${data.name}" data-bs-personid="${data.id}" data-bs-personemail="${data.email}" data-bs-personname="${data.name}" data-bs-personid="${data.id}" data-bs-parentid="${parentid}"><i class="fas fa-trash me-2"></i>Person löschen</a>`))
            }

            data.children.forEach(function (person) {
                var $card = $($pcardtemplate[0].content.firstElementChild.cloneNode(true));
                _mlmtree_pcard_update($card, person);
                $pchildren.append($card);
            })

            // Activate tooltips again

            _bs_enable_tooltips();
        }
    ).done(function () {
        _loading_end();
    }).fail(function () {
        _loading_end();
        toast_error.show();
    })
}

// MLMTree: Get a team count


function mlmtree_get_teamcount(pid, elem) {
    _loading_start();

    $.get(
        url = `${window.mlmtree_api_url_base}t/${window.mlmtree_tree_id}/p/${pid}/get/teamcount`,
        success = function (data) {
            console.log(data);
            elem.removeAttribute('onclick');
            elem.title = "Anzahl direkter 'Kinder'";
            newelem = elem.cloneNode();
            newelem.title = `Gesamtteamgrösse`;
            newelem.className = "badge bg-danger ms-1";
            newelem.innerText = data.count;
            elem.insertAdjacentElement("afterend", newelem);
            _bs_enable_tooltips(newelem);
        }
    ).done(function () {
        _loading_end();
    }).fail(function () {
        _loading_end();
        toast_error.show();
    })
}

// MLMTree: Create a new child

const addChildFormModalElement = document.getElementById('addChildFormModal');
const addChildFormModal = new bootstrap.Modal(addChildFormModalElement);

window.addEventListener('load', () => {
    addChildFormModalElement.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;

        $('#addchildform--personname').text(button.getAttribute('data-bs-personname'));
        $('#addchildform--personid').text(button.getAttribute('data-bs-personid'));
    })
})

function mlmtree_addchild_post() {
    var pid = $('#addchildform--personid').text();

    if (!$('#addchildform-name').val()) {
        return;
    }

    $.post(
        url = `${window.mlmtree_api_url_base}t/${window.mlmtree_tree_id}/p/${pid}/createchild`,
        data = {
            'name': $('#addchildform-name').val(),
            'userid': $('#addchildform-userid').val(),
            'email': $('#addchildform-email').val(),
            'info': $('#addchildform-info').val(),
        },
        success = function (data) {
            location.hash = data.id;

            $('#addchildform-name').val("");
            $('#addchildform-userid').val("");
            $('#addchildform-email').val("");
            $('#addchildform-info').val("");
        },
    ).done(function () {
        addChildFormModal.hide();
        toast_success.show();
    }).fail(function () {
        toast_error.show();
    })
}


// MLMTree: Edit a person

const editPersonFormModalElement = document.getElementById('editPersonFormModal');
const editPersonFormModal = new bootstrap.Modal(editPersonFormModalElement);

window.addEventListener('load', () => {
    editPersonFormModalElement.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;

        $('#editpersonform--personname').text(button.getAttribute('data-bs-personname'));
        $('#editpersonform--personid').text(button.getAttribute('data-bs-personid'));

        $('#editpersonform-name').val(button.getAttribute('data-bs-personname'));
        $('#editpersonform-userid').val(button.getAttribute('data-bs-personuserid'));
        $('#editpersonform-email').val(button.getAttribute('data-bs-personemail'));
        $('#editpersonform-info').val(button.getAttribute('data-bs-personinfo'));
    })
})

function mlmtree_editperson_post() {
    var pid = $('#editpersonform--personid').text();

    if (!$('#editpersonform-name').val()) {
        return;
    }

    $.post(
        url = `${window.mlmtree_api_url_base}t/${window.mlmtree_tree_id}/p/${pid}/update`,
        data = {
            'name': $('#editpersonform-name').val(),
            'userid': $('#editpersonform-userid').val(),
            'email': $('#editpersonform-email').val(),
            'info': $('#editpersonform-info').val(),
        },
        success = function (data) {
            $('#editpersonform-name').val("");
            $('#editpersonform-userid').val("");
            $('#editpersonform-email').val("");
            $('#editpersonform-info').val("");
        },
    ).done(function () {
        mlmtree_loadperson(pid);
        editPersonFormModal.hide();
        toast_success.show();
    }).fail(function () {
        toast_error.show();
    })
}

// MLMTree: Delete a person

const deletePersonFormModalElement = document.getElementById('deletePersonFormModal');
const deletePersonFormModal = new bootstrap.Modal(deletePersonFormModalElement);

window.addEventListener('load', () => {
    deletePersonFormModalElement.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;

        $('#deletepersonform--personname').text(button.getAttribute('data-bs-personname'));
        $('#deletepersonform--personid').text(button.getAttribute('data-bs-personid'));
        $('#deletepersonform--parentid').text(button.getAttribute('data-bs-parentid'));

        $('#deletepersonform-name').val(button.getAttribute('data-bs-personname'));
        $('#deletepersonform-userid').val(button.getAttribute('data-bs-personuserid'));
        $('#deletepersonform-email').val(button.getAttribute('data-bs-personemail'));
        $('#deletepersonform-info').val(button.getAttribute('data-bs-personinfo'));
    })
})

function mlmtree_deleteperson_post() {
    var pid = $('#deletepersonform--personid').text();

    $.post(
        url = `${window.mlmtree_api_url_base}t/${window.mlmtree_tree_id}/p/${pid}/delete`,
        data = {},
        success = function (data) {
            $('#deletepersonform-name').val("");
            $('#deletepersonform-userid').val("");
            $('#deletepersonform-email').val("");
            $('#deletepersonform-info').val("");
        },
    ).done(function () {
        mlmtree_loadperson($('#deletepersonform--parentid').text());
        deletePersonFormModal.hide();
        toast_success.show();
    }).fail(function () {
        toast_error.show();
    })
}