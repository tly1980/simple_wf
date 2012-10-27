(function($){

    function _do_strip(tpl_content){
        var p_useless_nstart = /\n[\t ]*/g;
        var p_useless_nend = /[\t ]*\n/g;
        var p_useless_space =  />[\t ]+</g;

        return tpl_content.replace(new RegExp(p_useless_nstart), '\n').
            replace(new RegExp(p_useless_nend), '\n').
            replace( new RegExp(p_useless_space), '><');
    }


    function tpl_filename(url){
        var pathname = $('<a>').attr('href', url)[0].pathname;
        var fname = pathname.split('/').pop();
        return fname.split('.')[0];
    }


    function load(){
        var tpl = { };
        var good_url = [];
        var bad_url = [];
        
        for (var i = 0; i < arguments.length; i++){
            var url = arguments[i];
            tpl_name = tpl_filename(url);
            var xhr = $.ajax({
                url: url,
                async: false
              });

            if (xhr.statusText === 'OK'){
                var tmp_dict = {};
                if(tpl [tpl_name] !== undefined ){
                    console.log('duplicated tpl name', tpl_name);
                }
                tpl [tpl_name] = xhr.responseText;
                good_url.push(url);
            }else{
                bad_url.push(url);
            }
        }

        return {
            tpl: tpl,
            good_url: good_url,
            bad_url: bad_url
        };
    }

    $['tload'] = load;
    

})(jQuery);

