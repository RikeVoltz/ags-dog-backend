function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function () {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            let csrf_token = $.cookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
    $('.btn-order-by-time').on('click', function () {
        $('.order-by-time-form').toggle();
    });

    $('.district-select').on('change', function () {
        $('.date-select').hide();
        $('.walkers-panel').hide();
        $('.walking-order-contacts').hide();
        $('.no-walkers-warning').hide();
        $('.walking-type').hide();
        $('.btn-save-booking').hide();
        $('.row-cost-walking').hide();
        $('.btn-book-time.activated').removeClass('activated');
        $('.walking-type button.activated').removeClass('activated');
        $.ajax({
            type: "POST",
            url: '/walking/',
            data: {'walking_zone': $(this).val()},
            success: function (data) {
                $('.date-select').empty();
                data = $.parseJSON(data);
                if (data.length === 0) {
                    $('.order-by-time-form').append('<span class="no-walkers-warning" style="color:red">К сожалению, в данном районе пока нет выгульщиков. Пожалуйста, выберите другой район</span>')
                } else {
                    $('.date-select').append('<option value="" disabled selected style=\'display:none;\'>Выберите из списка</option>');
                    $(data).each(function () {
                        $('.date-select').append(`<option value="${this}">${this}</option>`);
                    });
                    $('.date-select').show();
                }
                $('.walkers-panel').hide();
                $('.btn-save-booking').hide();
                $('.walking-type').hide();
                $('.btn-book-time.activated').removeClass('activated');
                $('.walking-type button.activated').removeClass('activated');
                $('.row-cost-walking').hide();
            },
        });
    });

    $('.date-select').on('change', function () {
        $('.btn-save-booking').hide();
        $('.row-cost-walking').hide();
        $.ajax({
            type: "POST",
            url: '/walking/',
            data: {'walking_zone': $('.district-select').val(), 'day_month': $(this).val()},
            success: function (data) {
                data = $.parseJSON(data);
                $('.walkers-panel').empty();
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

    $(function () {
        $('.map-pop').on('click', function () {
            $('.map-preview').attr('src', $(this).find('img').attr('src'));
            $('#map-modal').modal('show');
        });
    });

    $('.calendar-carousel').flickity({
        wrapAround: true,
    });

    $('.calendar-col:not(.calendar-col-h):not(.hour-booked):not(.hour-disabled)').on('click', function () {
        if ($(this).hasClass('hour-activated')) {
            $(this).removeClass('hour-activated');
        } else
            $(this).addClass('hour-activated');
    });

    $('.order-walking-form').submit(function (event) {
        event.preventDefault();
        let form_data = new FormData();
        form_data.append('name', $('.order-walking-name-input').val());
        form_data.append('breed', $('.order-walking-breed-input').val());
        form_data.append('type', $('.walking-type button.activated').text());
        form_data.append('address', $('.order-walking-address-input').val());
        form_data.append('hour', $('.btn-book-time.activated').val().split(':')[0]);
        form_data.append('day', $('.date-select').val());
        form_data.append('walker_id', $('.btn-book-time.activated').parents('.walker-order-card').prop('id'));
        $.ajax({
                type: "POST",
                url: "/book_walking/",
                data: form_data,
                processData: false,
                contentType: false,
            }
        );
    });

    $('.walking-dates-form').submit(function (event) {
        let walking_dates = new Map();
        $('.hour-activated').each(function () {
            let cur_month_days = parseInt($('.calendar-carousel-cell:first >.container> .calendar-row:last > .calendar-col-h:first-child').text());
            let hour = parseInt(this.id.split('-')[1]);
            let day = parseInt($(this).parents('.calendar-row').prop('id').split('-')[1]);
            let month = parseInt($(this).parents('.calendar-carousel-cell').prop('id').split('-')[1]);
            let idx = cur_month_days * month + day - 1;
            if (walking_dates.has(idx)) {
                let tmp = walking_dates.get(idx);
                tmp.push(hour + 7);
                walking_dates.set(idx, tmp);
            } else
                walking_dates.set(idx, [hour + 7]);

        });
        let res = "";
        for (let [day, hours] of walking_dates) {
            res += `${day}-${hours.join(',')};`;
        }
        $('#id_walking_dates').val(res);

    });

    $('.main-photos-carousel').flickity({
        wrapAround: true,
    });

    $(".dropdown").hover(
        function () {
            $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideDown(150);
            $(this).toggleClass('open');
        },
        function () {
            $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideUp(150);
            $(this).toggleClass('open');
        }
    );
    $('.zone-arrow-up').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 600);
    });
    $(".walker-img").on("mouseover mouseout", function () {
        let tmp = $(this).attr('src');
        $(this).attr('src', $(this).attr('data-alter-img'));
        $(this).attr('data-alter-img', tmp);
    });

    $(".blacker").on("mouseover", function () {
        if (!$(this).hasClass("activated")) {
            if ($(this).children(".main-table-col").hasClass("main-table-col-down")) {
                $(this).children(".main-table-col").stop(false, false).animate({opacity: 0.2}, 500);
                $(this).children(".blacker-text").stop(false, false).animate({"margin-top": "37vh"}, 500);
            } else {
                $(this).children(".main-table-col").stop(false, false).animate({opacity: 0.2}, 500);
                $(this).children(".blacker-text").stop(false, false).animate({"margin-top": "-37vh"}, 500);
            }
            $(this).addClass("activated");
            $(this).find(".blacker-btn").stop(false, false).animate({"z-index": 2000}, 300);
        }
    });

    $(".blacker").on("mouseout", function () {
        if ($(this).hasClass("activated")) {
            $(this).children(".main-table-col").stop(false, false).animate({opacity: 1}, 500);
            $(this).children(".blacker-text").stop(false, false).animate({"margin-top": "0vh"}, 500);
            $(this).removeClass("activated");
            $(this).find(".blacker-btn").stop(false, false).animate({"z-index": -1}, 300);
        }
    });

    $(".far-area").on("mouseover", function () {
        $(this).popover('show');
    });

    $(".far-area").on("mouseout", function () {
        $(this).popover('hide');
    });
});

$(window).scroll(function () {
    if ($(this).scrollTop() >= 50) {
        $('.zone-arrow-up').fadeIn(200, function () {
            $(".zone-arrow-up").attr("style", "display: flex!important");
        });
        $('.arrow-up').fadeIn(200);
    } else {
        $('.zone-arrow-up').fadeOut(200, function () {
            $(".zone-arrow-up").attr("style", "display: none!important");
        });
        $('.arrow-up').fadeOut(200);
    }
});


;
;