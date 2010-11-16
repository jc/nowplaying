var REFRESH_INTERVAL = 6000;

var nowplaying = {
    refreshTimer : null,
    firstFetch : true,
    current : "",
    
    init : function(user) {
        nowplaying.user = user;
        this.fetchNowPlaying();
        this.fetchChart();
        setInterval(this.fetchNowPlaying, REFRESH_INTERVAL);
    },
    
    fetchNowPlaying : function() {
        var data = {};
        data['user'] = nowplaying.user;
        $.ajax({
            url : '/now_playing',
            data : data,
            dataType : 'json',
            method : 'GET',
            success : function(data, textStatus) {
                var artist = "Paused."
                var image = "";
                var track = "";
                var stopped = true;
                var id = "";
                if (data['artist'])
                    id = id + data['artist'];
                if (data['track'])
                    id = id + data['track'];

                if (!nowplaying.firstFetch && nowplaying.current == id)
                    return;
                nowplaying.current = id;
                if (data['stopped'] == false) {
                    artist = "<a href='"+data['artisturl']+"'>"+data['artist']+"</a>";
                    if (data['image'])
                        image = "<img src='"+data['image']+"' />";
                    track = "<a href='"+data['trackurl']+"'>"+data['track']+"</a>";
                    stopped = false;
                }
                
                if (nowplaying.firstFetch) {
                    nowplaying.firstFetch = false;
                }
                
                $('.changeable').fadeOut(function() {
                    $('span#artist').html(artist);
                    $('span#track').html(track);
                    if (image == "") {
                        $('span#image').html("");
                    } else {
                        $('span#image').html(image);
                    }
                    $('.changeable').fadeIn();
                });
            },
            error : function(XMLHttpRequest, textStatus, errorThrown) {
                $('.changeable').fadeOut(function() {
                    $('span#artist').html("Failed to load &mdash; trying again shortly.");
                    $('span#artist').html("");
                    $('span#track').html("");
                    $('span#image').html("");
                    $('.changeable').fadeIn();
                });                

                nowplaying.current = "FAILED"
                setTimeout(nowplaying.fetchNowPlaying, 10000);
            }
        });
    },
    
    fetchChart : function() {
        var data = {};
        data['user'] = nowplaying.user;
        $.ajax({
            url : '/play_chart',
            data : data,
            dataType : 'json',
            method : 'GET',
            success : function(data, textStatus) {
                if (data) {
                    $('img#sparkline').attr("src", data);
                }
                return;
            }
            
        });
        return;
    }
};



