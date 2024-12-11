$(document).ready(function() {
    
    showHeart();
});


function showHeart() {
    $.ajax({
        type: 'GET',
        url: '/show_heart/{{name}}/',  
        data: {},
        success: function(response) {
            let my_heart = response['my_heart'];  
            if (my_heart && my_heart['interested'] === 'Y') {
                
                $("#heart").css("color", "red");
                $("#heart").attr("onclick", "unlike()");  
            } else {
                
                $("#heart").css("color", "grey");
                $("#heart").attr("onclick", "like()");  
            }
        },
        error: function(request, status, error) {
            console.error("AJAX error:", error);  
        }
    });
}


function like() {
    $.ajax({
        type: 'POST',
        url: '/like/{{name}}/',  
        data: { interested: 'Y' },  
        success: function(response) {
            alert(response['msg']);  
            window.location.reload();  
        },
        error: function(request, status, error) {
            console.error("AJAX error:", error);  
        }
    });
}


function unlike() {
    $.ajax({
        type: 'POST',
        url: '/unlike/{{name}}/',  
        data: { interested: 'N' },  
        success: function(response) {
            alert(response['msg']);  
            window.location.reload();  
        },
        error: function(request, status, error) {
            console.error("AJAX error:", error);  
        }
    });
}