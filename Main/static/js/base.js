function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function upload(event) {
    event.preventDefault();
    var data = new FormData(this);

    $("#importbutton").button("loading")

    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function (data, status) {
            if (data == "Ok") {
                $('.modal').modal('hide');
                $(".dynamic").load($(".dynamic").data("form"));
                $(".selected").load($(".selected").data("form"));
                $("#importbutton").button("complete")
            } else {
                $('.modal').empty();
                $('.modal').append(data);
                $(".modal").modal('show');
            }
        }
    });
    return false;
}


function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function popupwindow(url, title, w, h) {
    w = typeof w !== 'undefined' ? w : 800;
    h = typeof h !== 'undefined' ? h : 400;
    var left = 200;
    var top = -100;
    return window.open(url, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
}

function PopupCenter(url, title, w, h) {
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    if (window.focus) {
        newWindow.focus();
    }
}


$(function () {

    $('[data-toggle="tooltip"]').tooltip();

    $('body').tooltip({
        selector: '[data-toggle="tooltip"]'
    });

    $(".dynamic").on("click", ".download", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        window.location.href = url;
        return false;
    });

    $(".dynamic").on("click", ".silent", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $.get(url)
        $(".dynamic").empty();
        $(".dynamic").load($(".dynamic").data("form"));
        $(".selected").load($(".selected").data("form"));
        return false;
    });

    $(".dynamic").on("click", ".paging", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".dynamic").empty();
        $(".dynamic").load(url);
        return false;
    });

    $(".modal").on("click", ".paging", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").load(url);
        return false;
    });

    $(".dynamic").on("click", ".edit", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $(".dynamic").on("click", ".popup", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        PopupCenter(url, "preview", 800, 600);
        return false;
    });

    $(".modal").on("click", ".edit", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").empty();
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $(".selected").on("click", ".add", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $(".selected").on("click", ".edit", function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $(".new").click(function (ev) {
        ev.preventDefault();
        var url = $(this).data("form");
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $(".new-selected").click(function (ev) {
        ev.preventDefault();
        var url = $("#button-url").find(":selected").val();
        $(".modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });


    $('.modal').on('hidden.bs.modal', function () {
        $(this).empty();
    })

    $(".dynamic").load($(".dynamic").data("form"));

    var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $(".filter-input").on("keyup", function (ev) {
        delay(function () {
            if ($(".filter-input").val() != "") {
                $(".dynamic").load($(".dynamic").data("form") + '/' + $(".filter-input").val());
            } else {
                $(".dynamic").load($(".dynamic").data("form"));
            }
        }, 200);
    })

    $('.modal').on("submit", ".modal-form", function () {
        $.ajax({
            type: this.method,
            url: this.action,
            data: $(this).serialize(),
            context: this,
            success: function (data, status) {
                if (data == "Ok") {
                    $('.modal').modal('hide');
                    $(".dynamic").load($(".dynamic").data("form"));
                    $(".selected").load($(".selected").data("form"));
                } else {
                    $('.modal').empty();
                    $('.modal').append(data);
                    $(".modal").modal('show');
                }
            }
        });
        return false;
    });

    $('.modal').on("click", ".refresh", function () {
        $('.modal').load($(".refresh").data("url"));
        return false;
    });

    $('.modal').on("change", 'input[id=targetlist]', function () {
        $('#filepath').val($(this).val());
    })

    $('.modal').on("submit", ".modal-form-file", upload);

    $('.select').change(function (ev) {

        if ($("select option:selected").val() == "") {
            $(".selected").empty();
        } else {
            $(".selected").load($("select option:selected").data("form"));
            $(".selected").attr("data-form", $("select option:selected").data("form"))
        }
    })

    index_form = function (fset, index) {

        $(fset).find(':input').each(function () {
            var name = $(this).attr('name').replace(new RegExp('(\_\_prefix\_\_|\\d)'), index);
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id});
        });

        $(fset).find('label').each(function () {
            var newFor = $(this).attr('for').replace(new RegExp('(\_\_prefix\_\_|\\d)'), index);
            var id = 'label_' + newFor;
            $(this).attr({'id': id, 'for': newFor});
        });

    }

    reindex_formset = function (formset_zone) {

        var formset = $(formset_zone).find('.nsorte');
        for (var cpt = 0; cpt < formset.length; cpt++) {
            index_form(formset[cpt], cpt);
        }
        ;

        $("#id_form-TOTAL_FORMS").val(parseInt(cpt));

    };

    set_event = function () {
        $('.modal').on('click', ".bt_rm_sorte", function () {
            $(this).parents(".nsorte").remove();
            reindex_formset("#formsetZone");
        });
    };

    $('.modal').on('click', "#bt_add_sorte", function () {

        $("#eform").clone(true).appendTo($("#formsetZone"));

        reindex_formset("#formsetZone");

    });

    set_event();
});
