jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function(arg) {
    return function( elem ) {
        return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(function(){
    $('form input[type="submit"]').click(function(e){
        e.preventDefault();
        var input = $(this);
        var data = $(this).parent().serialize();
        var name = $(this).siblings('input').val();
        var ol = $('>ol', $(this).parents('div.practice'))
        if(name != '' && $.inArray(name.toLowerCase(), $.map(ol.find('li'), function(el){return $(el).html().toLowerCase()})) < 0){
            $.ajax($(this).parent().attr('action'), {
                data: data,
                success: function(response){
                    if(response.res){
                        $(input).siblings('input').val('');
                        ol.append('<li>'+response.playername+'</li>');
                        remove_add_draggable();
                    }else{
                        $('<form method="get" action="'+response.formurl+'">'+response.form+'<input type="submit" value="'+$(input).val()+'"/></form>')
                        .submit(function(e){
                            e.preventDefault();
                            var form = $(this);
                            $.ajax($(this).attr('action'), {
                                data: $(this).serialize(),
                                success: function(response){
                                    if(response.res){
                                        ol.append('<li>'+$('input[name="name"]').val()+'</li>');
                                        remove_add_draggable();
                                        $(".ui-dialog-content").remove();
                                    }else{
                                        $.each(response.errors, function(key, val){
                                            $('#id_'+key).parent().addClass('ui-state-error-text')
                                                .effect("pulsate", { times:3 }, 500);
                                        });
                                    }
                                }
                            });
                        })
                        .dialog({
                            title: $(input).val(),
                            modal: true
                        });
                    }
                }
            });
        }else{
            if(name != ''){
                $('>li:Contains("'+name+'")', ol).effect("pulsate", {times: 6}, 750);
            }
        }
        $('input[type="text"]').val('');
    });
    $('ol>li').draggable({revert: true});
    $('div.practice img').droppable({
        drop: function(ev, ui){
            var _id = +ui.draggable.parents('div.practice').attr('id').replace('practice_', '');
            $('<form method="get" action="'+actions[_id].remove+'">'+trans.are_you_sure_delete+'<br />'+
                '<input type="text" name="email" id="email_remove"/>'+
                '<input type="hidden" name="player" value="'+ui.draggable.text()+'" />'+
                '<input type="submit" value="'+trans.del+'" /></form>').dialog({
                    title: trans.del,
                    modal: true
            }).submit(function(e){
                e.preventDefault();
                $.ajax($(this).attr('action'), {
                    data: $(this).serialize(),
                    success: function(response){
                        if(response){
                            $(ui.draggable).remove();
                            $(".ui-dialog-content").remove();
                        }else{
                            $('input#email_remove').parent().addClass('ui-state-error-text')
                                .effect("pulsate", { times:3 }, 500);
                        }
                    }
                });
            });
        }
    });
    $('div.practice div.header a').click(function(e){
        e.preventDefault();
        $.ajax($(this).attr('href'), {
            success: registerScores($(this).attr('href'))
        })
    })
});

var remove_add_draggable = function(){
    $('ol>li').draggable('destroy').draggable({revert: true});
};

var registerScores = function(url){
    return function(data){
        var addPlayers = function(ul, players){
            $.each(players, function(i, p){
                ul.append($('<li>').text(p));
            })
        };
        var getInput = function(name){
            return $('<input name="'+name+'" type="text" />').change(function(e){
               var val = +$(this).val();
               if(isNaN(val)){
                   $(this).val('0');
               }
            }).css({width: '50%', textAlign: 'center'}).val('0');
        }
        var main = $('<div>');
        var home = $('<ul id="hometeam">').addClass('team').addClass('ui-corner-all');
        addPlayers(home, data.home);
        var away = $('<ul id="awayteam">').addClass('team').addClass('ui-corner-all');
        addPlayers(away, data.away);
        var button = $('<button>').text(trans.save).click(function(e){
            var data = {}
            data['hometeam'] = $.makeArray($('ul#hometeam li').map(function(i, el){return $(el).text()}));
            data['awayteam'] = $.makeArray($('ul#awayteam li').map(function(i, el){return $(el).text()}));
            data['homescore'] = $('div > input[name="homescore"]').val();
            data['awayscore'] = $('div > input[name="awayscore"]').val();
            $.ajax(url, {
                type: 'POST',
                data: data,
                success: function(response){
                    asdf=response;
                    if(response.res){
                        $(".ui-dialog-content").remove();
                    }else{
                        alert('Error wat?');
                    }
                }
            })
        }).css({float: 'right'}).button();
        var scores = $('<div>').append(getInput('homescore')).append(getInput('awayscore'))
            .css({width: '100%'});
        main.append(scores).append(home).append(away).append(button).dialog({
            modal: true,
            title: trans.register_scores,
            width: '500px',
        });
        $('ul.team').droppable({
            drop: function(ev, ui){
                $(this).append(ui.draggable);
            }
        });
        $('ul.team li').draggable({revert: true});
    }
};


