function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function applyCSRFTokenToAjaxRequests() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            let csrf_token = $.cookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
}

function onDistrictSelectAjaxSuccessHandler(data) {
    data = $.parseJSON(data);
    if (data.length === 0) {
        $('.order-by-time-form').append('<span class="no-walkers-warning" style="color:red">К сожалению, в данном районе пока нет выгульщиков. Пожалуйста, выберите другой район</span>')
    } else {
        date_select.append('<option value="" disabled selected style=\'display:none;\'>Выберите из списка</option>');
        $(data).each(function () {
            $('.date-select').append(`<option value="${this}">${this}</option>`);
        });
        $('.date-select').show();
    }
}


$(document).ready(function () {
    applyCSRFTokenToAjaxRequests();
    let district_select = $('.district-select');
    let date_select = $('.date-select');
    let walkers_panel = $('.walkers-panel');
    let no_walker_warning = $('.no-walkers-warning');
    let walking_type = $('.walking-type');
    let walking_cost = $('.row-cost-walking');
    let booked_time_btn = $('.btn-book-time.activated');
    let walking_type_activated_btn = $('.walking-type button.activated');
    let walking_order_contacts = $('.walking-order-contacts');
    let btn_save_booking = $('.btn-save-booking');

    $('.btn-show-test').on('click', function () {
        $('.test-container').show();
    });

    $('.btn-order-by-time').on('click', function () {
        $('.order-by-time-form').toggle();
    });

    district_select.on('change', function () {
        date_select.empty();
        date_select.hide();
        walkers_panel.empty();
        walkers_panel.hide();
        walking_order_contacts.hide();
        no_walker_warning.hide();
        walking_type_activated_btn.removeClass('activated');
        walking_type.hide();
        walking_cost.hide();
        btn_save_booking.hide();
        $.ajax({
            type: "POST",
            url: '/walking/',
            data: {'walking_zone': $(this).val()},
            success: onDistrictSelectAjaxSuccessHandler,
        });
    });

    date_select.on('change', function () {
        walkers_panel.empty();
        walkers_panel.hide();
        walking_order_contacts.hide();
        no_walker_warning.hide();
        walking_type_activated_btn.removeClass('activated');
        walking_type.hide();
        walking_cost.hide();
        btn_save_booking.hide();
        $.ajax({
            type: "POST",
            url: '/walking/',
            data: {'walking_zone': district_select.val(), 'day_month': $(this).val()},
            success: function (data) {
                data = $.parseJSON(data);
                $(data[0]).each(function () {
                    let hours = '';
                    $(this.hours).each(function () {
                        hours += `<input type="button" class="btn btn-book-time p-0" value="${this}">`;
                    });
                    $('.walkers-panel').append(`<div id="${this.walker_id}" data-toggle="popover" data-placement="left"` +
                        ` data-container="body"  data-content="Данный волкер находится рядом с выбранным Вами районом"` +
                        ` class="card walker-order-card green-walker"><img src="/media/${this.photo}" class="card-img-top walker-order-card-img img-fluid green-border" alt="...">` +
                        `<div class="card-body"><h5 class="card-title walker-order-card-title">${this.name}</h5>` +
                        `<div class="card-text walker-order-card-text d-flex justify-content-center">${hours}</div></div>` +
                        `</div>`);
                });
                $(data[1]).each(function () {
                    let hours = '';
                    $(this.hours).each(function () {
                        hours += `<input type="button" class="btn btn-book-time p-0" value="${this}">`;
                    });
                    $('.walkers-panel').append(`<div id="${this.walker_id}" data-toggle="popover" data-placement="left"` +
                        ` data-container="body"  data-content="Данный волкер находится далеко от выбранного Вами района"` +
                        ` class="card walker-order-card blue-walker"><img src="/media/${this.photo}" class="card-img-top walker-order-card-img img-fluid blue-border" alt="...">` +
                        `<div class="card-body"><h5 class="card-title walker-order-card-title">${this.name}</h5>` +
                        `<div class="card-text walker-order-card-text d-flex justify-content-center">${hours}</div></div>` +
                        `</div>`);
                });
                $('.walker-order-card').on("mouseover", function () {
                    $(this).popover('show');
                });

                $('.walker-order-card').on("mouseout", function () {
                    $(this).popover('hide');
                });
                $('.btn-book-time').on('click', function () {
                    if (!$(this).hasClass('activated')) {
                        $(this).addClass('activated');
                        $('.walking-type').show();
                        if ($(this).parents('.walker-order-card').hasClass('green-walker')) {
                            if ($('.walking-type button.activated').text() === 'Классический') {
                                $('.walking-cost').text(300 * $('.btn-book-time.activated').length);
                            } else {
                                $('.walking-cost').text(350 * $('.btn-book-time.activated').length);
                            }
                        } else if ($(this).parents('.walker-order-card').hasClass('blue-walker')) {
                            if ($('.walking-type button.activated').text() === 'Классический') {
                                $('.walking-cost').text(450 * $('.btn-book-time.activated').length);
                            } else {
                                $('.walking-cost').text(500 * $('.btn-book-time.activated').length);
                            }
                        }
                    } else {
                        $(this).removeClass('activated');
                        if ($('.btn-book-time.activated').length === 0) {
                            $('.walking-type').hide();
                            $('.btn-save-booking').hide();
                            $('.walking-type button.activated').removeClass('activated');
                            $('.row-cost-walking').hide();
                        } else {
                            if ($(this).parents('.walker-order-card').hasClass('green-walker')) {
                                if ($('.walking-type button.activated').text() === 'Классический') {
                                    $('.walking-cost').text(300 * $('.btn-book-time.activated').length);
                                } else {
                                    $('.walking-cost').text(350 * $('.btn-book-time.activated').length);
                                }
                            } else if ($(this).parents('.walker-order-card').hasClass('blue-walker')) {
                                if ($('.walking-type button.activated').text() === 'Классический') {
                                    $('.walking-cost').text(450 * $('.btn-book-time.activated').length);
                                } else {
                                    $('.walking-cost').text(500 * $('.btn-book-time.activated').length);
                                }
                            }
                        }
                    }
                });
                $('.walkers-panel').show();
                $('.walking-order-contacts').show();
                $('.btn-save-booking').hide();
                $('.row-cost-walking').hide();
                $('.walking-type').hide();
                $('.btn-book-time.activated').removeClass('activated');
                $('.walking-type button.activated').removeClass('activated');
            },
        });
    });

    $('.walking-type button').on('click', function () {
        if ($('.btn-book-time.activated').parents('.walker-order-card').hasClass('green-walker')) {
            if ($(this).text() === 'Классический') {
                $('.walking-cost').text(300 * $('.btn-book-time.activated').length);
            } else {
                $('.walking-cost').text(350 * $('.btn-book-time.activated').length);
            }
        } else if ($('.btn-book-time.activated').parents('.walker-order-card').hasClass('blue-walker')) {
            if ($(this).text() === 'Классический') {
                $('.walking-cost').text(450 * $('.btn-book-time.activated').length);
            } else {
                $('.walking-cost').text(500 * $('.btn-book-time.activated').length);
            }
        }
        if (!$(this).hasClass('activated')) {
            $('.walking-type button.activated').removeClass('activated');
            $(this).addClass('activated');
            $('.btn-save-booking').show();
            $('.row-cost-walking').show();
        } else {
            $(this).removeClass('activated');
            if ($('.walking-type button.activated').length === 0) {
                $('.btn-save-booking').hide();
                $('.row-cost-walking').hide();
            }
        }
    });

    $('.map-pop').on('click', function () {
        $('.map-preview').attr('src', $(this).find('img').attr('src'));
        $('#map-modal').modal('show');
    });

    $('.calendar-carousel').flickity({
        wrapAround: true,
    });

    $('.calendar-col:not(.calendar-col-h):not(.hour-booked):not(.hour-disabled)').on('click', function () {
        $(this).toggleClass('hour-activated');
    });

    $('.order-walking-form').submit(function (event) {
        event.preventDefault();
        $("#walking-order-success").modal('toggle');
        let form_data = getOrderWalkingFormData();
        $.ajax({
                type: "POST",
                url: "/book_walking/",
                data: form_data,
                processData: false,
                contentType: false,
            }
        );
    });

    $('.walking-dates-form').submit(function () {
        let walking_dates = getWalkingDatesMap();
        let serialized_walking_dates = serializeWalkingDates(walking_dates);
        $('#id_walking_dates').val(serialized_walking_dates);
    });

    $('.main-photos-carousel').flickity({
        wrapAround: true,
    });

    $(".dropdown").hover(onDropdownHoverHandler);

    $('.arrow-up').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 600);
    });
    $(".walker-img").on("mouseover mouseout", function () {
        let tmp = $(this).attr('src');
        $(this).attr('src', $(this).attr('data-alter-img'));
        $(this).attr('data-alter-img', tmp);
    });

    $(".blacker").hover(onBlackerMouseoverHandler, onBlackerMouseoutHandler);

    $(".far-area").on("mouseover", function () {
        $(this).popover('show')
    }).on("mouseout", function () {
        $(this).popover('hide')
    });
});

$(window).scroll(function () {
    if ($(this).scrollTop() >= 50) {
        $('.arrow-up').fadeIn(200, function () {
            $(".arrow-up").attr("style", "display: flex!important");
        });
    } else {
        $('.arrow-up').fadeOut(200, function () {
            $(".arrow-up").attr("style", "display: none!important");
        });
    }
});

function onDropdownHoverHandler() {
    let dropdown_menu = $('.dropdown-menu', this).not('.in .dropdown-menu');
    dropdown_menu.stop(true, true);
    if ($(this).hasClass('open'))
        dropdown_menu.slideUp(150);
    else
        dropdown_menu.slideDown(150);
    $(this).toggleClass('open');
}

function serializeWalkingDates(walking_dates) {
    let serialized = "";
    for (let [day, hours] of walking_dates) {
        serialized += `${day}-${hours.join(',')};`;
    }
    return serialized;
}

function getOrderWalkingFormData() {
    let result = new FormData();
    let booked_time_btn = $('.btn-book-time.activated');
    result.append('name', $('.order-walking-name-input').val());
    result.append('breed', $('.order-walking-breed-input').val());
    result.append('type', $('.walking-type button.activated').text());
    result.append('address', $('.order-walking-address-input').val());
    result.append('hour', booked_time_btn.val().split(':')[0]);
    result.append('day', $('.date-select').val());
    result.append('walker_id', booked_time_btn.parents('.walker-order-card').prop('id'));
    return result;
}

function getWalkingDatesMap() {
    let result = new Map();
    $('.hour-activated').each(function () {
        let cur_month_days = parseInt($('.calendar-carousel-cell:first >.container> .calendar-row:last > .calendar-col-h:first-child').text());
        let hour = parseInt(this.id.split('-')[1]);
        let day = parseInt($(this).parents('.calendar-row').prop('id').split('-')[1]);
        let month = parseInt($(this).parents('.calendar-carousel-cell').prop('id').split('-')[1]);
        let idx = cur_month_days * month + day - 1;
        if (result.has(idx)) {
            let tmp = result.get(idx);
            tmp.push(hour + 7);
            result.set(idx, tmp);
        } else
            result.set(idx, [hour + 7]);
    });
    return result;
}

function onBlackerMouseoverHandler() {
    if (!$(this).hasClass("activated")) {
        let blacker_text = $(this).children(".blacker-text");
        let main_table_col = $(this).children(".main-table-col");
        main_table_col.stop(false, false).animate({opacity: 0.2}, 500);
        let margin_top = "37vh";
        if (main_table_col.hasClass("main-table-col-up"))
            margin_top = "-" + margin_top;
        blacker_text.stop(false, false).animate({"margin-top": margin_top}, 500);
        $(this).addClass("activated");
        $(this).find(".blacker-btn").stop(false, false).animate({"z-index": 2000}, 300);
    }
}

function onBlackerMouseoutHandler() {
    if ($(this).hasClass("activated")) {
        $(this).children(".main-table-col").stop(false, false).animate({opacity: 1}, 500);
        $(this).children(".blacker-text").stop(false, false).animate({"margin-top": "0vh"}, 500);
        $(this).removeClass("activated");
        $(this).find(".blacker-btn").stop(false, false).animate({"z-index": -1}, 300);
    }
}
