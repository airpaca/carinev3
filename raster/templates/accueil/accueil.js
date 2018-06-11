//todo
function preprocess_files(){
    $.get({
        url:"http://inf-tools/dashboard/log",
        data : {
            id : 'preprocess_files',
            script : 'carinev3/raster',
            etape : 1 ,
            type : 'INFO',
            m : 'début régénération des sources'
        }
    })
    $.ajax({
        url:'{% url "preprocess_files" %}',
        async : true,
        success : function(msg){
            check_statut()
            $("#poll_switch_1 > ."+active_poll_left_table ).click()
            refresh_right_table()
            process_files=true
            $.get({
                url:"http://inf-tools/dashboard/log",
                data : {
                    id : 'preprocess_files',
                    script :'carinev3/raster',
                    etape : 100,
                    type : 'INFO',
                    m : 'régénération des sources terminée'
                }
            })
        },
        error : function(msg){
            $.get({
                url:"http://inf-tools/dashboard/log",
                data : {
                id : 'preprocess_files',
                script : 'carinev3/raster',
                etape : 100,
                type : 'ERROR',
                m : 'régénération des sources incomplète, fichiers probablement corrompus'
                }
            })
        }
    })   
}
function init(){
	
	init='{{init.file_ok}}'
	if (init=='False') {
		$.ajax({
			url:'{% url "preprocess_files" %}',
			async : true,
			success : function(){
				$.get({
					url:'{% url "set_state" %}',
					async : true,
					data : { state : 'True' },
					success : function(msg){
						$(".loader-daddy").css("display","None")
						
						console.log(msg)
					}
				})
			}
		})
	}
	else {
		$(".loader-daddy").css("display","None")
		
		//$("#a-exploit").attr('href',"{% url 'index' %}")
	}
	$("#a-previ").attr('href',"{% url 'index' %}")
}
init()