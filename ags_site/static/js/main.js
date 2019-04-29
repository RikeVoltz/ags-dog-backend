$(document).ready(function () {
    applyCSRFTokenToAjaxRequests();
    $('.btn-show-test').on('click', function () {
        $('.test-container').show();
    });

    $('.btn-order-by-time').on('click', function () {
        $('.order-by-time-form').toggle();
    });

    $('.district-select').on('change', onDistrictSelectChangeHandler);

    $('.date-select').on('change', onDateSelectChangeHandler);

    $('.walking-type button').on('click', onWalkingTypeBtnClickHandler);

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
    $(".walker-img").hover(function () {
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


