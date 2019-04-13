$(document).ready(function () {

    $('.calendar-carousel').flickity({
        wrapAround: true,
    });

    $('.calendar-col:not(.calendar-col-h):not(.hour-booked):not(.hour-disabled)').on('click', function () {
        if ($(this).hasClass('hour-activated')) {
            $(this).removeClass('hour-activated');
        } else
            $(this).addClass('hour-activated');
    });

    $('.walking-dates-form').submit(function (event) {
        let walking_dates = new Map();
        $('.hour-activated').each(function () {
            let cur_month_days = parseInt($('.calendar-carousel-cell:first .calendar-row:last-child .calendar-col-h:first-child').text());
            let hour = parseInt(this.id.split('-')[1]);
            let day = parseInt($(this).parent().prop('id').split('-')[1]);
            let month = parseInt($(this).parents('.calendar-carousel-cell').prop('id').split('-')[1]);
            let idx = cur_month_days * month + day;
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


