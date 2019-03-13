$(document).ready(function () {
	//Ajax call for getting the file path
    var data = "Hello";
    $.ajax({
            type: 'GET',
            url: '/file_path',
            data: data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
				var file_path = data.slice(8);
				document.getElementById("leaf").src = "/uploads/"+file_path;
            },
        });
    });

