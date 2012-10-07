var APP_PORTAL = null;
(function( $ ){
    var _app_portal ;
    
    var RESOURCE_DEFAULT = {
        app_name: 'noname app',
        icon: '/static/merchant/assets/images/icons/icon_32_computer.png',
        icon_small: '/static/merchant/assets/images/icons/icon_22_computer.png',
        tpl: {}
    };

    var RUNTIME = {
        app_registry : {},
        win_counter : 0,
        lst_app : [],
        lst_win : [],
        $desktop : $('#desktop'),
        $dock : $('#dock')
    };

    function http_get(url){
        var xhr = $.ajax({
            url: url,
            async: false,
            dataType: 'json'
        });

        if (xhr.statusText === 'OK')
            return xhr.responseText;

        throw {
            exception: 'HttpGetError',
            msg: 'Failed to get content of url:' + url
        };
    }

    function touch_url(base_url, url){
        //console.log('base_url', base_url, 'url', url);
        if (url === undefined ){
            return base_url;
        }
        
        if (url.indexOf('/') === 0 ){
            return url;
        }
        url = base_url + '/' + url;
        return url;
    }

    function get_json(json_url){
        //console.log('json_url', json_url);
        var data = http_get(json_url);
        return JSON.parse(data);
    }

    function maskedEval(src, app){
        // set up an object to serve as the context for the code
        // being evaluated.
        var mask = {};
        // mask global properties
        for (var p in this){
            mask[p] = undefined;
        }

        mask.app = app;
        mask['jQuery'] = $;
        mask['console']= console;
        mask['Mustache'] = Mustache;
        mask['JSON'] = JSON;
        mask['AJLoader'] = AJLoader;
        mask['Backbone'] = Backbone;
        mask['_'] = _;
        mask['WebSocket'] = WebSocket;
        // execute script in private context
        (new Function( "with(this) { " + src + " }")).call(mask);
    }

    function guid() {
       function S4() {
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        }
       return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    }

    function create_window(win_params, app_id){
        RUNTIME.win_counter ++;
        var window_params = $.extend(true, {}, RESOURCE_DEFAULT.win_params, win_params);
        window_params['win_id'] = 'win.' + RUNTIME.win_counter;
        window_params['app_id'] = app_id;
        var window = {
            app_id: function(){
                return app_id;
            },

            win_id: function (){
                return window_params.win_id;
            },

            start: function (){
                var html_win = Mustache.to_html( RESOURCE_DEFAULT.tpl.win, window_params);
                //console.log('html_win', html_win, window_params);
                var html_dock = Mustache.to_html( RESOURCE_DEFAULT.tpl.dock, window_params);
                var $win = $(html_win);
                var $dock_btn = $(html_dock);

                $( '.window_content', $win).append(window_params.win_html.win_content);
                $( '.window_bottom', $win).append(window_params.win_html.win_bottom);
                $win.appendTo(RUNTIME.$desktop);
                $dock_btn.appendTo(RUNTIME.$dock);

                window_params.jq_win = $win;
                window_params.jq_dock =  $dock_btn;

                this.debut();
            },

            debut: function(){
                var step = 10;
                var x, y = 0;
                x = y = step * RUNTIME.win_counter;
                x = x % $('#desktop').width();

                if (x < 100){
                    x = x + 100;
                }

                y = y % ($('#desktop').height() - $('#bar_bottom').height()) + $('#bar_top').height() + 5;
                var offset = {left:  x, top: y };
                //console.log('offset', offset);
                window_params.jq_win.offset(offset);
                //console.log('after offset', window_params.jq_win.offset());
                this.top_most(offset);
            },

            top_most: function (offset){
                JQD.util.window_flat();
                window_params.jq_win.addClass('window_stack').show();
                //console.log('after2 offset', window_params.jq_win.offset());

                if (offset !== undefined ){
                    window_params.jq_win.offset(offset);
                }
            },

            max_win: function(){
                //console.log('window_params.jq_win', window_params.jq_win);
                JQD.util.window_resize(window_params.jq_win);
            },


            // reg_event: function(is_reg){
            //     if (is_reg === undefined){
            //         is_reg = true;
            //     }

            //     var evt_lst = .event_list();

            //     for (var i=0; i<evt_lst.length; ++i){
            //         var evt = evt_lst[i];
            //         if (is_reg){
            //             this._jq_win.delegate(evt.selector, evt.events, evt.handler);
            //         }else{
            //             this._jq_win.undelegate(evt.selector, evt.events, evt.handler);
            //         }
            //     }
            // },

            shut_down: function(){
                // this.reg_event(false);
                window_params.jq_dock.remove();
                window_params.jq_win.remove();
                RUNTIME.lst_win = _.without(RUNTIME.lst_win, this );
            },

            jq_win: function(){
                return window_params.jq_win;
            },
        };

        return window;
    }

    function _create_app( app_data ){

        if (app_data.app_id === undefined ){
            app_data.app_id = guid();
        }

        if ( RUNTIME.app_registry[app_data.app_id] !== undefined ){
            alert('app cannot be registered with app_id ', app_data.app_id );
            throw {
                'exception': 'AppIdAlreadyRegistered',
                'msg': 'app cannot be registered with app_id:' + app_data.app_id
            };
        }

        var app = {
            app_data: function(){
                return app_data;
            },

            app_id: function(){
                return app_data.app_id;
            },

            win_html: function(){
                throw "Please overite this in app!";
            },

            win_params: function(){
                ret = app_data.win_params;
                ret = $.extend( true, {}, RESOURCE_DEFAULT.win_params, ret);
                ret['win_html'] = this.win_html();
                //console.log('win_params', ret);
                return ret;
            },

            name: function( name ){
                if (name !== undefined ){
                    app_data.name = name;
                }
                return app_data.name;
            },

            singleton: function(){
                console.log('app_data', app_data);
                return app_data.singleton;
            },

            start: function(){
                //console.log('starting...');
                if( this.singleton() === true ){
                    //console.log('singleton ...');
                    this._start_single();
                }else{
                    //console.log('not singleton ...');
                    this._start();
                }
            },

            _existing_win: function(){
                var the_win = null;
                for (var i = 0; i < RUNTIME.lst_win.length; ++i ){
                    if ( RUNTIME.lst_win[i].app_id() === this.app_id() ){
                        the_win = RUNTIME.lst_win[i];
                    }
                }
                return the_win;
            },

            _start_single: function(){
                var existing_win = this._existing_win();
                console.log('existing_win', existing_win);
                if (existing_win !== null ){
                    existing_win.top_most();
                    return;
                }

                this._start();
            },

            _start: function(){
                var the_win = create_window(
                        this.win_params(),
                        this.app_id()
                    );
                the_win.start();
                if (this.win_params().max_win_at_starting === true ){
                    the_win.max_win();
                }
                
                this.main_win(the_win);

                //console.log('a');
                if (this.window_created !== undefined ){
                    //console.log('b');
                    this.window_created();
                }

                RUNTIME.lst_win.push(the_win);
            }, 

            main_win: function( the_win ){
                if ( the_win !== undefined ){
                    this.the_win = the_win;
                }

                return the_win;
            },

            modal_app_dlg: function(params){
                if (params !== undefined ){
                    var the_params = $.extend( {}, {
                        resizable: false,
                        height:140,
                        modal: true,
                        closeOnEscape: false,
                        close: function(evt, ui){
                            //console.log('dlg closed');
                            $(this).empty();
                        }
                    }, params);

                    if ( params.the_html !== undefined ){
                        $('#dialog-app').html(params.the_html);
                    }else {
                        $('#dialog-app').empty();
                        $('#dialog-app').append(params.the_el);
                    }
                    
                    $('#dialog-app').dialog(the_params);
                    $('#dialog-app').attr('app_id', this.app_id());
                }

                return $('#dialog-app');
            },

            modal_app_dlg2: function(params){
                if (params !== undefined ){
                    var the_params = $.extend( {}, {
                        resizable: false,
                        height:140,
                        modal: true,
                        closeOnEscape: false,
                        close: function(evt, ui){
                            //console.log('dlg2 closed');
                            $(this).empty();
                        }

                    }, params);

                    $('#dialog-app2').html(params.the_html);
                    $('#dialog-app2').dialog(the_params);
                    $('#dialog-app2').attr('app_id', this.app_id());
                }

                return $('#dialog-app2');
            },


            modal_confirm_dlg: function(params){
                if (params !== undefined ){
                    var the_params = $.extend( {}, {
                        resizable: false,
                        height:140,
                        modal: true
                    }, params);
                    $('#dialog-confirm .confirm_msg').text(params.confirm_msg);
                    $('#dialog-confirm').dialog(the_params);
                }
                return $('#dialog-confirm');
            }


            // reg_event: function(events, selector, handler ){
            //     this._evt_list.push({
            //         events: events,
            //         selector: selector,
            //         handler: handler
            //     });
            // },

            // event_list: function(){
            //     return this._evt_list;
            // },
        };

        return app;
    }

    _app_portal = {
        evt_queue: [],
        resource: function(res_url){
            if( res_url !== undefined ){
                var res_data = get_json(res_url);

                var arry_names = res_url.split('/');
                arry_names.pop();
                var base_url = arry_names.join('/');

                res_data.app_icon = touch_url(base_url, res_data.app_icon);
                res_data.app_icon_small = touch_url(base_url, res_data.app_icon_small);

                for (var i=0; i<res_data.tpl_url.length; ++i){
                    res_data.tpl_url[i] = touch_url( base_url, res_data.tpl_url[i]);
                }

                if (res_data.tpl_url !== undefined ){
                    var tpl_dict = $.tload.apply(null, res_data.tpl_url);
                    res_data.tpl = $.extend(true, {}, res_data.tpl, tpl_dict.tpl);
                }
                //console.log('res_data', res_data);
                
                RESOURCE_DEFAULT = $.extend(true, {}, RESOURCE_DEFAULT, res_data);
            }
            return RESOURCE_DEFAULT;
        },

        app_resource: function(app_url){
            var arry_names = app_url.split('/');
            arry_names.pop();
            var base_url = arry_names.join('/');
            var data = get_json(app_url);

            data.js_src = http_get(base_url + '/' + data.js_url);
            
            for (var i=0; i< data.tpl_url.length; i++){
                data.tpl_url[i] = base_url + '/' + data.tpl_url[i];
            }
            
            var tpl_dict = $.tload.apply(null, data.tpl_url);
            if (data.tpl === undefined){
                data.tpl = {};
            }

            data.tpl = $.extend({}, data.tpl, tpl_dict.tpl);
            console.log('data', data, 'RESOURCE_DEFAULT', RESOURCE_DEFAULT);
            var ret = $.extend(true, {}, RESOURCE_DEFAULT, data);
            return ret;
        },

        install: function (){
            var lst_app_url = this.install.arguments;

            for (var i = 0; i < lst_app_url.length; i++ ){
                var app_url = lst_app_url[i];
                var app_data = this.app_resource(app_url);
                var app = _create_app(app_data);
                maskedEval(app_data.js_src, app);
                RUNTIME.lst_app.push(app);
            }

            this.refresh_desktop();
            var that = this;
            setTimeout(function(){
                that.check_evt_queue();
            }, 500);
            
        },

        check_evt_queue: function(){
            
            var task = this.evt_queue.pop();
            if (task !== undefined ){
                console.log('executing task', task);
                var app =this.start_app_instance(task.app_id);
                app[task.action].apply(app, task.params);
            }
        },

        refresh_desktop: function (){
            var top = 20;
            var left = 20;
            RUNTIME.$desktop.empty();

            for ( var i = 0; i < RUNTIME.lst_app.length; i++ ){
                var app = RUNTIME.lst_app[i];
                
                var params = {top: top,
                     left: left,
                     icon: app.app_data().icon,
                     app_name : app.name,
                     app_id: app.app_data().app_id
                    };
                var html = Mustache.to_html(RESOURCE_DEFAULT.tpl.icon,
                    params
                );

                //console.log('params', params);
                $icon = $(html).appendTo(RUNTIME.$desktop);


                $icon.css({top:top, left:left});
                top = top + 80;
            }
        },


        start_app_instance: function(app_id){
            var the_app = null;
            //console.log('app_id', app_id);
            for (var i = 0; i < RUNTIME.lst_app.length; i++){

                if ( RUNTIME.lst_app[i].app_id() === app_id ){
                    the_app = RUNTIME.lst_app[i];
                }
            }

            if (the_app !== null ){
                the_app.start();
            }

            return the_app;
        },

        shutdown_app_instance: function(win_id){
            //console.log('shutdown_app_instance', win_id);
            var the_win = null;
            //console.log('RUNTIME.lst_win[0]', RUNTIME.lst_win[0].win_id());
            for (var i = 0; i < RUNTIME.lst_win.length; ++i ){

                if ( RUNTIME.lst_win[i].win_id() === win_id ){
                    the_win = RUNTIME.lst_win[i];
                }
            }
            
            if (the_win !== null ){
                the_win.shut_down();
            }
        }
    };
    APP_PORTAL = _app_portal;
})( jQuery );

