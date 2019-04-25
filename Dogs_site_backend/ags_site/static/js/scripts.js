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
    for (let [day, hours] of walking_dates)
        serialized += `${day}-${hours.join(',')};`;
    return serialized;
}

function getOrderWalkingFormData() {
    let result = new FormData();
    let booked_time_btn = $('.btn-book-time.activated');
    result.extend('name', $('.order-walking-name-input').val());
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
    let date_select = $('.date-select');
    data = $.parseJSON(data);
    if (data.length === 0) {
        date_select.hide();
        $('.order-by-time-form').append('<span class="no-walkers-warning" style="color:red">К сожалению, в данном районе пока нет выгульщиков. Пожалуйста, выберите другой район</span>')
    } else {
        date_select.append('<option value="" disabled selected style=\'display:none;\'>Выберите из списка</option>');
        $(data).each(function () {
            $('.date-select').append(`<option value="${this}">${this}</option>`);
        });
        date_select.show();
    }
}

function createWalkerCards(walkers_data, is_blue) {
    let popup_message = (is_blue) ? 'Данный волкер находится далеко от выбранного Вами района' : 'Данный волкер находится рядом с выбранным Вами районом';
    $(walkers_data).each(function () {
            let hours = '';
            $(this.hours).each(function () {
                hours += `<input type="button" class="btn btn-book-time p-0" value="${this}">`;
            });
            $('.walkers-panel').append(`<div id="${this.walker_id}" data-toggle="popover" data-placement="left"` +
                ` data-container="body"  data-content="${popup_message}"` +
                ` class="card walker-order-card ${(is_blue) ? 'blue' : 'green'}-walker"><img src="/media/${this.photo}" class="card-img-top walker-order-card-img img-fluid ${(is_blue) ? 'blue' : 'green'}-border" alt="...">` +
                `<div class="card-body"><h5 class="card-title walker-order-card-title">${this.name}</h5>` +
                `<div class="card-text walker-order-card-text d-flex justify-content-center">${hours}</div></div>` +
                `</div>`);
        }
    );
}

function changeCost() {
    let cost = 0;
    let bookTimeBtnActivated = $('.btn-book-time.activated');
    if (bookTimeBtnActivated.parents('.walker-order-card').hasClass('green-walker'))
        cost = 300;
    else
        cost = 450;
    if ($('.walking-type button.activated').text() === 'Активный')
        cost += 50;
    $('.walking-cost').text(cost * bookTimeBtnActivated.length);
}

function onClickBookedTimeBtnHandler() {
    if (!$(this).hasClass('not-click')) {
        $(this).toggleClass('activated');
        let bookTimeBtnActivated = $('.btn-book-time.activated');
        if (bookTimeBtnActivated.length === 0) {
            $('.btn-book-time.not-click').removeClass('not-click');
            $('.walking-type').hide();
            $('.btn-save-booking').hide();
            $('.walking-type button.activated').removeClass('activated');
            $('.row-cost-walking').hide();
        } else {
            $('.btn-book-time').addClass('not-click');
            $(this).parent().children().removeClass('not-click');
            $('.walking-type').show();
            changeCost();
        }
    }
}

function onDataSelectAjaxSuccessHandler(data) {
    let walker_panels = $('.walkers-panel');
    data = $.parseJSON(data);
    walker_panels.empty();
    createWalkerCards(data[0], false);
    createWalkerCards(data[1], true);
    $('.walker-order-card').hover(function () {
            $(this).popover('show');
        }, function () {
            $(this).popover('hide');
        },
    );
    $('.btn-book-time').on('click', onClickBookedTimeBtnHandler);
    walker_panels.show();
    $('.walking-order-contacts').show();
    $('.btn-save-booking').hide();
    $('.row-cost-walking').hide();
    $('.walking-type').hide();
    $('.btn-book-time.activated').removeClass('activated');
    $('.walking-type button.activated').removeClass('activated');
}

function onDistrictSelectChangeHandler() {
    let walkers_panel = $('.walkers-panel');
    $('.walker-order-card').popover('hide');
    $('.date-select').empty();
    walkers_panel.empty();
    walkers_panel.hide();
    $('.walking-order-contacts').hide();
    $('.no-walkers-warning').hide();
    $('.walking-type button.activated').removeClass('activated');
    $('.walking-type').hide();
    $('.row-cost-walking').hide();
    $('.btn-save-booking').hide();
    $.ajax({
        type: "POST",
        url: '/walking/',
        data: {'walking_zone': $(this).val()},
        success: onDistrictSelectAjaxSuccessHandler,
    });
}

function onDateSelectChangeHandler() {
    $('.walker-order-card').popover('hide');
    $.ajax({
        type: "POST",
        url: '/walking/',
        data: {'walking_zone': $('.district-select').val(), 'day_month': $(this).val()},
        success: onDataSelectAjaxSuccessHandler
    });
}

function onWalkingTypeBtnClickHandler() {
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
    changeCost();
}
