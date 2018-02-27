$(function() {
    $('#upload-file-btn').click(function() {
	$('#no_pic_uploaded').hide();
	$('#file_too_big').hide();
        var form_data = new FormData($('#upload-file')[0]);
		if ($('#files')[0].files[0] == null)
			{$("#no_pic_uploaded").show();
			}
		var fsize = $('#files')[0].files[0].size;
		console.log(fsize)
		var maximum_file_size=document.getElementById("max_pic_size2").innerHTML;
		console.log("test jack")
        if(fsize>maximum_file_size*1048576) //do something if file size more than 1 mb (1048576)
			{$('#file_too_big').show();
			}
		else{
        $.ajax({
            type: 'POST',
            url: '/comparefile',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                var myDiv = $('#resultarea');
                myDiv.html(data);
            },            
        });
		};
    });
});

document.getElementById("files").onchange = function () {
	$('#file_too_big').hide();
	$('#upload-file-btn').prop('disabled', true);
    var reader = new FileReader();
	console.log("JAVAJAJ");
    reader.onload = function (e) {
        // get loaded data and render thumbnail.
		var previews = document.getElementsByClassName("prev_image");
		for (var i = 0; i < previews.length; i++) {
			previews[i].src = e.target.result;
    }
			var fsize = $('#files')[0].files[0].size;
			var maximum_file_size=document.getElementById("max_pic_size2").innerHTML;
			console.log(maximum_file_size)
				if(fsize<maximum_file_size*1048576) //do something if file size more than limit
					{$('#upload-file-btn').prop('disabled', false);
					}
				else{$('#file_too_big').show()};
	console.log("test");
    };
	
    // read the image file as a data URL.
    reader.readAsDataURL(this.files[0]);	
};

$(function(){
        // Check the initial Position of the Sticky Header
        var stickyHeaderTop = $('#image').offset().top;

        $(window).scroll(function(){
                if( $(window).scrollTop() > stickyHeaderTop ) {
                        $('#image').css({position: 'fixed', top: '0px', left:'70%', zIndex:'1000'});
                        $('#stickyalias').css('display', 'block');
                } else {
                        $('#image').css({position: 'static', top: '0px'});
                        $('#stickyalias').css('display', 'none');
                }
        });
  });
 
var enable_text = function() {
	var isChecked = $('#other_cat').prop('checked');
	return !isChecked;
	}
 
 $('.close_form').click(function() {
    $(this).parent().hide();
});
 
$(document).ready(function() {
  $("input[name='category']").click(function() {
	$("#cat_text").prop('disabled', enable_text);
   });

}); 
