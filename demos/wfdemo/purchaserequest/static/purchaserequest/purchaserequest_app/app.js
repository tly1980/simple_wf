( function(app, $) {

    function elem_appdlg(selector){
        if (selector === undefined ){
            return app.modal_app_dlg();
        }
        return app.modal_app_dlg().find(selector);
    }

    function elem(selector){
        if ( selector === undefined ){
            return app.the_win.jq_win();
        }
        return app.the_win.jq_win().find(selector);
    }

    function tpl(tpl_name){
        return app.app_data().tpl[tpl_name];
    }

    function bb_refresh_list(){
        var PurchaseRequestCollection = Backbone.Collection.extend({
            url: function(){
                var ret = '/purchaserequest/?filter=' + elem('select[name=req_filter]').val();
                return ret;
            }

        });

        var prlist = new PurchaseRequestCollection();

        prlist.fetch({
            success:function(){
                var the_html = Mustache.to_html(
                    tpl('req_table'), {'pr_lst' : prlist.toJSON()} );
                elem('.req_browser').html(the_html);
            }
        });
    }

    function submit_wf(pr_id, wf_action, conditions){
        var comments = $('textarea[name=comments]').val();
        var the_params = {
            action: wf_action,
            comments: comments,
            conditions: JSON.stringify(null)
        };

        if ( conditions !== undefined ){
            the_params['conditions'] = JSON.stringify(conditions);
        }

        console.log('the_params', the_params);

        $.ajax({
            url: '/purchaserequest/' + pr_id + '/wf/',
            type: 'PUT',
            data: the_params,
            success: function(){
                console.log('success!');
                app.modal_app_dlg().dialog('close');
                bb_prequest_wf(pr_id);
            }
        });

    }

    function bb_prequest_log(pr_id){
        $.ajax({
            url: '/purchaserequest/' + pr_id + '/log/',
            type: 'GET'
        }).done(function(data){
            var the_html = Mustache.to_html(
                tpl('log'), {logs: data}
            );

            elem('tbody.log_table').html(the_html);
        });
    }

    function bb_prequest_wf(pr_id, can_edit){
        bb_prequest_log(pr_id);
        if ( can_edit === undefined ){
            can_edit = false;
        }
        var PurchaseRequest = Backbone.Model.extend({
            url: function(){
                return '/purchaserequest/' + pr_id;
            }
        });

        prequest = new PurchaseRequest();

        var PurchaseRequestView = Backbone.View.extend({
            className: 'pr_view',
            tagName: 'div',
            events: {
                'click button[wf_action]': 'wf_action',
                'click button.edit_pr': 'edit_pr'
            },

            initialize: function(){
               prequest.on('change', this.load, this);
            },

            edit_pr: function(evt){
                bb_prequest_edit(pr_id);
            },

            wf_action: function(evt){

                var $btn =  $(evt.currentTarget);
                var wf_action = $btn.attr('wf_action');
                
                if (wf_action !== 'admin_check' && wf_action != 'manager_check'){
                    app.modal_app_dlg({
                        title: 'Action: ' + $btn.text(),
                        the_html: tpl('wf_dlg'),
                        width: 390,
                        height: 280,
                        buttons: {
                            'Submit': function(){
                                submit_wf(pr_id,
                                    wf_action
                                );
                                
                            },

                            'Cancel': function(){
                                app.modal_app_dlg().empty();
                                $(this).dialog('close');
                            }
                        }
                    });
                }else{
                    app.modal_app_dlg({
                        title: 'Action: ' + $btn.text(),
                        the_html: tpl('wf_dlg'),
                        width: 390,
                        height: 280,
                        buttons: {
                            'Approve': function(){
                                submit_wf(pr_id,
                                    wf_action,
                                    {'approve': true}
                                );
                                
                            },

                            'Disapprove': function(){
                                submit_wf(pr_id,
                                    wf_action,
                                    {'approve': false}
                                );
                                
                            },


                            'Cancel': function(){
                                app.modal_app_dlg().empty();
                                $(this).dialog('close');
                            }
                        }
                    });

                }
            },

            render: function(){
                return this;
            },

            load: function(){
                var pre_req = prequest.toJSON();

                this.$el.html(
                    Mustache.to_html(
                        tpl('req_editor'),
                        pre_req
                    )
                );


                if (pre_req.can_edit === true){
                    this.$('li.edit_pr').show();
                }else{
                    this.$('li.edit_pr').hide();
                }

                this.$('div.wf_op').html(
                    Mustache.to_html(
                        '{{#todos}}<button wf_action={{action}}>{{action_text}}</button>{{/todos}}',
                        pre_req
                    )
                );

                this.$('button').button();
            }

        });

        var pr_view = new PurchaseRequestView();
        pr_view.render();
        prequest.fetch();
        
        elem('.req_view').empty().append(pr_view.$el);
        switch_prview(true);

    }

    function switch_prview(show_pr){
        if (show_pr === true ){
            elem('.req_browser').hide();
            elem('.req_filter_wrap').hide();
            elem('.req_dtview').show();
            elem('.req_logview').show();
            elem('.back_to_filter').show();
            
            
        }else{
            elem('.req_browser').show();
            elem('.req_filter_wrap').show();
            elem('.back_to_filter').hide();
            elem('.req_dtview').hide();
            elem('.req_logview').hide();
        }
    }

    function bb_prequest_edit(pr_id){
        var PurchaseRequest = Backbone.Model.extend({
            urlRoot: '/purchaserequest'
        });

        var prequest =  new PurchaseRequest({
            id: pr_id
        });

        prequest.set('id', pr_id);

        var PurchaseRequestView = Backbone.View.extend({
            className: 'pr_view',
            tagName: 'div',
            events: {
                'click button.save_pr': 'save_pr'
            },

            save_pr: function(){
                prequest.save({
                    product_name: this.$('input[name=product_name]').val(),
                    product_url: this.$('input[name=product_url]').val(),
                    amount: this.$('input[name=amount]').val()
                }, {wait: true,
                    success: function(){
                        bb_prequest_wf(pr_id);
                        app.modal_app_dlg().dialog('close');
                        bb_refresh_list();
                    }
                });
                
            },

            initialize: function(){
                prequest.on('change', this.load, this);
            },

            load: function(){
                //console.log('save!', prequest.get('id'));
                this.$('input[name=product_name]').val( prequest.get('product_name'));
                this.$('input[name=product_url]').val( prequest.get('product_url'));
                this.$('input[name=amount]').val( prequest.get('amount'));
            },

            render: function(){
                this.$el.html(
                    tpl('req_new')
                );
                return this;
            }
        });

        var pr_view = new PurchaseRequestView();
        pr_view.render();
        prequest.fetch();
        app.modal_app_dlg({
            title: 'Purchase Request',
            width: 480,
            height: 280,
            the_el: pr_view.$el,
            buttons: {
                'Save': function(){
                    pr_view.save_pr();
                },

                'Cancel': function(){
                    app.modal_app_dlg().empty();
                    $(this).dialog('close');
                }
            }
        });


    }

    function bb_prequest_new(){
        var PurchaseRequest = Backbone.Model.extend({
            url: function(){
                return '/purchaserequest/';
            }
        });

        var prequest = null;
 

        prequest = new PurchaseRequest();


        var PurchaseRequestView = Backbone.View.extend({
            className: 'pr_view',
            tagName: 'div',
            events: {
                'click button.save_pr': 'save_pr'
            },

            save_pr: function(){
                
                prequest.save({
                    product_name: this.$('input[name=product_name]').val(),
                    product_url: this.$('input[name=product_url]').val(),
                    amount: this.$('input[name=amount]').val()
                }, {wait: true});
                
            },

            initialize: function(){
                prequest.on('change', this.load, this);
            },

            load: function(){
                //console.log('save!', prequest.get('id'));
                var pr_id = prequest.get('id');
                bb_prequest_wf(pr_id);
                app.modal_app_dlg().dialog('close');
                bb_refresh_list();

            },

            render: function(){
                this.$el.html(
                    tpl('req_new')
                );
                //console.log('$el', this.$el);
                //console.log('reg_edit', tpl('req_editor'));
                return this;
            }
        });

        var pr_view = new PurchaseRequestView();
        pr_view.render();

        app.modal_app_dlg({
            title: 'Purchase Request',
            width: 480,
            height: 280,
            the_el: pr_view.$el,
            buttons: {
                'Save': function(){
                    pr_view.save_pr();
                },

                'Cancel': function(){
                    app.modal_app_dlg().empty();
                    $(this).dialog('close');
                }
            }
        });
    }

    function window_created(){
        console.log('window_created');
        elem().on('click', 'a[href="#pr/create"]',
            function(evt){
                bb_prequest_new();
            }
        );

        elem().on('change', 'select[name=req_filter]',
            function(evt){
                bb_refresh_list();
            }
        );

        elem().on('dblclick', 'tr[pr_id]',
            function(evt){
                var pr_id = $(evt.currentTarget).attr('pr_id');
                bb_prequest_wf(pr_id);
            }
        );

        elem().on('click', 'a.back_to_filter',
            function(evt){
                switch_prview(false);
            }
        );

        $('body').on('click', 'a.open_pr',
            function(evt){
                bb_prequest_wf($(evt.currentTarget).attr('pr_id'));
            }
        );


        bb_refresh_list();
        web_listen();
    }

    function web_listen(){
        var ws = new WebSocket("ws://localhost:8888/listen");
        ws.onopen = function() {
            console.log('openned');
        };
        ws.onmessage = function (evt) {
            console.log('coming', evt.data);
            var msg = JSON.parse(evt.data);
            console.log('coming', evt.data);

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'Request Process ' + msg.pr_id + ' updated by ' +  msg.operator,
                // (string | mandatory) the text inside the notification
                text: '<a class="open_pr" href="#" pr_id="' + msg.pr_id +'" >Click here to view or edit</a>'
            });

        };
    }

    //initialization starts from here   
    //console.log('rewrite app.win_html');
    app.win_html = function(){
        //console.log('app.app_data().tpl.win_content:', app.app_data().tpl.win_content);
        return {
            win_content: app.app_data().tpl.win_content,
            win_bottom: app.app_data().tpl.win_bottom
        };
    };

    app.window_created = window_created;

})(app, jQuery);