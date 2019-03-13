$(document).ready(function () {

    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
				if(data.redirect){
					window.location.replace(data.redirect);
				}
            },
        });
    });

});
